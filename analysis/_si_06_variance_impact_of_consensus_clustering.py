import gzip
import itertools
import multiprocessing
import os
import pickle

import networkx as nx
import pandas as pd

from cdlib import NodeClustering, evaluation
from legal_data_clustering.pipeline.cd_cluster import (add_weighted_clique,
                                                       cluster)

clustering_chunk_size = 1000

consensus_runs_counts = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000]
sample_size = 100
cluster_runs = max(consensus_runs_counts) * sample_size


def init_worker_clustering(graphfile):
    global g
    g = nx.read_gpickle(graphfile)


def _cluster(chunk_idx, dataset):
    start_seed = clustering_chunk_size * chunk_idx
    clustering_path = (
        f"../results/variance_impact_of_consensus/{dataset}_{start_seed}.pickle.gz"
    )

    if os.path.exists(clustering_path):
        print("Skip", clustering_path)
    else:
        clusterings = []
        config = dict(method="infomap", markov_time=1.0, number_of_modules=100)

        for seed in range(start_seed, start_seed + clustering_chunk_size):
            clusterings.append(
                cluster(g, config, return_tree=False, seed=seed).communities
            )

        with gzip.GzipFile(clustering_path, "wb") as f:
            pickle.dump(clusterings, f)
        print("Done", clustering_path)
    return clustering_path


def run_infomap(graphfile, dataset):
    chunks = int(cluster_runs / clustering_chunk_size)
    if chunks * clustering_chunk_size < cluster_runs:
        chunks += 1
    with multiprocessing.Pool(
        initializer=init_worker_clustering, initargs=(graphfile,)
    ) as p:
        clustering_paths = p.starmap(
            _cluster, [(i, dataset) for i in range(chunks)], chunksize=1
        )
    return clustering_paths


def consensus_clustering(g_nodes, clustering_communities):
    consensus_g = nx.Graph()
    consensus_g.add_nodes_from(g_nodes)
    for communities in clustering_communities:
        for community in communities:
            add_weighted_clique(community, consensus_g)

    min_edge = int(len(clustering_communities) * 0.95)

    edges_below_threshold = [
        (u, v)
        for u, v in consensus_g.edges
        if consensus_g.edges[u, v]["weight"] < min_edge
    ]
    consensus_g.remove_edges_from(edges_below_threshold)
    significant_clusters = list(nx.connected_components(consensus_g))
    significant_clusters = sorted(
        [list(x) for x in significant_clusters], key=lambda x: -len(x)
    )
    return significant_clusters


def get_significant_clusters(consensus_runs_count, sample_idx, dataset):
    start = sample_idx * consensus_runs_count
    selected_clsuterings = [
        get_clusterings_from_cache(idx, dataset)
        for idx in range(start, start + consensus_runs_count)
    ]
    significant_clusters = consensus_clustering(g_nodes, selected_clsuterings)
    return significant_clusters


def init_worker_significant_clusters(g_nodes_arg):
    global g_nodes
    g_nodes = g_nodes_arg
    global clusterings_cache
    clusterings_cache = {}


def get_clusterings_from_cache(idx, dataset):
    if idx not in clusterings_cache:
        start_seed = idx - (idx % clustering_chunk_size)
        clustering_path = (
            f"../results/variance_impact_of_consensus/{dataset}_{start_seed}.pickle.gz"
        )
        print("load", clustering_path)
        with gzip.GzipFile(clustering_path, "rb") as f:
            clusterings_chunk = pickle.load(f)
        for i, clustering in enumerate(clusterings_chunk):
            clusterings_cache[start_seed + i] = clustering

    res = clusterings_cache[idx]
    del clusterings_cache[idx]
    # print('use', idx)
    return res


def init_worker_scores(significant_clusterings_arg):
    global significant_clusterings
    significant_clusterings = significant_clusterings_arg


def get_scores(idx1, idx2):
    c1 = significant_clusterings[idx1]
    c2 = significant_clusterings[idx2]

    score_nmi = evaluation.normalized_mutual_information(
        NodeClustering(c1, None, None), NodeClustering(c2, None, None)
    ).score

    score_rand = evaluation.adjusted_rand_index(
        NodeClustering(c1, None, None), NodeClustering(c2, None, None)
    ).score
    return score_nmi, score_rand


def get_stats(consensus_runs_counts, sample_size, dataset, graphfile):
    stats = []

    init_worker_clustering(graphfile)

    for consensus_runs_count in consensus_runs_counts:
        with multiprocessing.Pool(
            initializer=init_worker_significant_clusters,
            initargs=(g.nodes,),
        ) as p:
            significant_clusterings = p.starmap(
                get_significant_clusters,
                [
                    (consensus_runs_count, sample_idx, dataset)
                    for sample_idx in range(sample_size)
                ],
            )
        print(consensus_runs_count, "clusterings done")

        with multiprocessing.Pool(
            initializer=init_worker_scores,
            initargs=(significant_clusterings,),
        ) as p:
            scores = p.starmap(
                get_scores,
                itertools.combinations(range(len(significant_clusterings)), 2),
            )

        scores_nmi, scores_rand = list(zip(*scores))

        stats.append({"NMI": scores_nmi, "Rand": scores_rand})
        print(consensus_runs_count, "stats done")

    return stats


def get_dataframes_from_stats(consensus_runs_counts, stats, dataset):
    df = pd.DataFrame(
        [
            {"consensus_runs": consensus_runs_count, "method": method, "values": val}
            for consensus_runs_count, methods_data in zip(consensus_runs_counts, stats)
            for method, method_results in methods_data.items()
            for val in method_results
        ]
    ).set_index(["method", "consensus_runs"])
    df.to_pickle(f"../results/variance_impact_of_consensus_clustering_{dataset}.pickle")
    df_desc = df.groupby(["method", "consensus_runs"])["values"].describe()
    df_desc.to_csv(f"../results/variance_impact_of_consensus_clustering_{dataset}.csv")
    return df, df_desc


if __name__ == "__main__":

    os.makedirs("../results/variance_impact_of_consensus/", exist_ok=True)

    # US
    graphfile = "../../legal-networks-data/us_reg/10_preprocessed_graph/2019_0-0_1-0_-1.gpickle.gz"
    clustering_paths = run_infomap(graphfile, dataset="us_reg")
    stats = get_stats(consensus_runs_counts, sample_size, "us_reg", graphfile)
    df, df_desc = get_dataframes_from_stats(consensus_runs_counts, stats, "us_reg")

    # DE

    graphfile = "../../legal-networks-data/de_reg/10_preprocessed_graph/2019-12-31_0-0_1-0_-1.gpickle.gz"
    clustering_paths = run_infomap(graphfile, dataset="de_reg")
    stats = get_stats(consensus_runs_counts, sample_size, "de_reg", graphfile)
    df, df_desc = get_dataframes_from_stats(consensus_runs_counts, stats, "de_reg")
