import pandas as pd

from analysis.statics import YEARS
from analysis.utils import (get_basic_parser, get_cluster_evolution_path,
                            get_cluster_result_path, get_country,
                            get_crossreference_path, get_node_and_edge_files,
                            load_json)
from quantlaw.utils.files import list_dir


def create_cluster_volume_df(country, n_clusters):
    cluster_result_path = get_cluster_result_path(country)
    cluster_result_files = [
        f"{cluster_result_path}/{f}"
        for f in list_dir(cluster_result_path, f"_n{n_clusters}_m1-0_s0_c1000.json")
        if int(f[:4]) in YEARS
    ]
    cluster_evolution_path = get_cluster_evolution_path(country)
    cluster_evolution_file = [
        f"{cluster_evolution_path}/{f}"
        for f in list_dir(
            cluster_evolution_path,
            f"_n{n_clusters}_m1-0_s0_c1000.families.json",
        )
    ][0]
    crossreference_path = get_crossreference_path(country)
    nodefiles, _ = get_node_and_edge_files(crossreference_path, YEARS)

    cluster_families = {
        idx: sorted(
            [x.replace("-12-31", "") for x in content]
        )  # this needs to match the -MM-DD part of the DE snapshots
        for idx, content in enumerate(load_json(cluster_evolution_file))
    }
    cluster_families_inverted = {
        cluster: idx
        for idx, clusters in cluster_families.items()
        for cluster in clusters
    }

    cluster_results = {
        int(fn.split("/")[-1][:4]): {  # the key is the snapshot year
            idx: content for idx, content in enumerate(load_json(fn)["communities"])
        }
        for fn in cluster_result_files
    }

    cluster_volumes = pd.DataFrame(columns=["statute", "regulation"])
    for year, file in zip(YEARS, nodefiles):
        print(f"Starting {year}...", end="\r")
        assert file.startswith(str(year))
        nodes = pd.read_csv(
            f"{crossreference_path}/{file}",
            usecols=["key", "document_type", "tokens_n"],
            low_memory=True,
            skiprows=[1],  # the global root is at position 1 and we don't need it
        ).set_index("key")
        clusters = cluster_results[year]
        dfs = []
        for idx in list(clusters.keys()):
            dfs.append(
                nodes.loc[clusters[idx]]
                .groupby("document_type")
                .sum()
                .T.rename(dict(tokens_n=f"{year}_{idx}"))
            )
        cluster_volumes = (
            pd.concat([cluster_volumes, *dfs], ignore_index=False).fillna(0).astype(int)
        )

    cluster_volumes["year"] = cluster_volumes.index.map(lambda x: int(x[:4]))
    cluster_volumes["total"] = cluster_volumes.statute + cluster_volumes.regulation
    cluster_volumes["family"] = cluster_volumes.index.map(cluster_families_inverted)

    cluster_family_volumes = (
        cluster_volumes.groupby(["family", "year"]).sum().reset_index()
    )
    return cluster_family_volumes


if __name__ == "__main__":
    parser = get_basic_parser()
    parser.add_argument("-l", "--labels", action="store_true")
    parser.add_argument("-n", "--number_of_clusters", type=int, default=100)
    args = parser.parse_args()
    country = get_country(args)
    with_labels = args.labels
    n_clusters = args.number_of_clusters
    df = create_cluster_volume_df(country, n_clusters)
    df["family"] = df["family"].astype(int)
    df.to_csv(
        f"../results/cluster-family-volumes-{country}-n{n_clusters}.csv",
        index=False,
    )
    if with_labels:
        last_year = YEARS[-1]
        largest_families = (
            df.query("year == @last_year")
            .sort_values("total", ascending=False)[:10]
            .family.values
        )
        labels = pd.DataFrame(columns=["family", "label"], data=None)
        labels["family"] = largest_families
        labels["family"] = labels.family.astype(int)
        labels.to_csv(
            f"../supplements/cluster-family-labels-new-n{n_clusters}-{country}-empty.csv",
            index=False,
        )
