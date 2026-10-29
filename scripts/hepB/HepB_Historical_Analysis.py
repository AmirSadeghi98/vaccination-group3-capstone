from pathlib import Path

# Folders (this file is in scripts/hepB/, so the repository folder is two levels up)
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "hepB" / "raw"
CLEAN = ROOT / "data" / "hepB" / "cleaned"
FIGS = ROOT / "documents" / "figures" / "hepB"
CLEAN.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

# Historical HepB Analysis
# National age-specific acute HepB incidence, 2008–2023

import pandas as pd

# Load CDC Excel workbook
raw = pd.read_excel(RAW / "figure-2.4.xlsx", sheet_name="Fig2.4", header=None)

# Inspect worksheet structure
print("\nWorksheet shape:")
print(raw.shape)

print("\nFirst 9 rows:")
print(raw.head(9).to_string(index=False, header=False))

# Reshape historical incidence data
# Extract year labels
years = raw.iloc[1, 3:19].astype(int).tolist()

# Extract age groups and incidence rates
incidence = raw.iloc[2:8, 2:19].copy()

# Assign column names
incidence.columns = ["age_group"] + years

# Reshape from wide to long format
historical = incidence.melt(id_vars="age_group", var_name="year", value_name="acute_hepb_rate")

# Ensure correct data types
historical["year"] = historical["year"].astype(int)
historical["acute_hepb_rate"] = pd.to_numeric(historical["acute_hepb_rate"], errors="coerce")

# Add source information
historical["source"] = "CDC Hepatitis Surveillance 2023, Figure 2.4"

# Sort observations
historical = historical.sort_values(["year", "age_group"]).reset_index(drop=True)

# Validate
print("\nHistorical Dataset Shape:")
print(historical.shape)

print("\nMissing Values:")
print(historical.isna().sum())

print("\nObservations Per Year:")
print(historical.groupby("year").size())

print("\nFirst 12 Rows:")
print(historical.head(12).to_string(index=False))

# Save cleaned historical incidence data
output_file = CLEAN / "HepB_AgeSpecific_Incidence_2008_2023.csv"

historical.to_csv(output_file, index=False, encoding="utf-8-sig")

print("\nCleaned historical dataset saved:")
print(output_file)

print("\nFinal dataset dimensions:")
print(historical.shape)

# Retrieve CDC historical surveillance dataset
url = "https://archive.cdc.gov/www_cdc_gov/hepatitis/statistics/2018surveillance/HepB.htm"

tables = pd.read_html(url)

# Clean scraped CDC 2018 age-specific data
older = tables[3].copy()

# Reshape wide table into long format
older = older.melt(id_vars="Age (years)", var_name="year", value_name="acute_hepb_rate")

# Standardize column names and age-group labels
older = older.rename(columns={"Age (years)": "age_group"})

older["age_group"] = (older["age_group"].astype(str).str.replace("-", "–", regex=False).replace({
    "0–19": "0–19 years",
    "20–29": "20–29 years",
    "30–39": "30–39 years",
    "40–49": "40–49 years",
    "50–59": "50–59 years",
    "60+": "≥60 years"}))

older["year"] = older["year"].astype(int)
older["acute_hepb_rate"] = pd.to_numeric(older["acute_hepb_rate"], errors="coerce")

# Compare overlapping years (2008–2018)
comparison = older.merge(historical, on=["year", "age_group"], suffixes=("_2018", "_2023"))

comparison["difference"] = (comparison["acute_hepb_rate_2018"] - comparison["acute_hepb_rate_2023"])

print("\nOlder dataset shape:", older.shape)
print("Missing values:", older.isna().sum().sum())
print("Overlapping observations:", len(comparison))

print("\nAge groups in older dataset:")
print(older["age_group"].unique())

print("\nNon-matching incidence rates:")
print(comparison.loc[comparison["difference"].abs() > 0.000001,
        ["year", "age_group",
         "acute_hepb_rate_2018",
         "acute_hepb_rate_2023",
         "difference"]].to_string(index=False))

# Combine historical age-specific incidence datasets
# Retain only years unavailable in the newer dataset
older_unique = older[older["year"] < 2008].copy()

older_unique["source"] = ("CDC Hepatitis Surveillance 2018, Figure 2.4")

# Combine historical and newer observations
combined = pd.concat([older_unique, historical], ignore_index=True)

combined = combined.sort_values(["year", "age_group"]).reset_index(drop=True)

# Validate combined dataset
print("\nCombined Dataset Shape:")
print(combined.shape)

print("\nYear Range:")
print(combined["year"].min(), "-", combined["year"].max())

print("\nMissing Values:")
print(combined.isna().sum())

print("\nDuplicate Year/Age Group Combinations:")
print(combined.duplicated(["year", "age_group"]).sum())

print("\nObservations Per Year:")
print(combined.groupby("year").size().to_string())

# Save combined dataset
output_file = CLEAN / "HepB_AgeSpecific_Incidence_2003_2023.csv"
combined.to_csv(output_file, index=False, encoding="utf-8-sig")

print("\nCombined dataset saved:", output_file)

# Plot historical age-specific HepB incidence
import matplotlib.pyplot as plt

age_order = [
    "0–19 years",
    "20–29 years",
    "30–39 years",
    "40–49 years",
    "50–59 years",
    "≥60 years"
]

plt.figure(figsize=(11, 6))

for age_group in age_order:
    subset = combined[combined["age_group"] == age_group]
    plt.plot(subset["year"], subset["acute_hepb_rate"], marker="o", markersize=3, linewidth=1.8, label=age_group)

plt.title("Acute Hepatitis B Incidence by Age Group, US (2003–2023)")
plt.xlabel("Year")
plt.ylabel("Reported cases per 100,000 population")
plt.xticks(range(2003, 2024, 2))
plt.legend(title="Age group")
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(FIGS / "HepB_AgeSpecific_Incidence_Trends.png", dpi=300)
plt.show()

# Quantify incidence changes by age group (generate absolute and percent change from 2003 to 2023)
baseline = combined[combined["year"] == 2003][["age_group", "acute_hepb_rate"]].rename(columns={"acute_hepb_rate": "rate_2003"})

endpoint = combined[combined["year"] == 2023][["age_group", "acute_hepb_rate"]].rename(columns={"acute_hepb_rate": "rate_2023"})

changes = baseline.merge(endpoint, on="age_group")

changes["absolute_change"] = (changes["rate_2023"] - changes["rate_2003"])

changes["percent_change"] = (changes["absolute_change"] / changes["rate_2003"]) * 100

print("\nIncidence Changes, 2003–2023:")
print(changes.round(2).to_string(index=False))

# Identify highest-incidence age group each year to investigate hypothesis of increased childhood vaccination may contribute to lower incidence as children age into adulthood
peak_age = combined.loc[combined.groupby("year")["acute_hepb_rate"].idxmax(), ["year", "age_group", "acute_hepb_rate"]].sort_values("year")

print("\nHighest-Incidence Age Group by Year:")
print(peak_age.to_string(index=False))

print("\nNumber of Years Each Age Group Had Highest Incidence:")
print(peak_age["age_group"].value_counts())

# Compare incidence across three (seven year) historical periods
import numpy as np

combined["period"] = pd.cut(combined["year"], bins=[2002, 2009, 2016, 2023], labels=["2003–2009", "2010–2016", "2017–2023"])

period_summary = (combined.groupby(["age_group", "period"], observed=True)["acute_hepb_rate"].mean().unstack().reindex(age_order))

period_summary["percent_change"] = ((period_summary["2017–2023"] - period_summary["2003–2009"]) / period_summary["2003–2009"]) * 100

print("\nMean Incidence by Age Group and Period:")
print(period_summary.round(2).to_string())

# Spearman trend analysis by age group
from scipy.stats import spearmanr

trend_results = []

for age_group in age_order:
    subset = combined[combined["age_group"] == age_group].sort_values("year")
    rho, p_value = spearmanr(subset["year"],subset["acute_hepb_rate"])
    trend_results.append({"age_group": age_group, "n_years": len(subset), "spearman_rho": rho, "p_value": p_value})

trend_results = pd.DataFrame(trend_results)

print("\nSpearman Temporal Trend Results (2003–2023):")
print(trend_results.round(4).to_string(index=False))

# Calculate annual incidence changes by age group (linear regression slope)
from scipy.stats import linregress

slope_results = []

for age_group in age_order:
    subset = combined[combined["age_group"] == age_group].sort_values("year")
    result = linregress(subset["year"], subset["acute_hepb_rate"])
    slope_results.append({"age_group": age_group, "annual_slope": result.slope, "r_squared": result.rvalue ** 2, "p_value": result.pvalue})

slope_results = pd.DataFrame(slope_results)

print("\nAnnual Incidence Trends (2003–2023):")
print(slope_results.round(4).to_string(index=False))

# Approximate birth-year ranges to match age group

age_ranges = {"0–19 years": (0, 19), "20–29 years": (20, 29), "30–39 years": (30, 39), "40–49 years": (40, 49), "50–59 years": (50, 59)}

cohort_rows = []

for year in [2003, 2013, 2023]:
    for age_group, (min_age, max_age) in age_ranges.items():
        cohort_rows.append({"year": year, "age_group": age_group, "earliest_birth_year": year - max_age, "latest_birth_year": year - min_age})

cohort_summary = pd.DataFrame(cohort_rows)

print("\nApproximate Birth Cohorts by Age Group:")
print(cohort_summary.to_string(index=False))

# Calculate birth-year representation after 1991 (US universal infant HepB vaccination recommendation)
cohort_summary["total_birth_years"] = (cohort_summary["latest_birth_year"] - cohort_summary["earliest_birth_year"] + 1)
cohort_summary["post_1991_birth_years"] = (cohort_summary["latest_birth_year"] - cohort_summary["earliest_birth_year"].clip(lower=1991) + 1).clip(lower=0)
cohort_summary["post_1991_percent"] = (cohort_summary["post_1991_birth_years"] / cohort_summary["total_birth_years"] * 100)

print("\nBirth-Year Representation, 1991 Onward:")
print(cohort_summary[["year", "age_group", "post_1991_percent"]].round(1).to_string(index=False))
