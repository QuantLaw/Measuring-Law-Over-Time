import os
import re


def prettify_table(filename, table_type):
    with open(filename) as f:
        lines = f.readlines()
    if table_type == "summary":
        assert re.fullmatch(r"\\begin\{tabular\}\{[lr]{7}\}\n", lines[0]), lines[0]
        lines[0] = "\\begin{tabular}{lrrrrrr}\n"
        newlines = get_newlines_summary(lines)
    elif table_type == "star":
        newlines = get_newlines_star(lines)
    elif table_type == "star-description":
        newlines = get_newlines_star_description(lines)
    else:
        raise NotImplementedError(
            f"Prettification not implemented for table type {table_type}"
        )
    with open(filename, "w") as f:
        f.writelines(newlines)


def get_newlines_summary(lines):
    newlines = []
    for idx, line in enumerate(lines):
        if idx == 1 and line == "\hline\n":
            line = (
                line[:-1]
                + r" & \multicolumn{3}{c}{\textbf{Statutes}} & \multicolumn{3}{c}{\textbf{Regulations}} \\"
                + "\n"
            )
        line = re.sub(r"(?<![{])(Tokens|Structures|References)", r"\\textbf{\1}", line)
        line = re.sub(r"[(]['](?:Statutes|Regulations)['], (\d+)[)]", r"\1", line)
        line = re.sub(
            r"[(]['](?:Statutes|Regulations)['],\s[']Delta['][)]", r"$\\Delta$", line
        )
        newlines.append(line)
    return newlines


def get_newlines_star(lines):
    newlines = []
    for idx, line in enumerate(lines):
        if idx == 1 and line == "\hline\n":
            line = (
                line[:-1]
                + r"&\multicolumn{2}{c}{\textbf{1998}}&\multicolumn{2}{c}{\textbf{2019}}\\"
                + "\n"
            )
        line = re.sub(r"(?<![{])(Sink|Hinge|Source|S-Hub|R-Hub)", r"\\textbf{\1}", line)
        line = re.sub(r"[/](?:1998|2019)", "", line)
        newlines.append(line)
    return newlines


def get_newlines_star_description(lines):
    newlines = []
    for idx, line in enumerate(lines):
        if idx == 0:
            line = r"\begin{tabular}{rrrrlp{0.4\textwidth}p{0.2\textwidth}}" + "\n"
        newlines.append(line)
    return newlines


if __name__ == "__main__":
    for country in ["us", "de"]:
        for table_type in ["summary", "star"]:
            if os.path.exists(f"{table_type}-statistics-{country}.tex"):
                prettify_table(
                    f"{table_type}-statistics-{country}.tex", table_type=table_type
                )
        for year in [1998, 2019]:
            if os.path.exists(f"star-descriptions-{country}-{year}.tex"):
                prettify_table(
                    f"star-descriptions-{country}-{year}.tex",
                    table_type="star-description",
                )
