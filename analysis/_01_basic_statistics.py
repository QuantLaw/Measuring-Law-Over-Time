import pandas as pd

from analysis.statics import YEARS
from analysis.utils import (get_basic_parser, get_country,
                            get_crossreference_path, get_node_and_edge_files)
from tabulate import tabulate


def get_networkx_graph_components(basepath, nodefile, edgefile):
    nodes = pd.read_csv(
        f"{basepath}/{nodefile}",
        usecols=["key", "document_type", "level", "type", "tokens_n"],
    ).set_index("key")
    edges = pd.read_csv(f"{basepath}/{edgefile}")
    return nodes, edges


def abs_to_rel(abs_array):
    rel_array = abs_array / abs_array[0]
    return rel_array


def create_basic_statistics_dataframe(crossreference_path, years):
    nodefiles, edgefiles = get_node_and_edge_files(crossreference_path, years)
    tokens_n_abs_reg = []
    tokens_n_abs_sta = []
    structures_n_abs_sta = []
    structures_n_abs_reg = []
    structures_n_abs_sta_ssi = []
    structures_n_abs_reg_ssi = []
    seqitems_n_abs_sta = []
    seqitems_n_abs_reg = []
    crossrefs_n_abs_sta = []
    crossrefs_n_abs_reg = []
    crossrefs_n_abs_sta_reg = []
    crossrefs_n_abs_reg_sta = []
    for nf, ef in zip(nodefiles, edgefiles):
        print(f"Starting year {nf[:4]}...", end="\r")
        nodes, edges = get_networkx_graph_components(crossreference_path, nf, ef)
        edges = edges.join(nodes[["document_type"]], on="u").rename(
            dict(document_type="u_document_type"), axis=1
        )
        edges = edges.join(nodes[["document_type"]], on="v").rename(
            dict(document_type="v_document_type"), axis=1
        )
        tokens_n_abs_reg.append(
            nodes.query("level == 0 and document_type == 'regulation'")[
                "tokens_n"
            ].sum()
        )
        tokens_n_abs_sta.append(
            nodes.query("level == 0 and document_type == 'statute'")["tokens_n"].sum()
        )
        structures_n_abs_sta.append(
            nodes.query(
                "level != -1 and document_type == 'statute' and type != 'subseqitem'"
            ).count()["document_type"]
        )
        structures_n_abs_reg.append(
            nodes.query(
                "level != -1 and document_type == 'regulation' and type != 'subseqitem'"
            ).count()["document_type"]
        )
        structures_n_abs_sta_ssi.append(
            nodes.query("level != -1 and document_type == 'statute'").count()[
                "document_type"
            ]
        )
        structures_n_abs_reg_ssi.append(
            nodes.query("level != -1 and document_type == 'regulation'").count()[
                "document_type"
            ]
        )
        seqitems_n_abs_sta.append(
            nodes.query("document_type == 'statute' and type == 'seqitem'").count()[
                "tokens_n"
            ]
        )
        seqitems_n_abs_reg.append(
            nodes.query("document_type == 'regulation' and type == 'seqitem'").count()[
                "tokens_n"
            ]
        )
        crossrefs_n_abs_sta.append(
            edges.query(
                "edge_type == 'reference' and u_document_type == 'statute' and v_document_type == 'statute'"
            ).count()["edge_type"]
        )
        crossrefs_n_abs_reg.append(
            edges.query(
                "edge_type == 'reference' and u_document_type == 'regulation' and v_document_type == 'regulation'"
            ).count()["edge_type"]
        )
        crossrefs_n_abs_sta_reg.append(
            edges.query(
                "edge_type == 'reference' and u_document_type == 'statute' and v_document_type == 'regulation'"
            ).count()["edge_type"]
        )
        crossrefs_n_abs_reg_sta.append(
            edges.query(
                "edge_type == 'reference' and u_document_type == 'regulation' and v_document_type == 'statute'"
            ).count()["edge_type"]
        )
    tokens_n_rel_reg = abs_to_rel(tokens_n_abs_reg)
    tokens_n_rel_sta = abs_to_rel(tokens_n_abs_sta)
    structures_n_rel_sta = abs_to_rel(structures_n_abs_sta)
    structures_n_rel_reg = abs_to_rel(structures_n_abs_reg)
    structures_rel_sta_ssi = abs_to_rel(structures_n_abs_sta_ssi)
    structures_rel_reg_ssi = abs_to_rel(structures_n_abs_reg_ssi)
    seqitems_n_rel_sta = abs_to_rel(seqitems_n_abs_sta)
    seqitems_n_rel_reg = abs_to_rel(seqitems_n_abs_reg)
    crossrefs_n_rel_sta = abs_to_rel(crossrefs_n_abs_sta)
    crossrefs_n_rel_reg = abs_to_rel(crossrefs_n_abs_reg)
    crossrefs_n_rel_sta_reg = abs_to_rel(crossrefs_n_abs_sta_reg)
    crossrefs_n_rel_reg_sta = abs_to_rel(crossrefs_n_abs_reg_sta)
    df = pd.DataFrame(
        dict(
            tokens_n_abs_sta=tokens_n_abs_sta,
            tokens_n_abs_reg=tokens_n_abs_reg,
            structures_n_abs_sta=structures_n_abs_sta,
            structures_n_abs_reg=structures_n_abs_reg,
            structures_n_abs_sta_ssi=structures_n_abs_sta_ssi,
            structures_n_abs_reg_ssi=structures_n_abs_reg_ssi,
            seqitems_n_abs_sta=seqitems_n_abs_sta,
            seqitems_n_abs_reg=seqitems_n_abs_reg,
            crossrefs_n_abs_sta=crossrefs_n_abs_sta,
            crossrefs_n_abs_reg=crossrefs_n_abs_reg,
            crossrefs_n_abs_sta_reg=crossrefs_n_abs_sta_reg,
            crossrefs_n_abs_reg_sta=crossrefs_n_abs_reg_sta,
            tokens_n_rel_sta=tokens_n_rel_sta,
            tokens_n_rel_reg=tokens_n_rel_reg,
            structures_n_rel_sta=structures_n_rel_sta,
            structures_n_rel_reg=structures_n_rel_reg,
            structures_rel_sta_ssi=structures_rel_sta_ssi,
            structures_rel_reg_ssi=structures_rel_reg_ssi,
            seqitems_n_rel_sta=seqitems_n_rel_sta,
            seqitems_n_rel_reg=seqitems_n_rel_reg,
            crossrefs_n_rel_sta=crossrefs_n_rel_sta,
            crossrefs_n_rel_reg=crossrefs_n_rel_reg,
            crossrefs_n_rel_sta_reg=crossrefs_n_rel_sta_reg,
            crossrefs_n_rel_reg_sta=crossrefs_n_rel_reg_sta,
        )
    )
    df.index = years
    return df


def create_summary_statistics_dataframe(df):
    summary_statistics = pd.DataFrame(
        data=0,
        index=["Tokens", "Structures", "References"],
        columns=pd.MultiIndex.from_tuples(
            [
                ("Statutes", 1998),
                ("Statutes", 2019),
                ("Statutes", "Delta"),
                ("Regulations", 1998),
                ("Regulations", 2019),
                ("Regulations", "Delta"),
            ]
        ),
    )
    summary_statistics.loc["Tokens"] = [
        df.tokens_n_abs_sta[1998],
        df.tokens_n_abs_sta[2019],
        round(
            (df.tokens_n_abs_sta[2019] - df.tokens_n_abs_sta[1998])
            / df.tokens_n_abs_sta[1998]
            * 100
        ),
        df.tokens_n_abs_reg[1998],
        df.tokens_n_abs_reg[2019],
        round(
            (df.tokens_n_abs_reg[2019] - df.tokens_n_abs_reg[1998])
            / df.tokens_n_abs_reg[1998]
            * 100
        ),
    ]
    summary_statistics.loc["Structures"] = [
        df.structures_n_abs_sta_ssi[1998],
        df.structures_n_abs_sta_ssi[2019],
        round(
            (df.structures_n_abs_sta_ssi[2019] - df.structures_n_abs_sta_ssi[1998])
            / df.structures_n_abs_sta_ssi[1998]
            * 100
        ),
        df.structures_n_abs_reg_ssi[1998],
        df.structures_n_abs_reg_ssi[2019],
        round(
            (df.structures_n_abs_reg_ssi[2019] - df.structures_n_abs_reg_ssi[1998])
            / df.structures_n_abs_reg_ssi[1998]
            * 100
        ),
    ]
    summary_statistics.loc["References"] = [
        df.crossrefs_n_abs_sta[1998],
        df.crossrefs_n_abs_sta[2019],
        round(
            (df.crossrefs_n_abs_sta[2019] - df.crossrefs_n_abs_sta[1998])
            / df.crossrefs_n_abs_sta[1998]
            * 100
        ),
        df.crossrefs_n_abs_reg[1998],
        df.crossrefs_n_abs_reg[2019],
        round(
            (df.crossrefs_n_abs_reg[2019] - df.crossrefs_n_abs_reg[1998])
            / df.crossrefs_n_abs_reg[1998]
            * 100
        ),
    ]
    return summary_statistics


def num_to_str(num):
    if num > 1e6:
        return f"{num / 1e6:.1f}~M"
    elif num > 1e3:
        return f"{num / 1e3:.1f}~K"
    elif num:
        return str(num)
    else:
        num


def df_with_short_num_format(df):
    for key, value in df.items():
        df[key] = df[key].apply(num_to_str)


if __name__ == "__main__":
    parser = get_basic_parser()
    args = parser.parse_args()
    country = get_country(args)
    crossreference_path = get_crossreference_path(country)

    df = create_basic_statistics_dataframe(crossreference_path, YEARS)
    df.to_csv(f"../results/basic-statistics-{country}.csv")

    summary_statistics = create_summary_statistics_dataframe(df)
    df_with_short_num_format(summary_statistics)
    with open(f"../graphics/summary-statistics-{country}.tex", "w") as f:
        f.write(tabulate(summary_statistics, tablefmt="latex_raw", headers="keys"))
