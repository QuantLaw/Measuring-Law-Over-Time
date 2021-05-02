import os
from copy import deepcopy
from multiprocessing import Pool, cpu_count

import networkx as nx
import pandas as pd

from analysis.statics import YEARS
from analysis.utils import (get_basic_parser, get_country,
                            get_crossreference_path, get_node_and_edge_files,
                            get_preprocessed_graph_files,
                            get_preprocessed_graph_path)


def get_networkx_graph_components(basepath, nodefile, edgefile):
    cols = ["level", "type", "document_type", "heading", "law_name", "tokens_n", "key"]
    dtypes = dict(
        level=int,
        type=str,
        document_type=str,
        heading=str,
        law_name=str,
        tokens_n=int,
        key=str,
    )
    nodes = pd.read_csv(
        f"{basepath}/{nodefile}",
        low_memory=True,
        usecols=cols,
        dtype=dtypes,
        skiprows=[1],
    ).set_index("key")
    edges = pd.read_csv(f"{basepath}/{edgefile}", low_memory=True).query(
        "u != 'root' and v != 'root'"
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


def generate_individual_profiles(
    country,
    year,
    years,
    crossreference_path,
    preprocessed_graph_path,
    preprocessed_graph_files,
    nodefiles,
    edgefiles,
):
    print(f"Starting {country}, {year}...")
    qG = nx.read_gpickle(
        f"{preprocessed_graph_path}/{preprocessed_graph_files[years.index(year)]}"
    )
    qG_nodes = pd.DataFrame(
        [x for n, x in qG.nodes(data=True) if x.get("key") is not None]
    ).set_index("key")[
        ["type", "document_type", "heading", "law_name", "tokens_n", "tokens_unique"]
    ]

    nf = nodefiles[years.index(year)]
    ef = edgefiles[years.index(year)]
    nodes, edges, G = get_networkx_graph_components(crossreference_path, nf, ef)

    hG = G
    edges_to_remove = [
        (u, v, k)
        for u, v, k, d in G.edges(data="edge_type", keys=True)
        if d != "containment"
    ]
    hG.remove_edges_from(edges_to_remove)
    hG_leaves = {n for n in hG.nodes() if hG.out_degree(n) == 0}
    G = None

    max_leaf_tokens = []
    items_n = []
    seqitems_n = []
    subseqitems_n = []
    internal_references_n = []
    outgoing_references_n = []
    incoming_references_n = []
    outgoing_references_diversity_n = []
    incoming_references_diversity_n = []
    for idx, n in enumerate(qG_nodes.index):
        descendants = nx.descendants(hG, n)
        descendants_leaves = [v for v in descendants if v in hG_leaves]
        desc_nodes = nodes.loc[descendants]
        type_counts = desc_nodes.value_counts("type")
        n_items = type_counts.get("item", 0)
        n_seqitems = type_counts.get("seqitem", 0)
        n_subseqitems = type_counts.get("subseqitem", 0)
        max_tokens_in_leaf = desc_nodes.loc[descendants_leaves].tokens_n.max()
        internal_refs = len(
            edges.query(
                "u in @descendants and v in @descendants and edge_type == 'reference'"
            ).index
        )
        outgoing_refs = qG.out_degree(n)  # weighted out-degree
        incoming_refs = qG.in_degree(n)  # weighted in-degree
        outgoing_refs_diversity = len(set(qG.successors(n)))  # binary out-degree
        incoming_refs_diversity = len(set(qG.predecessors(n)))  # binary in-degree
        items_n.append(n_items)
        seqitems_n.append(n_seqitems)
        subseqitems_n.append(n_subseqitems)
        max_leaf_tokens.append(max_tokens_in_leaf)
        internal_references_n.append(internal_refs)
        outgoing_references_n.append(outgoing_refs)
        incoming_references_n.append(incoming_refs)
        outgoing_references_diversity_n.append(outgoing_refs_diversity)
        incoming_references_diversity_n.append(incoming_refs_diversity)

    qG_nodes["max_leaf_tokens"] = max_leaf_tokens
    qG_nodes["items_n"] = items_n
    qG_nodes["seqitems_n"] = seqitems_n
    qG_nodes["subseqitems_n"] = subseqitems_n
    qG_nodes["self_loops_n"] = internal_references_n
    qG_nodes["reliance_n"] = outgoing_references_n
    qG_nodes["responsibility_n"] = incoming_references_n
    qG_nodes["reliance_diversity_n"] = outgoing_references_diversity_n
    qG_nodes["responsibility_diversity_n"] = incoming_references_diversity_n
    qG_nodes["tokens_n"] = qG_nodes["tokens_n"].fillna(0).astype(int)
    qG_nodes["tokens_unique"] = qG_nodes["tokens_unique"].fillna(0).astype(int)
    qG_nodes["max_leaf_tokens"] = qG_nodes["max_leaf_tokens"].fillna(0).astype(int)

    qG_nodes.to_csv(
        f"../results/chapter-profiles/{year}-chapter-profiles-{country}.csv"
    )


if __name__ == "__main__":
    parser = get_basic_parser()
    parser.add_argument("--years", "-y", nargs="+", type=int, default=YEARS)
    args = parser.parse_args()
    country = get_country(args)
    years = args.years
    crossreference_path = get_crossreference_path(country)
    nodefiles, edgefiles = get_node_and_edge_files(crossreference_path, YEARS)
    preprocessed_graph_path = get_preprocessed_graph_path(country)
    preprocessed_graph_files = get_preprocessed_graph_files(
        preprocessed_graph_path, YEARS
    )
    result_path = "../results/chapter-profiles"
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    if country == "de":
        with Pool(cpu_count() - 4) as p:
            p.starmap(
                generate_individual_profiles,
                [
                    (
                        country,
                        year,
                        YEARS,
                        crossreference_path,
                        preprocessed_graph_path,
                        preprocessed_graph_files,
                        nodefiles,
                        edgefiles,
                    )
                    for year in years
                ],
            )
    else:  # 'us'
        for year in years:
            generate_individual_profiles(
                country,
                year,
                YEARS,
                crossreference_path,
                preprocessed_graph_path,
                preprocessed_graph_files,
                nodefiles,
                edgefiles,
            )
