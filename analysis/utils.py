import argparse
import json

from analysis.statics import (COUNTRIES, DE_CLUSTEREVOLUTION_PATH,
                              DE_CLUSTERRESULT_PATH,
                              DE_CROSSREFERENCE_GRAPH_PATH,
                              DE_PREPROCESSED_GRAPH_PATH,
                              US_CLUSTEREVOLUTION_PATH, US_CLUSTERRESULT_PATH,
                              US_CROSSREFERENCE_GRAPH_PATH,
                              US_PREPROCESSED_GRAPH_PATH)
from quantlaw.utils.files import list_dir


def load_json(path):
    with open(path) as f:
        obj = json.load(f)
    return obj


def get_node_and_edge_files(crossreference_path, years):
    nodefiles = [
        f
        for f in list_dir(crossreference_path, "csv.gz")
        if int(f[:4]) in years and "node" in f
    ]
    edgefiles = [
        f
        for f in list_dir(crossreference_path, "csv.gz")
        if int(f[:4]) in years and "edge" in f
    ]
    assert all([n.startswith(e[:4]) for n, e in zip(nodefiles, edgefiles)])
    return nodefiles, edgefiles


def get_preprocessed_graph_files(preprocessed_graph_path, years):
    files = [
        f
        for f in list_dir(preprocessed_graph_path, "gpickle.gz")
        if int(f[:4]) in years
    ]
    assert len(files) == len(
        years
    ), f"File(s) for year(s) {[y for y in years if not any([int(f[:4]) == y for f in files])]} missing!"
    return files


def get_basic_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("country", type=str)
    return parser


def get_country(args):
    country = args.country.lower()
    if country not in COUNTRIES:
        raise ValueError("Country must be 'us' or 'de'!")
    return country


def get_crossreference_path(country):
    if country == "us":
        return US_CROSSREFERENCE_GRAPH_PATH
    elif country == "de":
        return DE_CROSSREFERENCE_GRAPH_PATH
    else:
        raise ValueError("Country must be 'us' or 'de'!")


def get_preprocessed_graph_path(country):
    if country == "us":
        return US_PREPROCESSED_GRAPH_PATH
    elif country == "de":
        return DE_PREPROCESSED_GRAPH_PATH
    else:
        raise ValueError("Country must be 'us' or 'de'!")


def get_cluster_result_path(country):
    if country == "us":
        return US_CLUSTERRESULT_PATH
    elif country == "de":
        return DE_CLUSTERRESULT_PATH
    else:
        raise ValueError("Country must be 'us' or 'de'!")


def get_cluster_evolution_path(country):
    if country == "us":
        return US_CLUSTEREVOLUTION_PATH
    elif country == "de":
        return DE_CLUSTEREVOLUTION_PATH
    else:
        raise ValueError("Country must be 'us' or 'de'!")
