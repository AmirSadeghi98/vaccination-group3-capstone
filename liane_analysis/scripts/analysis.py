"""
analysis.py

WHAT IT DOES?
Asks: Is there a correlation between vaccination coverage and disease rates?
Follows the three analysis steps:
    1. BASIC CORRELATION: vaccine coverage vs disease rate, all states and years pooled
    2. FIXED EFFECTS: compare each state with itself over time, and each year with itself
        - removes anything constant within a state
    3. TIME LAGS: coverage in year X vs disease in year X+1, X+2, X+3, and the reverse
        - disease in year X vs coverage later, to see whether outbreaks raise vaccination
    4. POISSON REGRESSION: the standard model for case counts
        - gives a rate ration per +10 points of coverage, with a confidence interval
    5. CONTROLS
        - NEGATIVE: salmonellosis. vaccines cannot affect it, so any association it shows is false signal
        - POSTIVE: measles before and after the 1963 vaccine. Real effects should show up in the data
    6. ROBUSTNESS: coverage matched to disease by  birth year vs by birth year + age
        - uses childvaxview data only

All results come with 95% confidence intervals. Disease and coverage are compared at STATE and YEAR level

HOW TO RUN (from the repository folder)
    python scripts/cleaning_data.py     (create first to create cleaned data)
    python scripts/analysis.py

WHAT IT WRITES
    results/correlation_summary.csv, lag_correlations.csv, positive_control_measles.csv, offset_comparison.csv
    figures/fig1 to fig8

NEEDS: pandas, numpy, scipy, matplotlib, statsmodels
"""
from pathlib import Path                                    # finds folders and files
import numpy as np                                          # math tool
import pandas as pd                                         # tables
from scipy.stats import spearmanr, pearsonr, kendalltau     # correlation methods
import statsmodels.api as sm                                # used for the Poisson regression
import matplotlib.pyplot as plt                             # plotting

# ======================================================================================================================
# PART A. SETTINGS - change things here
# ======================================================================================================================
ROOT = Path(__file__).resolve().parents[1]           # the repository folder
DATA = ROOT / "data" / "cleaned_data"                # where cleaning_data.py wrote its files
FIGS = ROOT / "figures"                              # figures folder where figures are saved
RESULTS = ROOT / "results"                           # results folder where tables are saved
FIGS.mkdir(exist_ok=True)                            # creates the FIGS folder
RESULTS.mkdir(exist_ok=True)                         # creates RESULTS folder

FIRST_YEAR = 1995        # first year of NIS coverage data
MAX_LAG = 3              # how many years to look ahead in the lag analysis
N_BOOTSTRAP = 1000       # how many times to resample states for each confidence interval

# Each disease and the vaccine it is compared with
PAIRS = [("Measles", "MMR"), ("Mumps", "MMR"), ("Rubella", "MMR"),
         ("Hepatitis B (acute)", "HepB"),
         ("Salmonellosis", "MMR"), ("Salmonellosis", "HepB")]          # salmonellosis = negative control

MEASLES_VACCINE_YEAR = 1963       # year the measles vaccine was licensed (positive control)
BEFORE_YEARS = (1950, 1962)       # years compared BEFORE the vaccine
AFTER_YEARS = (1964, 1969)        # years compared AFTER (Tycho reporting gets sparse after about 1970)

OFFSET_TEST_AGE = "24 Months"     # age at which coverage was checked in the offset comparison (offset = 2 years)

BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#7a7a7a"     # colours used in every figure

# ======================================================================================================================
# PART B. FUNCTIONS
# ======================================================================================================================
# Print a progress message to see what the script is doing while it runs
def say(text):
    print(text)

# label for a disease-vaccine pair, used in figures
def label(disease, vaccine):
    return f"{disease.split(' (')[0]} ~ {vaccine}" + ("  (control)" if disease == "Salmonellosis" else "")

# Returns only the rows for one disease and its vaccine
def get_pair(df, disease, vaccine):
    return df[(df["Disease"] == disease) & (df["Vaccine"] == vaccine)].copy()

# FIXED EFFECTS: each state is compared with ITSELF over time
# For each column: subtract the state's own average.
def remove_fixed_effects(d, column):
    out = d[column] - d.groupby("State")[column].transform("mean")        # state's own average removed
    return out

# Resamples whole states (with replacement) many times and recomputes the Spearman correlation each time
# The middle 95% of those results is the confidence interval. If it includes 0, there is no clear relationship.
def bootstrap_interval(d, x, y):
    rng = np.random.default_rng(1)                                        # fixed seed so results are repeatable
    states = [(g[x].to_numpy(), g[y].to_numpy()) for _, g in d.groupby("State")]
    values = []
    for i in range(N_BOOTSTRAP):
        picked = rng.choice(len(states), size=len(states), replace=True)  # draw 50 states, repeats allowed
        xs = np.concatenate([states[j][0] for j in picked])
        ys = np.concatenate([states[j][1] for j in picked])
        values.append(spearmanr(xs, ys)[0])
    return np.percentile(values, [2.5, 97.5])

# Lines up coverage in one year with the disease rate k years LATER in the same state
# k = 0 means the same year. Returns the paired values, ready for a correlation
def lag_pairs(d, x, y, k):
    later = d[["State", "Year", y]].copy()
    later["Year"] = later["Year"] - k                    # move the later year back, so it lines up with this year
    return d[["State", "Year", x]].merge(later, on=["State", "Year"]).dropna()

# POISSON REGRESSION with state fixed effects
# Predict the number of cases from vaccine coverage considering population
# Standard errors are clustered by state because the same state appears in many years
def fit_poisson(d):
    d = d.copy()
    d = d[d.groupby("State")["Cases"].transform("sum") > 0]   # a state with zero cases in every year cannot be fitted
    d = d.reset_index(drop=True)
    # One dummy for EVERY state (this acts as the intercept)
    X = pd.DataFrame({"coverage_per_10": d["Coverage"] / 10})
    X = pd.concat([X, pd.get_dummies(d["State"], dtype=float)], axis=1)
    model = sm.GLM(d["Cases"], X, family=sm.families.Poisson(), offset=np.log(d["Population"]))
    return model.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d["State"])[0]}, maxiter=200), d

# Returns the RATE RATIO per +10 points of coverage, with its 95% confidence interval and p-value
def poisson_rate_ratio(d):
    result, _ = fit_poisson(d)
    low, high = np.exp(result.conf_int().loc["coverage_per_10"])
    return np.exp(result.params["coverage_per_10"]), low, high, result.pvalues["coverage_per_10"]

# Puts clean, readable tick labels (0.25, 0.5, 1, 2, 4...) on a log-scale rate-ratio axis
def tidy_ratio_axis(ax):
    ax.set_xscale("log")                                 # ratios are symmetric on a log scale
    low, high = ax.get_xlim()                            # keep the range the data already needs
    ticks = [t for t in [0.1, 0.25, 0.5, 1, 2, 4, 8, 16, 32] if low <= t <= high]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t) for t in ticks])
    ax.set_xlim(low, high)
    ax.xaxis.set_minor_locator(plt.NullLocator())        # no extra minor ticks

# Keep ONE dose per vaccine so each state-year appears once: MMR with at least 1 dose, hepatitis B with at least 3
def one_dose_per_vaccine(df):
    keep = ((df["Vaccine"] == "MMR") & (df["Dose"] == "≥1 Dose")) | \
           ((df["Vaccine"] == "HepB") & (df["Dose"] == "≥3 Doses"))
    return df[keep].dropna(subset=["Coverage", "Rate_per_100k"])

# Stops the script if any state-year appears twice for a disease-vaccine pair (for example two doses kept by mistake)
def check_one_row_per_state_year(df, where):
    for disease, vaccine in PAIRS:
        duplicates = get_pair(df, disease, vaccine).duplicated(["State", "Year"]).sum()
        assert duplicates == 0, f"{where}, {disease}: {duplicates} state-years appear more than once"

# ======================================================================================================================
# PART C. EXECUTION
# ======================================================================================================================
#---STEP1: Load and keep one clean slice---
# Uses the no-offset file because NIS coverage is a survey-year estimate (nothing to offset)
df = pd.read_csv(DATA / "linked_state_year_no_offset.csv")
df = one_dose_per_vaccine(df[(df["Coverage_Source"] == "NIS") & (df["Year"] >= FIRST_YEAR)])
check_one_row_per_state_year(df, "NIS")
say(f"Step 1: {len(df):,} rows kept (NIS, {FIRST_YEAR}-{int(df['Year'].max())})")

#---STEP2: Baseline correlation (all states and years pooled) and fixed-effects correlation---
# Pooled: simple, but the shared time trend and permanent state differences can create false correlations
# Fixed effects: each state is compared with ITSELF over time (its own average is subtracted from both columns first)
say("Step 2: pooled and fixed-effects correlations")
summary = []
fe_data = {}                                            # keeps the cleaned columns for the lag step
for disease, vaccine in PAIRS:
    d = get_pair(df, disease, vaccine)
    d["Coverage_FE"] = remove_fixed_effects(d, "Coverage")
    d["Rate_FE"] = remove_fixed_effects(d, "Rate_per_100k")
    fe_data[(disease, vaccine)] = d
    low, high = bootstrap_interval(d, "Coverage_FE", "Rate_FE")
    summary.append({"Disease": disease, "Vaccine": vaccine, "N": len(d),
                    "Pooled_Pearson": pearsonr(d["Coverage"], d["Rate_per_100k"])[0],
                    "Pooled_Spearman": spearmanr(d["Coverage"], d["Rate_per_100k"])[0],
                    "FE_Spearman": spearmanr(d["Coverage_FE"], d["Rate_FE"])[0],
                    "FE_CI_low": low, "FE_CI_high": high})

#---STEP3: Time lags---
# FORWARD: coverage in year X vs disease in year X+k    -> did low coverage come before an outbreak?
# REVERSE: disease in year X vs coverage in year X+k    -> did an outbreak come before a rise in coverage?
# Uses the fixed-effects columns, so only within-state timing is compared (no shared trends)
say("Step 3: time lags")
lag_rows = []
for (disease, vaccine), d in fe_data.items():
    for direction, x, y, lags_to_try in [("coverage -> later disease", "Coverage_FE", "Rate_FE", range(0, MAX_LAG + 1)),
                                         ("disease -> later coverage", "Rate_FE", "Coverage_FE", range(1, MAX_LAG + 1))]:
        for k in lags_to_try:
            both = lag_pairs(d, x, y, k)                        # line the years up
            low, high = bootstrap_interval(both, x, y)
            lag_rows.append({"Disease": disease, "Vaccine": vaccine, "Direction": direction,
                             "Lag_years": k, "N": len(both), "Spearman": spearmanr(both[x], both[y])[0],
                             "CI_low": low, "CI_high": high})
lags = pd.DataFrame(lag_rows)
lags.round(3).to_csv(RESULTS / "lag_correlations.csv", index=False)

#---STEP4: Poisson regression (the main model)---
# One rate ratio per disease. Compare with the correlations: they should tell the same story.
say("Step 4: Poisson regression")
for row in summary:
    d = get_pair(df, row["Disease"], row["Vaccine"])
    rr, low, high, p = poisson_rate_ratio(d)
    row["RateRatio_per_10pts"], row["RR_CI_low"], row["RR_CI_high"], row["RR_p"] = rr, low, high, p

table = pd.DataFrame(summary).round(3)
table.to_csv(RESULTS / "correlation_summary.csv", index=False)
say(table[["Disease", "Vaccine", "Pooled_Spearman", "FE_Spearman", "FE_CI_low", "FE_CI_high",
           "RateRatio_per_10pts", "RR_CI_low", "RR_CI_high"]].to_string(index=False))

#---STEP5: Positive control: measles before and after the 1963 vaccine---
# Project Tycho has weekly measles counts back to 1950. Population is only available from 1993,
# so this uses national CASE COUNTS, not rates.
# If the vaccine works and the data are sound, cases should drop clearly after 1963.
say("Step 5: positive control (measles, 1963)")
inc = pd.read_csv(DATA / "incidence_state_year.csv")
tycho = inc[(inc["Disease"] == "Measles") & (inc["Source"] == "Project Tycho") & (inc["Year"] <= AFTER_YEARS[1])]
national = tycho.groupby("Year")["Cases"].sum(min_count=1)
before = national.loc[BEFORE_YEARS[0]:BEFORE_YEARS[1]]
after = national.loc[AFTER_YEARS[0]:AFTER_YEARS[1]]
change = (after.mean() - before.mean()) / before.mean() * 100
pd.DataFrame({"Period": [f"{BEFORE_YEARS[0]}-{BEFORE_YEARS[1]}", f"{AFTER_YEARS[0]}-{AFTER_YEARS[1]}"],
              "Mean_cases_per_year": [round(before.mean()), round(after.mean())],
              "Percent_change": [0, round(change, 1)]}).to_csv(RESULTS / "positive_control_measles.csv", index=False)

#---STEP6: Robustness: coverage matched to disease with and without the age offset (ChildVaxView only)---
# NIS is a survey-year estimate, so it has no birth year to offset. ChildVaxView does.
#   WITH offset:    coverage of children born in year B is matched to disease in year B + 2 (they are 24 months old)
#   WITHOUT offset: coverage of children born in year B is matched to disease in year B
# The two versions cover slightly different disease years, so both are cut down to the years they share.
say("Step 6: offset vs no offset")
versions = {"With offset (birth year + 2)": "linked_state_year_age_offsets.csv",
            "No offset (birth year)": "linked_state_year_no_offset.csv"}
cvv = {}
for name, file in versions.items():
    x = pd.read_csv(DATA / file)
    cvv[name] = one_dose_per_vaccine(x[(x["Coverage_Source"] == "ChildVaxView") & (x["Age"] == OFFSET_TEST_AGE)])
    check_one_row_per_state_year(cvv[name], name)
first = max(x["Year"].min() for x in cvv.values())      # keep only the years both versions have
last = min(x["Year"].max() for x in cvv.values())
offset_rows = []
for name, x in cvv.items():
    x = x[(x["Year"] >= first) & (x["Year"] <= last)]
    for disease, vaccine in PAIRS:
        d = get_pair(x, disease, vaccine)
        d["Coverage_FE"] = remove_fixed_effects(d, "Coverage")
        d["Rate_FE"] = remove_fixed_effects(d, "Rate_per_100k")
        low, high = bootstrap_interval(d, "Coverage_FE", "Rate_FE")
        rr, rr_low, rr_high, rr_p = poisson_rate_ratio(d)
        offset_rows.append({"Version": name, "Disease": disease, "Vaccine": vaccine, "N": len(d),
                            "FE_Spearman": spearmanr(d["Coverage_FE"], d["Rate_FE"])[0],
                            "FE_CI_low": low, "FE_CI_high": high,
                            "RateRatio_per_10pts": rr, "RR_CI_low": rr_low, "RR_CI_high": rr_high, "RR_p": rr_p})
offset_table = pd.DataFrame(offset_rows).round(3)
offset_table.to_csv(RESULTS / "offset_comparison.csv", index=False)
say(f"   disease years {first}-{last}")

#---STEP7: Figures---
# fig1   average state vaccination coverage over time
# fig2   national disease incidence over time
# fig3   every state-year: coverage against disease rate, with the pooled correlation
# fig4   pooled correlation vs fixed-effects correlation: what survives once confounding is removed
# fig5   time lags in both directions, fixed effects removed
# fig6   Poisson rate ratios (the main model)
# fig7   positive control: measles and the 1963 vaccine
# fig8   appendix: matching coverage to disease by birth year vs by age (offset vs no offset)

say("Step 7: figures")
main_pairs = PAIRS[:4]                                  # the four vaccine-preventable diseases
y = np.arange(len(table))[::-1]                         # vertical positions used by the dot plots

# Figure 1: average state coverage by year (each state counts equally)
# MMR rows are repeated for each disease, so keep one row per state, year and vaccine first
coverage_only = df.drop_duplicates(["State", "Year", "Vaccine"])
average_coverage = coverage_only.groupby(["Vaccine", "Year"])["Coverage"].mean().unstack(0)
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.plot(average_coverage.index, average_coverage["MMR"], marker="o", color=BLUE, label="MMR (1 or more doses)")
ax.plot(average_coverage.index, average_coverage["HepB"], marker="o", color=ORANGE, label="Hepatitis B (3 or more doses)")
ax.set_xlabel("Year"); ax.set_ylabel("Average state coverage (%)")
ax.set_title(f"Average state vaccination coverage, {FIRST_YEAR}-{int(df['Year'].max())}")
ax.grid(alpha=0.3); ax.legend()
plt.tight_layout(); plt.savefig(FIGS / "fig1_average_coverage.png", dpi=200); plt.close()

# Figure 2: national incidence by year, one panel per disease (national rate = total cases / total population)
fig, axes = plt.subplots(2, 2, figsize=(12, 7))
for ax, (disease, vaccine) in zip(axes.flat, main_pairs):
    d = get_pair(df, disease, vaccine)
    year_total = d.groupby("Year")[["Cases", "Population"]].sum()
    ax.plot(year_total.index, year_total["Cases"] / year_total["Population"] * 100_000, marker="o", color=BLUE)
    ax.set_title(f"US {disease.split(' (')[0]} incidence, {FIRST_YEAR}-{int(df['Year'].max())}", fontsize=11)
    ax.set_xlabel("Year"); ax.set_ylabel("Cases per 100,000"); ax.set_ylim(bottom=0)
    ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(FIGS / "fig2_national_incidence.png", dpi=200); plt.close()

# Figure 3: every state-year as one dot (one state in one year), coverage across, disease rate up
# The title of each panel gives the pooled correlations. Most dots sit at 0 because most states have no cases in most years.
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for ax, (disease, vaccine), row in zip(axes.flat, PAIRS, table.itertuples()):
    d = get_pair(df, disease, vaccine)
    ax.scatter(d["Coverage"], d["Rate_per_100k"], alpha=0.5, color=BLUE)
    ax.set_title(f"{vaccine} coverage vs {disease.split(' (')[0]} incidence" + ("  (control)" if disease == "Salmonellosis" else "") +
                 f"\nSpearman {row.Pooled_Spearman:.2f}, Pearson {row.Pooled_Pearson:.2f}  ({row.N:,} state-years)", fontsize=10)
    ax.set_xlabel(f"{vaccine} coverage (%)"); ax.set_ylabel(f"{disease.split(' (')[0]} cases per 100,000")
    ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(FIGS / "fig3_coverage_vs_incidence.png", dpi=200); plt.close()

# Figure 4: for each pair, the pooled correlation (grey) and the fixed-effects correlation with its 95% interval (blue)
# Intervals that include 0 mean no clear relationship. Salmonellosis (control) should be near 0.
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.plot(table["Pooled_Spearman"], y + 0.12, "o", color=GRAY, label="Pooled (all states and years together)")
ax.errorbar(table["FE_Spearman"], y - 0.12, xerr=[table["FE_Spearman"] - table["FE_CI_low"], table["FE_CI_high"] - table["FE_Spearman"]],
            fmt="o", color=BLUE, capsize=3, label="Fixed effects (95% CI)")
ax.axvline(0, color="black", linewidth=0.8)
ax.set_yticks(y); ax.set_yticklabels([label(d, v) for d, v in PAIRS])
ax.set_xlabel("Spearman correlation between coverage and disease rate")
ax.set_title("Pooled vs fixed-effects correlation")
ax.legend(fontsize=8, loc="lower left")
plt.tight_layout(); plt.savefig(FIGS / "fig4_pooled_vs_fixed_effects.png", dpi=200); plt.close()

# Figure 5: lag correlations with 95% intervals (fixed effects removed)
# TOP row: coverage, then later disease.  BOTTOM row: disease, then later coverage.  One column per disease.
fig, axes = plt.subplots(2, len(PAIRS), figsize=(18, 6), sharey=True)
for col, (disease, vaccine) in enumerate(PAIRS):
    for row_i, (direction, color) in enumerate([("coverage -> later disease", BLUE), ("disease -> later coverage", ORANGE)]):
        g = lags[(lags["Disease"] == disease) & (lags["Vaccine"] == vaccine) & (lags["Direction"] == direction)]
        ax = axes[row_i, col]
        ax.errorbar(g["Lag_years"], g["Spearman"], yerr=[g["Spearman"] - g["CI_low"], g["CI_high"] - g["Spearman"]],
                    fmt="o-", color=color, capsize=3)
        ax.axhline(0, color="black", linewidth=0.8)             # no correlation
        ax.set_xticks(range(0, MAX_LAG + 1)); ax.set_xlim(-0.4, MAX_LAG + 0.4)
        if row_i == 0:
            ax.set_title(label(disease, vaccine), fontsize=10)
        if row_i == 1:
            ax.set_xlabel("Lag (years)")
axes[0, 0].set_ylabel("Coverage, then later disease\nSpearman (95% CI)")
axes[1, 0].set_ylabel("Disease, then later coverage\nSpearman (95% CI)")
fig.suptitle("Time lags (fixed effects removed)", fontsize=14)
plt.tight_layout(); plt.savefig(FIGS / "fig5_lags.png", dpi=200); plt.close()

# Figure 6: Poisson rate ratio for +10 points of coverage, with 95% interval
# The line at 1 means no effect. Below 1 = fewer cases with higher coverage. Intervals crossing 1 are not clear evidence.
fig, ax = plt.subplots(figsize=(8, 4.5))
for yi, r in zip(y, table.itertuples()):
    color = GRAY if r.Disease == "Salmonellosis" else BLUE
    ax.plot([r.RR_CI_low, r.RR_CI_high], [yi, yi], color=color, linewidth=2)
    ax.plot(r.RateRatio_per_10pts, yi, "o", color=color, markersize=7)
ax.axvline(1, color="black", linewidth=0.8)
tidy_ratio_axis(ax)
ax.set_yticks(y); ax.set_yticklabels([label(d, v) for d, v in PAIRS])
ax.set_xlabel("Rate ratio per +10 points of coverage\n(below 1 = fewer cases with higher coverage)")
ax.set_title("Poisson regression with state fixed effects")
plt.tight_layout(); plt.savefig(FIGS / "fig6_rate_ratios.png", dpi=200); plt.close()

# Figure 7: positive control. National measles cases before and after the 1963 vaccine
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.plot(national.index, national.values / 1000, color=BLUE, marker="o", markersize=3)
ax.axvline(MEASLES_VACCINE_YEAR, color=ORANGE, linestyle="--")
ax.text(MEASLES_VACCINE_YEAR + 0.3, ax.get_ylim()[1] * 0.93, "vaccine licensed 1963", color=ORANGE)
ax.hlines(before.mean() / 1000, BEFORE_YEARS[0], BEFORE_YEARS[1], color=GRAY, linewidth=2)
ax.hlines(after.mean() / 1000, AFTER_YEARS[0], AFTER_YEARS[1], color=GRAY, linewidth=2)
ax.text(MEASLES_VACCINE_YEAR + 0.3, 560,
        f"Mean {BEFORE_YEARS[0]}-{BEFORE_YEARS[1]}: {before.mean() / 1000:.0f}k a year\n"
        f"Mean {AFTER_YEARS[0]}-{AFTER_YEARS[1]}: {after.mean() / 1000:.0f}k a year ({change:.0f}%)")
ax.set_xticks(range(1950, 1970, 2))                      # whole years only
ax.set_xlabel("Year"); ax.set_ylabel("Reported measles cases (thousands)")
ax.set_title("Positive control: measles cases before and after the 1963 vaccine")
plt.tight_layout(); plt.savefig(FIGS / "fig7_positive_control_measles.png", dpi=200); plt.close()

# Figure 8 (appendix): Poisson rate ratio with and without the age offset (ChildVaxView, 24 months)
fig, ax = plt.subplots(figsize=(8, 4.8))
shift = {"With offset (birth year + 2)": 0.12, "No offset (birth year)": -0.12}      # nudges the two dots apart
for name, color in [("With offset (birth year + 2)", BLUE), ("No offset (birth year)", ORANGE)]:
    t = offset_table[offset_table["Version"] == name].reset_index(drop=True)
    ax.errorbar(t["RateRatio_per_10pts"], y + shift[name],
                xerr=[t["RateRatio_per_10pts"] - t["RR_CI_low"], t["RR_CI_high"] - t["RateRatio_per_10pts"]],
                fmt="o", color=color, capsize=3, label=name)
ax.axvline(1, color="black", linewidth=0.8)
tidy_ratio_axis(ax)
ax.set_yticks(y); ax.set_yticklabels([label(d, v) for d, v in PAIRS])
ax.set_xlabel("Rate ratio per +10 points of coverage (95% CI, log scale)")
ax.set_title(f"Appendix: matching by birth year or by age ({first}-{last})")
ax.legend(fontsize=8, loc="lower right")
plt.tight_layout(); plt.savefig(FIGS / "fig8_offset_vs_no_offset.png", dpi=200); plt.close()

say(f"Done. Tables in {RESULTS}, figures in {FIGS}")