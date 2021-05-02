import re
from glob import glob

figure_pattern = re.compile(
    re.escape("\\begin{figure}") + r"[\s\S]+?" + re.escape("\\end{figure}"),
    flags=re.MULTILINE,
)

table_pattern = re.compile(
    re.escape("\\begin{table}") + r"[\s\S]+?" + re.escape("\\end{table}"),
    flags=re.MULTILINE,
)

if __name__ == "__main__":
    tex_files = (
        glob("text/*.tex")
        + glob("figures/table_*.tex")
        + glob("../graphics/star*.tex")
        + glob("../graphics/summary*.tex")
    )
    with open("main.tex") as f:
        main = f.read()

    for tex_file in tex_files:
        needle = "\input{" + tex_file.replace(".tex", "") + "}"
        with open(tex_file) as f:
            sub_content = f.read()
        main = main.replace(needle, sub_content)

    for fig_text in figure_pattern.findall(main):
        print(fig_text)
        print("-" * 25)

    main = figure_pattern.sub("", main)

    table_texts = table_pattern.findall(main)
    for table_text in table_texts:
        print(table_text)
        print("-" * 25)

    main = table_pattern.sub("", main)

    table_text_merged = "\n\n\n".join(table_texts)

    main = main.replace(
        "\\end{document}",
        "\\clearpage\n\n" + table_text_merged + "\n\n" + "\\end{document}",
    )

    with open("merged.tex", "w") as f:
        f.write(main)
