import pandas as pd 

# Load cleaned HepB datasets 
coverage = pd.read_csv("HepB_Vaccination_Coverage_Clean.csv")
incidence = pd.read_csv("HepB_Acute_Incidence_Clean.csv")

# Check shape (dimensions + names of columns) of the datasets
print("Coverage shape:", coverage.shape)
print("Coverage columns:", coverage.columns.tolist())

print("\nIncidence shape:", incidence.shape)
print("Incidence columns:", incidence.columns.tolist())

# Validate states and year columns
print("\nCoverage states:", coverage["state"].nunique())
print("Incidence states:", incidence["state"].nunique())

print("\nStates only in coverage:", set(coverage["state"]) - set(incidence["state"]))

print("States only in incidence:", set(incidence["state"]) - set(coverage["state"]))

print("\nCoverage birth years:", coverage["birth_year"].min(), "to", coverage["birth_year"].max())

print("Incidence years:", incidence["year"].min(), "to", incidence["year"].max())

print("\nCoverage year datatype:", coverage["birth_year"].dtype)
print("Incidence year datatype:", incidence["year"].dtype)

# Create lag0 linkage
# Keep original birth year and create matching incidence year
coverage_lag0 = coverage.copy()
coverage_lag0["incidence_year"] = coverage_lag0["birth_year"]

# Merge coverage + incidence by state and year
hepb_lag0 = pd.merge(coverage_lag0, incidence, left_on=["state", "incidence_year"], right_on=["state", "year"], how="left", validate="one_to_one")

# Identify the lag specification
hepb_lag0["lag"] = 0

# Inspect results
print("\nLag-0 dataset shape:", hepb_lag0.shape)
print("\nFirst five observations:")
print(hepb_lag0.head().to_string(index=False))

print("\nMissing incidence rates:", hepb_lag0["acute_hepb_rate"].isna().sum())

# Create lag1 linkage
coverage_lag1 = coverage.copy()
coverage_lag1["incidence_year"] = coverage_lag1["birth_year"] + 1

hepb_lag1 = pd.merge(coverage_lag1, incidence, left_on=["state", "incidence_year"], right_on=["state", "year"], how="left", validate="one_to_one")

hepb_lag1["lag"] = 1

# Inspect results
print("\nLag-1 dataset shape:", hepb_lag1.shape)

print("\nFirst five lag-1 observations:")
print(hepb_lag1.head().to_string(index=False))

print("\nMissing incidence rates:", hepb_lag1["acute_hepb_rate"].isna().sum())

# Create lag2 linkage
coverage_lag2 = coverage[coverage["birth_year"] <= 2021].copy()

coverage_lag2["incidence_year"] = coverage_lag2["birth_year"] + 2

hepb_lag2 = pd.merge(coverage_lag2, incidence, left_on=["state", "incidence_year"], right_on=["state", "year"], how="left",  validate="one_to_one")

hepb_lag2["lag"] = 2

# Inspect results
print("\nLag-2 dataset shape:", hepb_lag2.shape)

print("\nFirst five lag-2 observations:")
print(hepb_lag2.head().to_string(index=False))

print("\nMissing incidence rates:", hepb_lag2["acute_hepb_rate"].isna().sum())

# Combine the three lag datasets
hepb_harmonized = pd.concat([hepb_lag0, hepb_lag1, hepb_lag2], ignore_index=True)

# Sort by state, birth year, and lag time
hepb_harmonized = hepb_harmonized.sort_values(["state", "birth_year", "lag"]).reset_index(drop=True)

# Inspect the combined dataset results
print("\nCombined dataset shape:", hepb_harmonized.shape)

print("\nObservations by lag:")
print(hepb_harmonized.groupby("lag").size())

print("\nMissing incidence rates by lag:")
print(hepb_harmonized.groupby("lag")["acute_hepb_rate"].apply(lambda x: x.isna().sum()))

print("\nDuplicate state/birth year/lag combinations:", hepb_harmonized.duplicated(subset=["state", "birth_year", "lag"]).sum())

# Finalize and complete harmonized dataset
hepb_harmonized = hepb_harmonized.drop(columns=["year"])

hepb_harmonized = hepb_harmonized.rename(columns={"birth_year": "coverage_birth_year"})

# Arrange columns in a more logical order
hepb_harmonized = hepb_harmonized[
    [
        "state",
        "coverage_birth_year",
        "incidence_year",
        "lag",
        "hepb_3dose_pct",
        "acute_hepb_cases",
        "acute_hepb_rate",
        "coverage_95ci",
        "sample_size"
    ]
]

# Verify the year alignment
assert (hepb_harmonized["incidence_year"] - hepb_harmonized["coverage_birth_year"] == hepb_harmonized["lag"]).all(), "Year alignment error detected!"

# Save the final dataset
hepb_harmonized.to_csv("HepB_Harmonized_Data.csv", index=False)

print("\nFinal harmonized dataset shape:", hepb_harmonized.shape)
print("\nFinal columns:", hepb_harmonized.columns.tolist())
print("\nYear alignment validation: PASSED")
print("Saved: HepB_Harmonized_Data.csv")