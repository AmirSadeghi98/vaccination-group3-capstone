import pandas as pd

# Load/import raw CDC CHildVaxView dataset
df = pd.read_csv("Vaccination_Coverage_among_Young_Children_(0-35_Months)_20260924.csv")

print(df.shape)
print(df.columns)

# Define 50 US states
states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California",
    "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
    "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

# Individual birth years available in the dataset
birth_years = [str(year) for year in range(2011, 2023)]

# Filter full dataset to HepB data needed for project
hepb = df[
    (df["Vaccine"] == "Hep B") &
    (df["Dose"] == "≥3 Doses") &
    (df["Geography Type"] == "States/Local Areas") &
    (df["Geography"].isin(states)) &
    (df["Birth Year/Birth Cohort"].astype(str).isin(birth_years)) &
    (df["Dimension Type"] == "Age") &
    (df["Dimension"] == "24 Months")].copy()

print("\nFiltered HepB dataset shape:")
print(hepb.shape)

# Validation of filtered dataset
print("\nObservations per birth year:")
print(hepb["Birth Year/Birth Cohort"].value_counts().sort_index())

print("\nNumber of unique states:")
print(hepb["Geography"].nunique())

print("\nMissing coverage estimates:")
print(hepb["Estimate (%)"].isna().sum())

print("\nDuplicate state/birth-year combinations:")
print(
    hepb.duplicated(
        subset=["Geography", "Birth Year/Birth Cohort"]
    ).sum()
)

print("\nFirst 10 rows:")
print(hepb.head(10))

# Create/format clean analysis dataset for export
hepb_clean = hepb.rename(columns={
    "Geography": "state",
    "Birth Year/Birth Cohort": "birth_year",
    "Estimate (%)": "hepb_3dose_pct",
    "95% CI (%)": "coverage_95ci",
    "Sample Size": "sample_size"}).copy()

# Keep columns needed for analysis only
hepb_clean = hepb_clean[
    [
        "state",
        "birth_year",
        "hepb_3dose_pct",
        "coverage_95ci",
        "sample_size"
    ]
].copy()

# Convert birth year to numeric
hepb_clean["birth_year"] = hepb_clean["birth_year"].astype(int)

# Sort by state and birth year
hepb_clean = hepb_clean.sort_values(["state", "birth_year"]).reset_index(drop=True)

print("\nClean HepB dataset:")
print(hepb_clean.head(15))

print("\nData types:")
print(hepb_clean.dtypes)

print("\nFinal shape:")
print(hepb_clean.shape)

# Save cleaned HepB vaccinate coverage dataset to CSV
hepb_clean.to_csv("HepB_Vaccination_Coverage_Clean.csv", index=False)