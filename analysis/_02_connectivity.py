import networkx as nx
import pandas as pd

from analysis.statics import YEARS
from analysis.utils import (get_basic_parser, get_country,
                            get_crossreference_path, get_node_and_edge_files)


def get_networkx_graph_components(basepath, nodefile, edgefile):
    nodes_to_skip = (
        pd.read_csv(f"{basepath}/{nodefile}", low_memory=True, usecols=["type"])
        .query("type != 'seqitem'")
        .index.values
        + 1  # need to increase index by one because 0 is the header
    )
    nodes = pd.read_csv(
        f"{basepath}/{nodefile}", low_memory=True, skiprows=nodes_to_skip
    ).set_index("key")
    edges_to_skip = (
        pd.read_csv(f"{basepath}/{edgefile}", low_memory=True, usecols=["edge_type"])
        .query("edge_type != 'reference'")
        .index.values
        + 1
    )
    edges = pd.read_csv(
        f"{basepath}/{edgefile}", low_memory=True, skiprows=edges_to_skip
    )
    edges = edges.join(nodes[["document_type"]], on="u").rename(
        dict(document_type="u_document_type"), axis=1
    )
    edges = edges.join(nodes[["document_type"]], on="v").rename(
        dict(document_type="v_document_type"), axis=1
    )
    G = nx.MultiDiGraph()
    G.add_nodes_from(nodes.index)
    G.add_edges_from(
        [
            (u, v, dict(edge_type=edge_type))
            for u, v, edge_type in zip(edges.u, edges.v, edges.edge_type)
        ]
    )
    assert len(edges) == G.number_of_edges()
    assert len(nodes) == G.number_of_nodes()
    return (nodes, edges, G)


def create_connectivity_dataframe(
    crossreference_path, years, statutes: bool, regulations: bool
):
    nodefiles, edgefiles = get_node_and_edge_files(crossreference_path, years)
    columns = [
        "number_of_nontrivial_ccs",
        "number_of_seqitems",
        "number_of_edges",
        "number_of_isolates",
        "number_of_nodes_in_lcc",
        "number_of_edges_in_lcc",
    ]
    df = pd.DataFrame(columns=columns)
    lccs = []
    for nf, ef in zip(nodefiles, edgefiles):
        year = int(nf.split("/")[-1][:4])
        print(f"Computing statistics for year {year}", end="\r")
        nodes, edges, G = get_networkx_graph_components(crossreference_path, nf, ef)
        if statutes and not regulations:
            G.remove_nodes_from(nodes.query("document_type != 'statute'").index)
        elif regulations and not statutes:
            G.remove_nodes_from(nodes.query("document_type != 'regulation'").index)
        G.remove_nodes_from(list(nx.isolates(G)))
        connected_components = []
        for cc in nx.weakly_connected_components(G):
            connected_components.append(G.subgraph(cc))
        connected_components.sort(
            key=lambda cc: (cc.number_of_nodes(), cc.number_of_edges()), reverse=True
        )
        number_of_nontrivial_ccs = len(connected_components)
        number_of_seqitems = len(nodes)
        number_of_isolates = number_of_seqitems - G.number_of_nodes()
        number_of_edges = G.number_of_edges()
        lccs.append(connected_components[0])
        row = [
            number_of_nontrivial_ccs,
            number_of_seqitems,
            number_of_edges,
            number_of_isolates,
            connected_components[0].number_of_nodes(),
            connected_components[0].number_of_edges(),
        ]
        df.loc[
            year
        ] = row  # df = df.append(pd.DataFrame.from_records([row], columns=columns, index=[year]))
    df["percent_nodes_in_lcc"] = df.number_of_nodes_in_lcc / df.number_of_seqitems
    df["percent_edges_in_lcc"] = df.number_of_edges_in_lcc / df.number_of_edges
    df["percent_isolates"] = df.number_of_isolates / df.number_of_seqitems
    df["percent_nodes_in_satellites"] = (
        1 - df.percent_nodes_in_lcc - df.percent_isolates
    )

    scc_sizes = []
    in_component_sizes = []
    out_component_sizes = []
    rest_sizes = []
    print("Starting to evaluate GCCs...")
    for G in lccs:
        # largest_scc is a list of nodes in the largest SCC of G
        largest_scc = sorted(max(nx.strongly_connected_components(G), key=len))
        reachable_from_largest_scc = nx.descendants(G, largest_scc[0]) | {
            largest_scc[0]
        }
        reaching_to_largest_scc = nx.descendants(G.reverse(), largest_scc[0]) | {
            largest_scc[0]
        }
        scc_size = len(set(largest_scc))
        scc_sizes.append(scc_size)
        in_component_size = len(reaching_to_largest_scc - set(largest_scc))
        in_component_sizes.append(in_component_size)
        out_component_size = len(reachable_from_largest_scc - set(largest_scc))
        out_component_sizes.append(out_component_size)
        rest_size = len(
            set(G.nodes()) - (reaching_to_largest_scc | reachable_from_largest_scc)
        )
        rest_sizes.append(rest_size)

    df["scc_size"] = scc_sizes
    df["in_component_size"] = in_component_sizes
    df["out_component_size"] = out_component_sizes
    df["rest_size"] = rest_sizes
    df["fraction_scc_in_lcc"] = df.scc_size / df.number_of_nodes_in_lcc
    df["fraction_in_in_lcc"] = df.in_component_size / df.number_of_nodes_in_lcc
    df["fraction_out_in_lcc"] = df.out_component_size / df.number_of_nodes_in_lcc
    df["fraction_rest_in_lcc"] = df.rest_size / df.number_of_nodes_in_lcc
    return df


if __name__ == "__main__":
    parser = get_basic_parser()
    args = parser.parse_args()
    country = get_country(args)
    crossreference_path = get_crossreference_path(country)

    combinations = [(True, True), (True, False), (False, True)]
    for (statutes, regulations) in combinations:
        print(
            f"Starting combination with statutes={statutes} and regulations={regulations}..."
        )
        df = create_connectivity_dataframe(
            crossreference_path, YEARS, statutes, regulations
        )
        if statutes and not regulations:
            df.to_pickle(
                f"../results/connectivity-data-statutes-only-{country}.gpickle.gz"
            )
        elif regulations and not statutes:
            df.to_pickle(
                f"../results/connectivity-data-regulations-only-{country}.gpickle.gz"
            )
        else:
            df.to_pickle(f"../results/connectivity-data-{country}.gpickle.gz")
