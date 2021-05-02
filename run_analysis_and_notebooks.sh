#!/bin/sh
set -e

echo -n "Install requirements? (y/n)"
read REPLY

if [[ $REPLY =~ ^[Yy]$ ]]
  then
    pip install -r requirements.txt
fi

export PYTHONPATH=$PYTHONPATH:$(pwd)

cd analysis

for i in "$@"
do
echo "STARTING ANALYSIS STEP $i"
case $i in
  1)
  for COUNTRY in us de
  do
    python _01_basic_statistics.py $COUNTRY
    echo "DONE: _01_basic_statistics $COUNTRY"
  done
  ;;
  2)
  for COUNTRY in us de
  do
    python _02_connectivity.py $COUNTRY
    echo "DONE: _02_connectivity $COUNTRY"
  done
  ;;
  3)
  for COUNTRY in us de
  do
    python _03_family_evolution.py $COUNTRY --labels
    echo "DONE: _03_family_evolution $COUNTRY"
  done
  ;;
  4)
  for COUNTRY in us de
  do
    python _04_structures.py $COUNTRY
    echo "DONE: _04_structures $COUNTRY"
  done
  ;;
  5)
  for COUNTRY in us de
  do
    python _05_structure_statistics.py $COUNTRY
    echo "DONE: _05_structure_statistics $COUNTRY"
  done
  ;;
  15)
  python _si_05_variance_between_infomap_runs.py
  echo "DONE: _si_05_variance_between_infomap_runs"
  ;;
  16)
  python _si_06_variance_impact_of_consensus_clustering.py
  echo "DONE: _si_06_variance_impact_of_consensus_clustering"
  ;;
  17)
  python _si_07_citation_extraction_quality.py
  echo "DONE: _si_07_citation_extraction_quality"
  ;;
esac
done

cd ../notebooks

for i in "$@"
do
echo "STARTING NOTEBOOK STEP $i"
case $i in
  1)
  jupyter nbconvert --inplace  --to notebook --execute 01-basic-statistics.ipynb
  echo "DONE: notebooks/01-basic-statistics"
  ;;
  2)
  jupyter nbconvert --inplace  --to notebook --execute 02-connectivity.ipynb
  echo "DONE: notebooks/02-connectivity"
  ;;
  3)
  jupyter nbconvert --inplace  --to notebook --execute 03-family-evolution.ipynb
  echo "DONE: notebooks/03-family-evolution"
  ;;
  4)
  jupyter nbconvert --inplace  --to notebook --execute 04-structures.ipynb
  echo "DONE: notebooks/04-structures"
  ;;
  5)
  jupyter nbconvert --inplace  --to notebook --execute 05-structure-statistics.ipynb
  echo "DONE: notebooks/05-structure-statistics"
  ;;
  11)
  jupyter nbconvert --inplace --to notebook --execute si-01-missing-volumes-in-cfr.ipynb
  echo "DONE: notebooks/si-01-missing-volumes-in-cfr"
  ;;
  12)
  jupyter nbconvert --inplace --to notebook --execute si-02-community-sankey-plot.ipynb
  echo "DONE: notebooks/si-02-community-sankey-plot"
  ;;
  13)
  jupyter nbconvert --inplace --to notebook --execute si-03-tfidf-cluster-family-inspection.ipynb
  echo "DONE: notebooks/si-03-tfidf-cluster-family-inspection"
  ;;
  14)
  jupyter nbconvert --inplace --to notebook --execute si-04-variance-for-preferred-number-of-clusters.ipynb
  echo "DONE: notebooks/si-04-variance-for-preferred-number-of-clusters"
  ;;
  15)
  jupyter nbconvert --inplace --to notebook --execute si-05-variance-between-infomap-runs.ipynb
  echo "DONE: notebooks/si-05-variance-between-infomap-runs"
  ;;
  16)
  jupyter nbconvert --inplace --to notebook --execute si-06-variance-impact-of-consensus-clustering.ipynb
  echo "DONE: notebooks/si-06-variance-impact-of-consensus-clustering"
  ;;
  17)
  jupyter nbconvert --inplace --to notebook --execute si-07-citation-extraction-quality.ipynb
  echo "DONE: notebooks/si-07-citation-extraction-quality"
  ;;
  18)
  jupyter nbconvert --inplace --to notebook --execute si-08-profile-extensions.ipynb
  echo "DONE: notebooks/si-07-profile-extensions"
  ;;
esac
done

cd ../graphics

python prettify-tables.py

cd ../notebooks

echo -n "Clear notebooks? (y/n)"
read REPLY

if [[ $REPLY =~ ^[Yy]$ ]]
  then
    python clear_metadata_from_notebooks.py
    jupyter nbconvert --clear-output --inplace $(ls *.ipynb)
fi

cd ../writing/figures

latexmk -pdf figure*.tex
latexmk -c -pdf figure*.tex

cd ..

latexmk -pdf main.tex si.tex
latexmk -c -pdf main.tex si.tex

python merge_tex_files.py
