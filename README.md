# Measuring Law Over Time
Paper and data analysis for "Measuring Law Over Time: A network analytical framework and an application to statutes and regulations in the United States and Germany" 

Corinna Coupette, Janis Beckedorf, Dirk Hartung, Michael Bommarito, and Daniel Martin Katz, *Measuring Law Over Time*, Frontiers in Physics, 2021, https://www.frontiersin.org/articles/10.3389/fphy.2021.658463.

## Structure 

- `analysis`: python code to prepare the input data for the graphics and tables presented in the paper
- `graphics`: graphics and tables presented in the paper; to get the tables into paper-shape, run `prettify_tables.py` in this folder
- `notebooks`: jupyter notebooks generating all graphics (and some of the tables) presented in the paper
- `results`: data for the micro-level connectivity and profiles sections that would otherwise clutter up the graphics folder
- `supplements`: manually edited supplementary material (law name lists for the German profile case study and cluster family labels)
- `writing`: the source code of the paper, including a `figures` folder composing paper figures and tables from the graphics folder

## Reproducing the Paper Results

1. It is assumed that you have Python 3.7 installed. (Other versions are not tested.)
2. Set up a virtual environment and activate it. (This is not required but recommended.)
3. Download the data at https://doi.org/10.5281/zenodo.4660133, extract it, so that `legal-networks-data` is next to the folder of this repository and has the subfolders `de`, `us`, and `us_reg`. Their subfolders must be manually extracted, if needed to run the analysis.
5. Run `run_analysis_and_notebooks.sh` to install the requirements and run the code.
6. The results are available in this folder `writing`.


## Related Work

Daniel Martin Katz, Corinna Coupette, Janis Beckedorf, and Dirk Hartung, Complex Societies and the Growth of the Law, *Sci. Rep.* **10** (2020), [https://doi.org/10.1038/s41598-020-73623-x](https://doi.org/10.1038/s41598-020-73623-x)

Related Repositories:
- [Complex Societies and the Growth of the Law](https://github.com/QuantLaw/Complex-Societies-and-Growth) ([First Publication Release](http://dx.doi.org/10.5281/zenodo.4070769))
- [Legal Data Preprocessing](https://github.com/QuantLaw/legal-data-preprocessing) ([First Publication Release](http://dx.doi.org/10.5281/zenodo.4070773))
- [Legal Data Clustering](https://github.com/QuantLaw/legal-data-clustering) ([First Publication Release](http://dx.doi.org/10.5281/zenodo.4070775))

Related Data: [Preprocessed Input Data for *Sci. Rep.* **10** (2020)](http://dx.doi.org/10.5281/zenodo.4070767)
