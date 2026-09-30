import pandas as pd

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

# Access CDC 2015 Viral Hepatitis Surveillance webpage
url_2015 = "https://archive.cdc.gov/www_cdc_gov/hepatitis/statistics/2015surveillance/index.htm"

# Read all HTML tables from the CDC page
tables = pd.read_html(url_2015)

# Extract CDC Table 3.1: Acute hepatitis B cases and rates by state, 2011-2015
hepb_2011_2015 = tables[5].copy()

# Reshape CDC Table 3.1 from wide format to state-year format
rows = []

for _, row in hepb_2011_2015.iterrows():
    state = row[("State", "State")]

    # Keep only the 50 US states (remove DC and national total row)
    if state not in states:
        continue

    for year in range (2011, 2016):
        cases = row[(str(year), "No.")]
        rate = row[(str(year), "Rate*")]

        rows.append({"state": state, "year": year, "acute_hepb_cases": cases, "acute_hepb_rate": rate})

# Create new dataframe in state-year format
hepb_incidence_2011_2015 = pd.DataFrame(rows)

# Convert case counts and incidence rates to numeric values
# Unavailable values such as "U" become missing values (NaN)
hepb_incidence_2011_2015["acute_hepb_cases"] = pd.to_numeric(
    hepb_incidence_2011_2015["acute_hepb_cases"],
    errors="coerce"
)

hepb_incidence_2011_2015["acute_hepb_rate"] = pd.to_numeric(
    hepb_incidence_2011_2015["acute_hepb_rate"],
    errors="coerce"
)

# Sort the dataset by state and year
hepb_incidence_2011_2015 = hepb_incidence_2011_2015.sort_values(
    ["state", "year"]
).reset_index(drop=True)

# Validate the cleaned 2011-2015 dataset
print("\nClean 2011-2015 acute HepB incidence data:")
print(hepb_incidence_2011_2015.head(15))

print("\nShape:")
print(hepb_incidence_2011_2015.shape)

print("\nNumber of unique states:")
print(hepb_incidence_2011_2015["state"].nunique())

print("\nObservations per year:")
print(
    hepb_incidence_2011_2015["year"]
    .value_counts()
    .sort_index()
)

print("\nMissing case values:")
print(
    hepb_incidence_2011_2015["acute_hepb_cases"]
    .isna()
    .sum()
)

print("\nMissing rate values:")
print(
    hepb_incidence_2011_2015["acute_hepb_rate"]
    .isna()
    .sum()
)

print("\nDuplicate state/year combinations:")
print(
    hepb_incidence_2011_2015.duplicated(
        subset=["state", "year"]
    ).sum()
)

# Access CDC 2018 Viral Hepatitis Surveillance
url_2018 = "https://archive.cdc.gov/www_cdc_gov/hepatitis/statistics/2018surveillance/HepB.htm"

# Read all HTML tables from the CDC page
tables_2018 = pd.read_html(url_2018)

# Extract CDC Table 2.1: Acute hepatitis B cases and rates by state, 2014-2018
hepb_2014_2018 = tables_2018[1].copy()

# Reshape CDC Table 2.1 from wide format to state-year format
rows_2018 = []

for _, row in hepb_2014_2018.iterrows():
    state = row["State"]

    # Keep only the 50 US states (remove DC and national total row)
    if state not in states:
        continue

    for year in range(2014, 2019):
        cases = row[f"{year} No."]
        rate = row[f"{year} Rate*"]

        rows_2018.append({
            "state": state,
            "year": year,
            "acute_hepb_cases": cases,
            "acute_hepb_rate": rate
        })

hepb_incidence_2014_2018 = pd.DataFrame(rows_2018)

# CDC uses "—" to indicate no reported cases
# Convert these to zero before converting columns to numeric
hepb_incidence_2014_2018["acute_hepb_cases"] = (
    hepb_incidence_2014_2018["acute_hepb_cases"].replace("—", 0)
)

hepb_incidence_2014_2018["acute_hepb_rate"] = (
    hepb_incidence_2014_2018["acute_hepb_rate"].replace("—", 0.0)
)

# Convert values to numeric
# "U" (unavailable) and "N" (not reportable) become NaN
hepb_incidence_2014_2018["acute_hepb_cases"] = pd.to_numeric(
    hepb_incidence_2014_2018["acute_hepb_cases"],
    errors="coerce"
)

hepb_incidence_2014_2018["acute_hepb_rate"] = pd.to_numeric(
    hepb_incidence_2014_2018["acute_hepb_rate"],
    errors="coerce"
)

# Sort by state and year
hepb_incidence_2014_2018 = hepb_incidence_2014_2018.sort_values(
    ["state", "year"]
).reset_index(drop=True)

# Check that the overlapping 2014-2015 values agree with the first CDC dataset
old_overlap = hepb_incidence_2011_2015[
    hepb_incidence_2011_2015["year"].isin([2014, 2015])
]

new_overlap = hepb_incidence_2014_2018[
    hepb_incidence_2014_2018["year"].isin([2014, 2015])
]

overlap_check = old_overlap.merge(
    new_overlap,
    on=["state", "year"],
    suffixes=("_2015_report", "_2018_report")
)

case_matches = (
    overlap_check["acute_hepb_cases_2015_report"]
    .fillna(-1)
    .eq(overlap_check["acute_hepb_cases_2018_report"].fillna(-1))
)

rate_matches = (
    overlap_check["acute_hepb_rate_2015_report"]
    .fillna(-1)
    .eq(overlap_check["acute_hepb_rate_2018_report"].fillna(-1))
)

print("\n2014-2015 overlap check:")
print("Case values matching:", case_matches.sum(), "of", len(overlap_check))
print("Rate values matching:", rate_matches.sum(), "of", len(overlap_check))

# Show differences (if any) between the overlapping 2014-2015 data
differences = overlap_check[
    ~(case_matches & rate_matches)
]

print("\n2014-2015 overlap differences:")
print(differences.to_string(index=False))

# Keep only the "new" years 2016-2018
hepb_incidence_2016_2018 = hepb_incidence_2014_2018[
    hepb_incidence_2014_2018["year"].isin([2016, 2017, 2018])
].copy()

print("\nClean 2016-2018 acute HepB incidence data:")
print(hepb_incidence_2016_2018.head(15))

print("\nShape:")
print(hepb_incidence_2016_2018.shape)

print("\nNumber of unique states:")
print(hepb_incidence_2016_2018["state"].nunique())

print("\nObservations per year:")
print(
    hepb_incidence_2016_2018["year"]
    .value_counts()
    .sort_index()
)

print("\nMissing case values:")
print(hepb_incidence_2016_2018["acute_hepb_cases"].isna().sum())

print("\nMissing rate values:")
print(hepb_incidence_2016_2018["acute_hepb_rate"].isna().sum())

print("\nDuplicate state/year combinations:")
print(
    hepb_incidence_2016_2018.duplicated(
        subset=["state", "year"]
    ).sum()
)

# Load/Import CDC 2023 Viral Hepatitis Surveillance table 
file_2023 = "table-2.1.xlsx"

# Read CDC Table 2.1
hepb_2019_2023 = pd.read_excel(
    file_2023,
    sheet_name="Tab2.1",
    header=None
)

# Reshape CDC Table 2.1 from wide format to state-year format
rows_2023 = []

for _, row in hepb_2019_2023.iterrows():
    state = str(row[1]).strip()

    # Keep only the 50 US states (remove DC and national total row)
    if state not in states:
        continue

    # Extract case counts and rates for each year
    for year, cases_col, rate_col in [
        (2019, 2, 3),
        (2020, 4, 5),
        (2021, 6, 7),
        (2022, 8, 9),
        (2023, 10, 11)
    ]:
        cases = str(row[cases_col]).strip()
        rate = str(row[rate_col]).strip()

        rows_2023.append({
            "state": state,
            "year": year,
            "acute_hepb_cases": cases,
            "acute_hepb_rate": rate
        })

# Create state-year dataframe
hepb_incidence_2019_2023 = pd.DataFrame(rows_2023)

# CDC uses "—" to indicate no reported cases
# Convert these to zero before converting columns to numeric
hepb_incidence_2019_2023["acute_hepb_cases"] = (
    hepb_incidence_2019_2023["acute_hepb_cases"].replace("—", 0)
)

hepb_incidence_2019_2023["acute_hepb_rate"] = (
    hepb_incidence_2019_2023["acute_hepb_rate"].replace("—", 0.0)
)

# Convert values to numeric
# "U" (unavailable) and other non-numeric codes become NaN
hepb_incidence_2019_2023["acute_hepb_cases"] = pd.to_numeric(
    hepb_incidence_2019_2023["acute_hepb_cases"],
    errors="coerce"
)

hepb_incidence_2019_2023["acute_hepb_rate"] = pd.to_numeric(
    hepb_incidence_2019_2023["acute_hepb_rate"],
    errors="coerce"
)

# Sort by state and year
hepb_incidence_2019_2023 = hepb_incidence_2019_2023.sort_values(
    ["state", "year"]
).reset_index(drop=True)

# Validate the cleaned 2019-2023 dataset
print("\nClean 2019-2023 acute HepB incidence data:")
print(hepb_incidence_2019_2023.head(15))

print("\nShape:")
print(hepb_incidence_2019_2023.shape)

print("\nNumber of unique states:")
print(hepb_incidence_2019_2023["state"].nunique())

print("\nObservations per year:")
print(
    hepb_incidence_2019_2023["year"]
    .value_counts()
    .sort_index()
)

print("\nMissing case values:")
print(
    hepb_incidence_2019_2023["acute_hepb_cases"]
    .isna()
    .sum()
)

print("\nMissing rate values:")
print(
    hepb_incidence_2019_2023["acute_hepb_rate"]
    .isna()
    .sum()
)

print("\nDuplicate state/year combinations:")
print(
    hepb_incidence_2019_2023.duplicated(
        subset=["state", "year"]
    ).sum()
)

# ------------------------------
# Combine all acute HepB incidence datasets from 2011-2023 into one dataset
# ------------------------------

hepb_incidence = pd.concat([
    hepb_incidence_2011_2015,
    hepb_incidence_2016_2018,
    hepb_incidence_2019_2023
], ignore_index=True)

# Sort by state and year
hepb_incidence = hepb_incidence.sort_values(
    ["state", "year"]
).reset_index(drop=True)

# Final validation
print("\nFINAL 2011-2023 ACUTE HEPB INCIDENCE DATASET")
print(hepb_incidence.head(15))

print("\nShape:")
print(hepb_incidence.shape)

print("\nNumber of unique states:")
print(hepb_incidence["state"].nunique())

print("\nYear range:")
print(
    hepb_incidence["year"].min(),
    "to",
    hepb_incidence["year"].max()
)

print("\nObservations per year:")
print(
    hepb_incidence["year"]
    .value_counts()
    .sort_index()
)

print("\nMissing case values:")
print(
    hepb_incidence["acute_hepb_cases"]
    .isna()
    .sum()
)

print("\nMissing rate values:")
print(
    hepb_incidence["acute_hepb_rate"]
    .isna()
    .sum()
)

print("\nDuplicate state/year combinations:")
print(
    hepb_incidence.duplicated(
        subset=["state", "year"]
    ).sum()
)

# Save final cleaned dataset
hepb_incidence.to_csv(
    "HepB_Acute_Incidence_Clean.csv",
    index=False
)