from pathlib import Path

# Folders (this file is in scripts/mmr/, so the repository folder is two levels up)
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "mmr" / "raw"
CLEAN = ROOT / "data" / "mmr" / "cleaned"

import pandas as pd
from scipy.stats import pearsonr, spearmanr

# read  dataset
df = pd.read_csv(
    CLEAN / "mumps mmr merge with population 2000-2021_final.csv")

# check data types
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

df["MMR_Coverage"] = pd.to_numeric(
    df["MMR_Coverage"], errors="coerce")

df["Mumps_per_100K"] = pd.to_numeric(
    df["Mumps_per_100K"], errors="coerce")

df["State"] = df["State"].str.strip().str.upper()

# check for duplicates
duplicates = df.duplicated(subset=["State", "Year"]).sum()
print("duplicate records:", duplicates)

if duplicates > 0:
    raise ValueError("check duplicate records")

# create coverage and incidence table
coverage = df[
    ["State", "Year", "MMR_Coverage"]].copy()

incidence = df[
    ["State", "Year", "Mumps_per_100K"]].copy()

# function lagged correlations
def calculate_lag(lag_years):

    # copy coverage data
    lagged_coverage = coverage.copy()

    # shift coverage forward to the incidence year
    lagged_coverage["Year"] += lag_years

    # merge coverage and incidence using State/Year
    merged = incidence.merge(
        lagged_coverage,
        on=["State", "Year"],
        how="inner",
        validate="one_to_one")

    # remove missing rows
    merged = merged.dropna(
        subset=["MMR_Coverage", "Mumps_per_100K"])

    # calculate Pearson correlation
    pearson_r, pearson_p = pearsonr(
        merged["MMR_Coverage"],
        merged["Mumps_per_100K"])

    # calculate Spearman correlation
    spearman_r, spearman_p = spearmanr(
        merged["MMR_Coverage"],
        merged["Mumps_per_100K"])

    return {
        "Lag_Years": lag_years,
        "Observations": len(merged),
        "Pearson_r": pearson_r,
        "Pearson_p": pearson_p,
        "Spearman_rho": spearman_r,
        "Spearman_p": spearman_p}

# run same year, one year, two year analyses
results = []

for lag in [0, 1, 2]:
    results.append(calculate_lag(lag))

results_table = pd.DataFrame(results)


# save
results_table.to_csv(
    CLEAN / "mumps and mmr analysis.csv",
    index=False)
