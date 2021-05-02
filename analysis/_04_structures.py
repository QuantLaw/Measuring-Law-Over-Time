import os

import networkx as nx
import numpy as np
import pandas as pd

from analysis.statics import YEARS
from analysis.utils import (get_basic_parser, get_crossreference_path,
                            get_node_and_edge_files)
from tabulate import tabulate


def get_networkx_graph_components(basepath, nodefile, edgefile):
    nodes_to_skip = (
        pd.read_csv(f"{basepath}/{nodefile}", low_memory=True, usecols=["type"])
        .query("type != 'seqitem'")
        .index.values
        + 1
    )
    nodes = pd.read_csv(
        f"{basepath}/{nodefile}",
        skiprows=nodes_to_skip,
        low_memory=True,
        usecols=["key", "law_name", "heading", "document_type"],
    ).set_index("key")
    edges = pd.read_csv(f"{basepath}/{edgefile}").query(
        "edge_type == 'reference' and u in @nodes.index and v in @nodes.index"
    )
    G = nx.MultiDiGraph()
    G.add_nodes_from(nodes.index)
    G.add_edges_from([(u, v) for u, v in zip(edges.u, edges.v)])
    assert len(edges) == G.number_of_edges()
    assert len(nodes) == G.number_of_nodes()
    return (nodes, edges, G)


def create_ego_star(n, G_simple):
    ego_network = nx.ego_graph(G_simple, n)
    too_connected_spokes = get_too_connected_spokes(ego_network, n)
    while too_connected_spokes:
        ego_network.remove_node(too_connected_spokes[0][0])
        too_connected_spokes = get_too_connected_spokes(ego_network, n)
    return ego_network


def get_too_connected_spokes(ego_network, n):
    return sorted(
        [
            (k, v)
            for k, v in dict(ego_network.degree()).items()
            if (v - 1) > 0.01 * (len(ego_network) - 1) and k != n
        ],
        key=lambda tup: tup[-1],
        reverse=True,
    )


def determine_star_type(out_degree, in_degree):
    if in_degree / max(out_degree, np.finfo(float).eps) >= 10:
        startype = "Sink"
    elif out_degree / max(in_degree, np.finfo(float).eps) >= 10:
        startype = "Source"
    else:
        startype = "Hinge"
    return startype


def make_star_df(ego_stars, nodes):
    df = pd.DataFrame(
        columns=[
            "n",
            "m_s",
            "out_degree",
            "in_degree",
            "type",
            "hub",
            "description",
            "key",
        ]
    )
    for idx, (hub, star) in enumerate(ego_stars[:100]):
        star_subgraph = nx.subgraph(G_digraph, star.nodes())
        out_degree = star_subgraph.out_degree(hub)
        in_degree = star_subgraph.in_degree(hub)
        df.loc[idx] = [
            star_subgraph.number_of_nodes(),
            star_subgraph.number_of_edges() - star_subgraph.number_of_nodes() + 1,
            out_degree,
            in_degree,
            determine_star_type(out_degree, in_degree),
            f"{nodes.loc[hub].heading} {nodes.loc[hub].law_name}",
            "",
            hub,
        ]
    return df


def get_ego_stars(G, G_simple):
    potential_hubs = sorted(
        [n for n in G.nodes() if G_simple.degree(n) >= 9],
        key=lambda n: G_simple.degree(n),
        reverse=True,
    )
    ego_stars = []
    for n in potential_hubs:
        ego_star = create_ego_star(n, G_simple)
        if len(ego_star) >= 10:
            ego_stars.append((n, ego_star))
    ego_stars.sort(key=lambda tup: (len(tup[-1])), reverse=True)
    return ego_stars


def save_star_df(df, nodes, country):
    df.merge(nodes[["document_type"]], on="key").to_csv(
        f"../results/stars-{country}-{year}.csv", index=False
    )


def make_star_description_df(df):
    sdf = pd.concat(
        [
            df.query('type == "Sink"')[:5],
            df.query('type == "Hinge"')[:5],
            df.query('type == "Source"')[:5],
        ],
        ignore_index=True,
    )
    sdf.hub = sdf.hub.str.replace("\u2009", " ")
    return sdf


def write_star_description_table(sdf):
    with open(f"../graphics/star-descriptions-{country}-{year}.tex", "w") as f:
        f.write(
            tabulate(
                sdf.drop("key", axis=1),
                tablefmt="latex_raw",
                headers=[
                    "$n$",
                    "$m_S$",
                    r"$\delta^+$",
                    r"$\delta^-$",
                    r"\textbf{Type}",
                    r"\textbf{Hub}",
                    r"\textbf{Description}",
                ],
                showindex=False,
            )
        )


def write_individual_stars(ego_stars, sdf, country):
    result_path = "../results/star-contents"
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    for key, ego_star in ego_stars:
        if key in sdf.key.values:
            nodes.loc[[key, *[x for x in ego_star.nodes() if x != key]]].to_csv(
                f"{result_path}/{country}-star-{key}.csv"
            )


if __name__ == "__main__":
    parser = get_basic_parser()
    args = parser.parse_args()
    country = args.country

    crossreference_path = get_crossreference_path(country)
    nodefiles, edgefiles = get_node_and_edge_files(crossreference_path, YEARS)
    for year in [YEARS[0], YEARS[-1]]:
        nodes, edges, G = get_networkx_graph_components(
            crossreference_path,
            nodefiles[YEARS.index(year)],
            edgefiles[YEARS.index(year)],
        )
        G_simple = nx.Graph(G)
        G_digraph = nx.DiGraph(G)

        ego_stars = get_ego_stars(G, G_simple)
        df = make_star_df(ego_stars, nodes)

        save_star_df(df, nodes, country)

        sdf = make_star_description_df(df)
        write_star_description_table(sdf)

        write_individual_stars(ego_stars, sdf, country)
