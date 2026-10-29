# Vaccination and the Return of "Eliminated" Diseases

UMGC BIOT 670I capstone, Group 3 (Amir Sadeghi, Nadin Salih, Maliha Shah, Liane Rosario). Instructor: Prof. Wolfgang Rumpf.

**Question:** is there a correlation between vaccine coverage (MMR, hepatitis B) and the incidence of measles, mumps, rubella and acute hepatitis B, at the state and year level?

## How to run it

You need Python 3.10 or newer. Open a terminal in this folder.

**Option 1: open the dashboard right away**

```
python -m install -r requirements.txt
python -m streamlit run app.py
```

All the tables and figures are already saved in this repository, so the dashboard works straight after downloading.

**Option 2: rebuild everything from the raw data first (needs internet)**

```
python -m install -r requirements.txt
python run_all.py
python -m streamlit run app.py
```

`run_all.py` rebuilds the tables and figures (about 1 minute) and replaces the saved copies. Three of the hepatitis B scripts download archived CDC web pages, so you need an internet connection.

## What is in the folders

```
app.py              the Streamlit dashboard
run_all.py          runs all the scripts in the right order
requirements.txt    Python packages
scripts/
  mmr/              measles, mumps, rubella vs MMR and hepatitis B coverage
  hepB/             hepatitis B analysis
data/
  mmr/raw/          raw inputs: case counts, NIS coverage, population
  hepB/raw/         raw inputs: CDC hepatitis B tables
  shared/           ChildVaxView coverage file used by both parts
  \*/cleaned/        cleaned tables (made by the scripts)
  \*/analysis/       result tables (made by the scripts)
documents/figures/  figures (made by the scripts)
```

All tables and figures are saved here. `run\_all.py` rebuilds most of them.

## What the scripts do

|Part|Scripts|Result|
|-|-|-|
|Measles, mumps, rubella, hepatitis B vs coverage, 1995-2023|`scripts/mmr/cleaning\_data.py`, then `analysis.py`|cleaned tables, correlation and regression tables, figures 1 to 8|
|Hepatitis B, age-specific and state-level|the scripts in `scripts/hepB/`|cleaned tables, regression results, figures|
|Mumps and MMR, 2000-2021|`scripts/mmr/mumps and mmr analysis.py`|one correlation table|

### The main analysis (`scripts/mmr/analysis.py`)

1. Correlation of coverage and disease rate, all states and years pooled.
2. Fixed effects: each state is compared only with itself over time, with 95% confidence intervals.
3. Time lags of 0 to 3 years, in both directions.
4. Poisson regression: rate ratio per +10 points of coverage.
5. Controls: salmonellosis (should show nothing) and measles before and after the 1963 vaccine (should show a drop).
6. Appendix check: matching coverage to disease by birth year vs by age.

Settings are at the top of the script.

## Data sources

|Data|File(s)|Source|
|-|-|-|
|Cases 1993-2015|`data/mmr/raw/Data\_extracted\_from\_published\_tables\_1993-2015.xlsx`|CDC MMWR annual tables (extracted by the group)|
|Cases 2016-2023|`data/mmr/raw/NNDSS\_\*.xls`|CDC NNDSS|
|Measles 1950-1992|`data/mmr/raw/Measles\_project\_tycho\_1950-1992.csv`|Project Tycho, University of Pittsburgh|
|Population 1993-2023|`data/mmr/raw/population\_1993-2023.csv`|US Census Bureau|
|Coverage by survey year|`data/mmr/raw/nis\_coverage\_1995-2024.csv`|CDC NIS-Child|
|Coverage by birth year|`data/shared/ChildVaxView\_...csv`|CDC ChildVaxView|
|Hepatitis B surveillance|`data/hepB/raw/table-2.1.xlsx`, `figure-2.4.xlsx`|CDC viral hepatitis surveillance report|
|Hepatitis B coverage 1994-2014|`data/hepB/raw/HepB\_Historical\_Coverage\_1994\_2014\_snapshot.csv`|CDC archived NIS-Child page (saved copy)|

## Notes

* The dashboard reads 9 of the saved tables: 4 in `data/mmr/analysis/correlations/`, `data/mmr/cleaned/linked\_state\_year\_no\_offset.csv`, `data/hepB/cleaned/HepB\_Harmonized\_Data.csv` and 3 in `data/hepB/analysis/`.
* Some saved files are not rebuilt by `run\_all.py`, because their scripts need input files that are not included. They are kept as saved: the three mumps figures in `documents/figures/mmr/`, `mmr coverage 1995-2025.csv`, `mumps cases cleaned 1923-2021\_final.csv`, `mumps mmr merge with population 2000-2021\_final.csv` and `HepB\_AgeSpecific\_Incidence\_2008\_2023.csv`.
* `HepB\_Exploratory\_Analysis.py`, `Coverage\_DataCheck.py` and `mumps and mmr graphs.py` only print or show plots, so `run\_all.py` does not run them.

