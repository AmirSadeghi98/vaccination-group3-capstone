from pathlib import Path

# Folders (this file is in scripts/hepB/, so the repository folder is two levels up)
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "hepB" / "raw"
CLEAN = ROOT / "data" / "hepB" / "cleaned"
FIGS = ROOT / "documents" / "figures" / "hepB"
CLEAN.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

import pandas as pd

# Load harmonized HepB dataset
hepb = pd.read_csv(CLEAN / "HepB_Harmonized_Data.csv")

# Verify dataset structure
print("Dataset shape:", hepb.shape)
print("\nColumns:", hepb.columns.tolist())

# Inspect data types and missing values
print("\nData types:")
print(hepb.dtypes)

print("\nMissing values by column:")
print(hepb.isna().sum())

# Initial descriptive statistics
print("\nHepB Vaccination Coverage Statistics:")
print(hepb[hepb["lag"] == 0]["hepb_3dose_pct"].describe())

print("\nAcute HepB Incidence Rate Statistics:")
print(hepb[hepb["lag"] == 0]["acute_hepb_rate"].describe())

# Check for potentially unusual values
print("\nCoverage range:", hepb["hepb_3dose_pct"].min(), "to", hepb["hepb_3dose_pct"].max())

print("\nIncidence rate range:", hepb["acute_hepb_rate"].min(), "to", hepb["acute_hepb_rate"].max())

# Identify highest incidence observations (potential outliers from descriptive statistics)
lag0 = hepb[hepb["lag"] == 0].copy()

print("\nTop 10 highest acute HepB incidence rates:")
print(lag0.nlargest(10, "acute_hepb_rate")[["state", "incidence_year", "acute_hepb_rate", "hepb_3dose_pct"]].to_string(index=False))

print("\nNumber of observations with incidence rate > 5:")
print((lag0["acute_hepb_rate"] > 5).sum())

# Better visualize distributions
import matplotlib.pyplot as plt

# Vaccination coverage distribution
plt.figure(figsize=(8, 5))
plt.hist(lag0["hepb_3dose_pct"], bins=20, edgecolor="black")
plt.xlabel("HepB 3-Dose Vaccination Coverage (%)")
plt.ylabel("Number of Observations")
plt.title("Distribution of Childhood HepB Vaccination Coverage")
plt.tight_layout()
plt.show()

# Acute HepB incidence distribution
plt.figure(figsize=(8, 5))
plt.hist(lag0["acute_hepb_rate"].dropna(), bins=25, edgecolor="black")
plt.xlabel("Acute HepB Incidence (per 100,000)")
plt.ylabel("Number of Observations")
plt.title("Distribution of Acute HepB Incidence Rates")
plt.tight_layout()
plt.show()

# Rank states by average acute HepB incidence (to try and address WV outlier)

# Use lag 0 to avoid double counting incidence observations which are repeated
trend_data = lag0.copy()

# Calculate average incidence for each state for original 2011-2022 period
state_incidence = (trend_data.groupby("state")["acute_hepb_rate"].agg(["mean", "median", "max", "count"]).sort_values("mean", ascending=False))

print("\nTop 10 states by average acute HepB incidence:")
print(state_incidence.head(10).round(2))

print("\nBottom 5 states by average acute HepB incidence:")
print(state_incidence.tail(5).round(2))

# Visualize incidence trends in highest-incidence states of WV, KY, and TN

# Select top 3 states based on average incidence (WV, KY, TN)
top_states = state_incidence.head(3).index.tolist()

# Calculate annual median across all states
yearly_median = trend_data.groupby("incidence_year")["acute_hepb_rate"].median()

plt.figure(figsize=(10, 6))

# Plot top 3 states
for state in top_states:
    state_data = trend_data[trend_data["state"] == state].sort_values("incidence_year")
    plt.plot(state_data["incidence_year"], state_data["acute_hepb_rate"], marker="o", linewidth=2, label=state)

# Plot annual median across all states
plt.plot(yearly_median.index, yearly_median.values, linestyle="--", color="black", linewidth=2, label="Median across 50 states")

plt.xlabel("Year")
plt.ylabel("Acute HepB Incidence (per 100,000)")
plt.title("Acute HepB Incidence Trends (2011–2022)")
plt.xticks(range(2011, 2023))
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# Scatterplot of coverage vs incidence (lag 0)
# Omit observations with missing incidence rates
scatter_data = lag0.dropna(subset=["hepb_3dose_pct", "acute_hepb_rate"])

plt.figure(figsize=(9, 6))

plt.scatter(scatter_data["hepb_3dose_pct"], scatter_data["acute_hepb_rate"], alpha=0.5, s=35, color="teal", edgecolor="black")

plt.xlabel("HepB 3-Dose Vaccination Coverage (%)")
plt.ylabel("Acute HepB Incidence (per 100,000)")
plt.title("Childhood HepB Coverage vs Acute Incidence (Lag 0)")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

print("\nObservations included in scatterplot:", len(scatter_data))

# Calculate Pearson and Spearman correlations (lag 0)
pearson_r = scatter_data["hepb_3dose_pct"].corr(scatter_data["acute_hepb_rate"], method="pearson")

spearman_r = scatter_data["hepb_3dose_pct"].corr(scatter_data["acute_hepb_rate"], method="spearman")

print("\nLag-0 Correlation Results:")
print("Number of observations:", len(scatter_data))
print("Pearson correlation:", round(pearson_r, 4))
print("Spearman correlation:", round(spearman_r, 4))

# Sensitivity analysis - recalculate Pearson and Spearman correlations at (lag 0), excluding WV
scatter_no_wv = scatter_data[scatter_data["state"] != "West Virginia"].copy()

pearson_no_wv = scatter_no_wv["hepb_3dose_pct"].corr(scatter_no_wv["acute_hepb_rate"], method="pearson")

spearman_no_wv = scatter_no_wv["hepb_3dose_pct"].corr(scatter_no_wv["acute_hepb_rate"], method="spearman")

print("\nLag-0 Sensitivity Analysis:")
print("All states:")
print("  Pearson:", round(pearson_r, 4))
print("  Spearman:", round(spearman_r, 4))

print("\nExcluding West Virginia:")
print("  Observations:", len(scatter_no_wv))
print("  Pearson:", round(pearson_no_wv, 4))
print("  Spearman:", round(spearman_no_wv, 4))

# Compare correlations across lag times (0, 1, 2) to assess potential lagged effects
# Restrict to common birth cohort window
common_data = hepb[hepb["coverage_birth_year"].between(2011, 2021)].copy()

results = []

for lag in [0, 1, 2]:
    lag_data = common_data[common_data["lag"] == lag].dropna(subset=["hepb_3dose_pct", "acute_hepb_rate"])
    pearson = lag_data["hepb_3dose_pct"].corr(lag_data["acute_hepb_rate"], method="pearson")
    spearman = lag_data["hepb_3dose_pct"].corr(lag_data["acute_hepb_rate"], method="spearman")
    results.append({"lag": lag, "observations": len(lag_data), "pearson_r": pearson, "spearman_r": spearman})

correlation_results = pd.DataFrame(results)

print("\nCorrelations Across All Three Lags:")
print(correlation_results.round(4).to_string(index=False))

# Calculate annual changes within each state
within_state = lag0.sort_values(["state", "coverage_birth_year"]).copy()

within_state["coverage_change"] = (within_state.groupby("state")["hepb_3dose_pct"].diff())

within_state["incidence_change"] = (within_state.groupby("state")["acute_hepb_rate"].diff())

# Inspect results for Virginia (as example)
print("\nVirginia: Annual Changes in Coverage and Incidence")
print(within_state[within_state["state"] == "Virginia"][["coverage_birth_year", "hepb_3dose_pct", "coverage_change", "acute_hepb_rate", "incidence_change"]].to_string(index=False))

print("\nObservations with both annual changes available:")
print(within_state[["coverage_change", "incidence_change"]].dropna().shape[0])

# Calculate correlation of within-state annual changes
change_data = within_state.dropna(subset=["coverage_change", "incidence_change"]).copy()

# Calculate correlations
change_pearson = change_data["coverage_change"].corr(change_data["incidence_change"], method="pearson")

change_spearman = change_data["coverage_change"].corr(change_data["incidence_change"], method="spearman")

print("\nWithin-State Annual Change Correlations:")
print("Observations:", len(change_data))
print("Pearson:", round(change_pearson, 4))
print("Spearman:", round(change_spearman, 4))

# Calculate year-specific correlations across states @ Lag0
yearly_results = []

for year, year_data in lag0.groupby("incidence_year"):
    valid_data = year_data.dropna(subset=["hepb_3dose_pct", "acute_hepb_rate"])
    yearly_results.append({"year": year, "observations": len(valid_data), "pearson_r": valid_data["hepb_3dose_pct"].corr(valid_data["acute_hepb_rate"],method="pearson"),
        "spearman_r": valid_data["hepb_3dose_pct"].corr(valid_data["acute_hepb_rate"], method="spearman")})

yearly_correlations = pd.DataFrame(yearly_results)

print("\nYear-Specific Correlations (Lag 0):")
print(yearly_correlations.round(4).to_string(index=False))