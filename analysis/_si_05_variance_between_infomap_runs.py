import itertools
import multiprocessing
from collections import defaultdict

import networkx as nx
import pandas as pd

from cdlib import NodeClustering, evaluation
from legal_data_clustering.pipeline.cd_cluster import cluster


def _cluster(run_idx):
    return cluster(g, config, return_tree=False, seed=run_idx * 10000).communities


def init_worker(graphfile):
    global g
    g = nx.read_gpickle(graphfile)
    global config
    config = dict(method="infomap", markov_time=1.0, number_of_modules=100)


def analyze_cluster_run_diff(year, graphfile):

    with multiprocessing.Pool(4, initializer=init_worker, initargs=(graphfile,)) as p:
        clusterings = p.map(_cluster, range(100))

    init_worker(graphfile)

    scores_nmi = [
        evaluation.normalized_mutual_information(
            NodeClustering(c1, g, None), NodeClustering(c2, g, None)
        ).score
        for c1, c2 in itertools.combinations(clusterings, 2)
    ]

    scores_rand = [
        evaluation.adjusted_rand_index(
            NodeClustering(c1, g, None), NodeClustering(c2, g, None)
        ).score
        for c1, c2 in itertools.combinations(clusterings, 2)
    ]

    #     scores_pairs = [
    #         evaluation.adjusted_mutual_information(
    #             NodeClustering(c1, g, None),
    #             NodeClustering(c2, g, None)
    #         ).score
    #         for c1, c2 in zip(clusterings[::2],clusterings[1::2])
    #     ]

    return {
        "NMI": scores_nmi,
        "Rand": scores_rand,
    }


if __name__ == "__main__":
    years = list(range(1998, 2019 + 1))

    # US

    scores = defaultdict(list)
    for year in years:
        scores_dict = analyze_cluster_run_diff(
            year,
            f"../../legal-networks-data/us_reg/10_preprocessed_graph/{year}_0-0_1-0_-1.gpickle.gz",
        )
        for method, method_scores in scores_dict.items():
            scores[method].append(method_scores)

        print(year, "done")

    dfs = []
    for method in scores:
        df = pd.DataFrame({y: s for y, s in zip(years, scores[method])}).T
        df["Method"] = method
        df = df.reset_index().set_index(["Method", "index"]).T
        dfs.append(df)
    df = pd.concat(dfs)
    df.to_pickle("../results/variance_infomap_runs_us_reg.pickle")

    # DE

    scores = defaultdict(list)
    for year in years:
        scores_dict = analyze_cluster_run_diff(
            year,
            f"../../legal-networks-data/de_reg/10_preprocessed_graph/{year}-12-31_0-0_1-0_-1.gpickle.gz",
        )
        for method, method_scores in scores_dict.items():
            scores[method].append(method_scores)

        print(year, "done")

    # %%

    dfs = []
    for method in scores:
        df = pd.DataFrame({y: s for y, s in zip(years, scores[method])}).T
        df["Method"] = method
        df = df.reset_index().set_index(["Method", "index"]).T
        dfs.append(df)
    df = pd.concat(dfs)
    df.to_pickle("../results/variance_infomap_runs_de_reg.pickle")
