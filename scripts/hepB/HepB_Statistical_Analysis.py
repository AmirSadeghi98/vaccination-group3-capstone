# HepB Statistical Analysis
# Two-way fixed-effects regression

import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path

# Load harmonized dataset
hepb = pd.read_csv(Path(__file__).resolve().parents[2] / "data" / "hepB" / "cleaned" / "HepB_Harmonized_Data.csv")

# Select lag0 observations
lag0 = hepb[hepb["lag"] == 0].copy()

# Remove observations with missing model variables
model_data = lag0.dropna(subset=["hepb_3dose_pct", "acute_hepb_rate"]).copy()

# Fit regression with state and year fixed effects
model = smf.ols(formula="acute_hepb_rate ~ hepb_3dose_pct + C(state) + C(incidence_year)",data=model_data
).fit(
cov_type="cluster", cov_kwds={"groups": model_data["state"]})

# Display regression results
print("\nLag-0 Two-Way Fixed-Effects Regression:")
print("Observations:", int(model.nobs))

print("\nVaccination Coverage Coefficient:")
print(model.params["hepb_3dose_pct"])

print("\nP-value:")
print(model.pvalues["hepb_3dose_pct"])

print("\n95% Confidence Interval:")
print(model.conf_int().loc["hepb_3dose_pct"])

# Compare two-way fixed-effects models across lags
common_data = hepb[hepb["coverage_birth_year"].between(2011, 2021)].copy()

regression_results = []

for lag in [0, 1, 2]:
    lag_data = common_data[common_data["lag"] == lag].dropna(subset=["hepb_3dose_pct", "acute_hepb_rate"]).copy()
    lag_model = smf.ols(formula="acute_hepb_rate ~ hepb_3dose_pct + C(state) + C(incidence_year)", data=lag_data
    ).fit(
    cov_type="cluster", cov_kwds={"groups": lag_data["state"]})

    regression_results.append({"lag": lag, "observations": int(lag_model.nobs), "coefficient": lag_model.params["hepb_3dose_pct"], "p_value": lag_model.pvalues["hepb_3dose_pct"],
        "ci_lower": lag_model.conf_int().loc["hepb_3dose_pct", 0], "ci_upper": lag_model.conf_int().loc["hepb_3dose_pct", 1]})

regression_results = pd.DataFrame(regression_results)

print("\nTwo-Way Fixed-Effects Regression Across Lags:")
print(regression_results.round(4).to_string(index=False))

# Run sensitivity analysis excluding WV
sensitivity_results = []

for lag in [0, 1, 2]:
    lag_data = common_data[(common_data["lag"] == lag) & (common_data["state"] != "West Virginia")
    ].dropna(
    subset=["hepb_3dose_pct", "acute_hepb_rate"]).copy()

    sensitivity_model = smf.ols(formula="acute_hepb_rate ~ hepb_3dose_pct + C(state) + C(incidence_year)", data=lag_data
    ).fit(
    cov_type="cluster", cov_kwds={"groups": lag_data["state"]})

    sensitivity_results.append({"lag": lag, "observations": int(sensitivity_model.nobs), "coefficient": sensitivity_model.params["hepb_3dose_pct"],
        "p_value": sensitivity_model.pvalues["hepb_3dose_pct"], "ci_lower": sensitivity_model.conf_int().loc["hepb_3dose_pct", 0],
            "ci_upper": sensitivity_model.conf_int().loc["hepb_3dose_pct", 1]})

sensitivity_results = pd.DataFrame(sensitivity_results)

print("\nFixed-Effects Sensitivity Analysis (Excluding West Virginia):")
print(sensitivity_results.round(4).to_string(index=False))

# Save fixed-effects regression results
output_folder = Path(__file__).resolve().parents[2] / "data" / "hepB" / "analysis"
output_folder.mkdir(parents=True, exist_ok=True)

# Save full-sample lag-0 regression
lag0_results = pd.DataFrame([{"lag": 0, "observations": int(model.nobs), "coefficient": model.params["hepb_3dose_pct"], "p_value": model.pvalues["hepb_3dose_pct"],
    "ci_lower": model.conf_int().loc["hepb_3dose_pct", 0], "ci_upper": model.conf_int().loc["hepb_3dose_pct", 1]}])

lag0_results.to_csv(output_folder / "HepB_FixedEffects_Lag0_FullSample.csv", index=False)

# Save common-cohort lag comparison
regression_results.to_csv(output_folder / "HepB_FixedEffects_Results.csv", index=False)

# Save sensitivity analysis excluding West Virginia
sensitivity_results.to_csv(output_folder / "HepB_FixedEffects_Sensitivity.csv", index=False)