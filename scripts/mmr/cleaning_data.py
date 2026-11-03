"""
cleaning_data.py

WHAT IT DOES?
1. Reads the raw disease-count files and turns each into a table with one row per state per year: State | Year | Disease | Cases
2. Reads the vaccination-coverage filess into a table with one row per state per year: State | Year | Disease | Coverage
3. Divides cases by population to get a rate per 100,000 people
4. Joins disease and coverage together by State + Year (+ vaccine) so they can be analyzed

HOW TO RUN (from the repository folder)
    python scripts/mmr/cleaning_data.py

HOW TO READ THIS FILE
    Read it top to bottom. Part A holds the settings you may want to change. 
    Part B is a set of small helper functions, each doing one job.
    Part C runs the steps in order
    Every rule in the cleaning is written next to the code that does it.

NEEDS: pandas, numpy, openpxl   (pip install pandas numpy openpyxl)
"""

from pathlib import Path    # Path tool used to find folders and files
import numpy as np          # numpy is a math tool to mark numbers as missing
import pandas as pd         # pandas is a tool that is used for data manipulation, analysis, amd cleaning

# ======================================================================================================================
# PART A. SETTINGS - change things here
# ======================================================================================================================
ROOT = Path(__file__).resolve().parents[2]              # the repository folder (this file is in scripts/mmr/)
RAW = ROOT / "data" / "mmr" / "raw"                             # enters "raw" folder
OUT = ROOT / "data" / "mmr" / "cleaned"                    # where the results are written

# ChildVaxView reports each estimate by the child's BIRTH YEAR, plus the age at which vaccination was checked (for example "24 months").
# A child born in 2015 is 24 months old in about 2017.
# To compare coverage with disease in the same calendar year, we ADD an offset (in years) to the birth year: Year = Birth_Year + offset.
#
# The offset depends on the age: roughly age in months / 12, rounded to the nearest whole year.
# A child born mid year is 13 months old about 1 year later, 24 months old about 2 years later.
# Birth-dose records (age in days) and ages up to 5 months get 0, because vaccination occurs in the birth year
# Change any number as needed
# Note that 7 months rounds to 1 year
AGE_OFFSET_YEARS = {"0-1 Days": 0, "0-2 Days": 0, "0-3 Days": 0,
                    "3 Months": 0, "5 Months": 0, "7 Months": 1,
                    "13 Months": 1, "19 Months": 2, "24 Months": 2, "35 Months": 3}

# Two versions are saved: coverage matched to disease by the offset year and by the plain birth year.
# NIS rows are survey-year estimates so they are never offset

# Includes only 50 US States.
STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
          "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
          "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
          "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
          "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
          "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
          "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
          "Wisconsin", "Wyoming"]

# Combine New York because it is reported in pieces in some files
NEW_YORK_PARTS = ["New York (upstate)", "New York (Upstate)", "New York City",
                  "New York (excluding New York City)"]

# Which NNDSS file belongs to which disease
# Change file name as necessary if downloading file from source
NNDSS_FILES = {"Measles": "NNDSS_2016-2023_Measles.xls",
               "Mumps": "NNDSS_2016-2023_Mumps.xls",
               "Rubella": "NNDSS_2016-2023_Rubella.xls",
               "Hepatitis B (acute)": "NNDSS_2016-2023_Hepatitis_B.xls",
               # salmonellosis needed three downloads because CDC renamed the disease in 2018
               "Salmonellosis": ["NNDSS_2016-2017_Salmonellosis.xls",
                                 "NNDSS_2018_Salmonellosis.xls",
                                 "NNDSS_2019-2023_Salmonellosis.xls"]}

# ======================================================================================================================
# PART B. FUNCTIONS - purpose is to clean each dataset
# ======================================================================================================================
# Print a progress message to see what the script is doing while it runs
def say (text):
    print(text)

# Ensures every source results in 50 states
# Combines rows that are reported in pireces into one row
# Drops all other rows that is not associated with one of the 50 states
# creates a copy where changes are made while original copy is untouched
def fix_names_and_merge(df):
    df = df.copy()                     
    df["State"] = df["State"].astype(str).str.strip()

    # Combine pieces of New York
    # Groups column depeding on data type
    is_ny = df["State"].isin(NEW_YORK_PARTS)
    group_cols = [c for c in ["Disease", "Year"] if c in df.columns]
    ny = df[is_ny].groupby(group_cols)["Cases"].sum(min_count=1).reset_index()
    ny["State"] = "New York"
    df = pd.concat([df[~is_ny], ny], ignore_index=True)

    return df[df["State"].isin(STATES)]

# Read CDC's case-count files for one disease and returns a clean table of State | Year | Cases | Disease | Source
# NNDSS files from CDC WONDER are tab-seperated text files and have footnote rows at the bottom that should be removed
# Reads each file from data/raw/incidence folder
# sep="\t" indicates that file is seperated by tabs
def read_nndss(file_names, disease):
    if isinstance(file_names, str):
        file_names = [file_names]
    tables = [pd.read_csv(RAW / f, sep="\t") for f in file_names]
    df = pd.concat(tables, ignore_index=True)
    df = df[df["Notes"].isna()]
    df = df.dropna(subset=["Year"])
    df = df.rename(columns={"Regions/States": "State", "Case Count": "Cases"})
    df["Year"] = df["Year"].astype(int)
    df["Cases"] = pd.to_numeric(df["Cases"], errors="coerce")

    df = fix_names_and_merge(df[["State", "Year", "Cases"]])
    df["Disease"] = disease
    df["Source"] = "CDC NNDSS"
    return df

# The 1993-2015 counts was manually extracted from CDC's MMWR yearly tables
# Dash mean no cases were reported (real zero)
# N means "not notifiable" and U means "unavailable" (both are missing, not zero)
# Reads each file from data/raw/incidence folder
def read_extracted_tables():
    df = pd.read_excel(RAW / "Data_extracted_from_published_tables_1993-2015.xlsx")
    df = df.rename(columns={"Area": "State", "Case Count": "Cases"})
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    text = df["Cases"].astype(str).str.strip()
    df["Cases"] = pd.to_numeric(text.str.replace(",", ""), errors="coerce")
    df.loc[text.isin(["—", "–", "-", "--"]), "Cases"] = 0

    # Standardize disease names
    names = {"measles": "Measles", "mumps": "Mumps", "rubella": "Rubella",
             "hepatitis b, acute": "Hepatitis B (acute)", "salmonellosis": "Salmonellosis"}
    df["Disease"] = df["Disease"].astype(str).str.strip().str.lower().map(names)
    df = df.dropna(subset=["Disease"])

    df = fix_names_and_merge(df[["Disease", "State", "Year", "Cases"]])
    df["Source"] = "MMWR annual summary tables (extracted)"
    return df

# Transforms Project Tycho's weekly measles counts into one total per state per year
# Returns a table of State | Year | Cases | Weeks_Reported | Few_Weeks_Reported | Disease | Source
# Does mot comsider rows that are running totals
# Removes city or country rows to avoid duplicate counts
def read_tycho_measles():
    df = pd.read_csv(RAW / "Measles_project_tycho_1950-1992.csv", low_memory=False)
    df = df[df["PartOfCumulativeCountSeries"] == 0]
    df = df[df["CityName"].isna() & df["Admin2Name"].isna()]
    df["State"] = df["Admin1Name"].astype(str).str.strip().str.title()
    df = df[df["State"].isin(STATES)]

    # Removes rows with week's start date that is not a valid date
    # Removes row with case counts that is not a number
    df["Week"] = pd.to_datetime(df["PeriodStartDate"], errors="coerce")
    df = df.dropna(subset=["Week"])
    df["CountValue"] = pd.to_numeric(df["CountValue"], errors="coerce")

    # Add weeks that are seperated together
    # Assigns each week a year which is the year it starts in
    weekly = (df.groupby(["State", "Week"])["CountValue"]
                .apply(lambda x: x.sum(min_count=1)).reset_index())
    weekly["Year"] = weekly["Week"].dt.year

    # Groups weekly rows by state and year
    # Finds the sum of the weekly counts
    # Counts weekly rows per state and year
    yearly = (weekly.groupby(["State", "Year"])
              .agg(Cases=("CountValue", lambda x: x.sum(min_count=1)),
                   Weeks_Reported=("CountValue", "count"))
              .reset_index())
    
    # Identifies if there are missing weeks from the file which may be unreported or zero
    # Retrieves years with less than 50 weekly rows then flagged
    yearly["Few_Weeks_Reported"] = yearly["Weeks_Reported"] < 50
    yearly["Disease"] = "Measles"
    yearly["Source"] = "Project Tycho"
    return yearly

# Reads ChildVaxView coverage file and returns a clean table of coverage with the offset year added
# ChildVaxView gives coverage by birth year for children checked at different ages
# Each row gets: Birth_Year (no offset) and Year = Birth_Year + the offset for that age
# Reads files from raw/coverage folder
# Dose columns for MMR rows are blank. Empty text are added into these columns to avoid inadvertently labeling them as missing values
def read_childvaxview():
    df = pd.read_csv(ROOT / "data" / "shared" / "ChildVaxView_Vaccination_Coverage_0-35_Months_20261019.csv",
                     low_memory=False)
    df["Dose"] = df["Dose"].fillna("")

    # Retrive MMR and Hep B rows only
    # Keep only rows that report age
    # Remove rows not inclluded in list of 50 states
    df = df[df["Vaccine"].isin(["\u22651 Dose MMR", "Hep B"])]
    df = df[df["Dimension Type"] == "Age"]
    df = df[df["Dimension"].isin(AGE_OFFSET_YEARS)]
    df = df[df["Geography"].isin(STATES)]

    # Remove birth columns that have multi-year groups to avoid duplicate counting
    birth = df["Birth Year/Birth Cohort"].astype(str).str.strip()
    is_single_year = birth.str.fullmatch(r"\d{4}") 
    df = df[is_single_year].copy()
    birth_year = birth[is_single_year].astype(int)

    # Seperate MMR and hep b rows
    is_mmr = df["Vaccine"] != "Hep B"
    offset = df["Dimension"].map(AGE_OFFSET_YEARS)

    # Build a new table with columns State | Vaccine | Dose | Age | Birth_Year | Offset_Years | Year | Coverage | Sample_Size
    out = pd.DataFrame({"State": df["Geography"],
                        "Vaccine": np.where(is_mmr, "MMR", "HepB"),
                        "Dose": np.where(is_mmr, "\u22651 Dose", df["Dose"]),   # MMR's dose is in its name
                        "Age": df["Dimension"],
                        "Birth_Year": birth_year,
                        "Offset_Years": offset,
                        "Year": birth_year + offset,
                        "Coverage": pd.to_numeric(df["Estimate (%)"], errors="coerce"),
                        "Sample_Size": pd.to_numeric(df["Sample Size"], errors="coerce")})
    out["Coverage_Source"] = "ChildVaxView"
    return out

# Reads NIS coverage file
# Each row is labeled by birth cohort
# Read file from data/nis_coverage folder
# Dose columns for MMR rows are blank. Empty text are added into these columns to avoid inadvertently labeling them as missing values
# Keep only the 50 states and overall rows
def read_nis():
    df = pd.read_csv(RAW / "nis_coverage_1995-2024.csv")
    df["Dose"] = df["Dose"].fillna("")
    df = df[df["Geography"].isin(STATES) & (df["Dimension"] == "Overall")]
    df = df[df["Vaccine"].isin(["\u22651 Dose MMR", "Hep B"])].copy()

    # Defines survey year by taking the birth cohort and addin 1 to the most earliest year
    is_mmr = df["Vaccine"] != "Hep B"
    survey_year = df["Birth Year/Birth Cohort"].astype(str).str[-4:].astype(int) + 1

    # Build a new table with columns State | Vaccine | Dose | Age | Birth Year | Offset_Years | Year | Coverage | Sample_Size
    out = pd.DataFrame({"State": df["Geography"],
                        "Vaccine": np.where(is_mmr, "MMR", "HepB"),
                        "Dose": np.where(is_mmr, "\u22651 Dose", df["Dose"]),
                        "Age": "19-35 Months (survey)",
                        "Birth_Year": np.nan,                  # not available in the public files
                        "Offset_Years": 0,
                        "Year": survey_year,
                        "Coverage": pd.to_numeric(df["Estimate (%)"], errors="coerce"),
                        "Sample_Size": pd.to_numeric(df["Sample Size"], errors="coerce")})
    out["Coverage_Source"] = "NIS"
    return out

# Join Disease and coverage on State + Year + Vaccine while keeping all rows
# Incidence: the disease table (cases, rates)
# Vaccine_for: the table saying which vaccine goes with which disease
# coverage_table: the coverage table join (with or without offsets)
# Removes row with no case count or coverage value because it can't be used for analysis
def link(incidence, vaccine_for, coverage_table):
    linked = incidence.merge(vaccine_for, on="Disease")
    linked = linked.merge(coverage_table, on=["State", "Year", "Vaccine"])
    return linked.dropna(subset=["Cases", "Coverage"])

# ======================================================================================================================
# PART C. EXECUTION - run the steps in order
# ======================================================================================================================   
# Check if output folder exists
# Creates folder if it doesn't exist
OUT.mkdir(parents=True, exist_ok=True)

#---STEP1: Disease Counts---
# Reads all disease incidence data and combines it into one table
say("Step 1: reading disease counts")
nndss = [read_nndss(f, d) for d, f in NNDSS_FILES.items()]     # 2016-2023
extracted = read_extracted_tables()                             # 1993-2015
tycho = read_tycho_measles()                                    # 1950-1992 (measles only)

incidence = pd.concat(nndss + [extracted, tycho], ignore_index=True)    # Create a table called incidence with all disease counts
incidence["Few_Weeks_Reported"] = incidence["Few_Weeks_Reported"].fillna(False).astype(bool)    # Flags rows from project tycho that has fewer than 50 rows

# CHECK1: State-year should not appear twice to make sure there are no duplicate counts
# Value should be 0
# If duplicates are found, the script stops
duplicates = incidence.duplicated(["Disease", "State", "Year"]).sum()
assert duplicates == 0, f"{duplicates} state-years appear in more than one source"

# CHECK2: EVERY disease-year should not have a value of 0
# If the sum of all states' cases is 0 or less than 40 states have a number, the script stops
# Prints a summary of number of rows loaded and it source
totals = incidence.groupby(["Disease", "Year"])["Cases"].agg(["sum", "count"])
bad = totals[(totals["sum"] == 0) & (totals["count"] >= 40)]
assert bad.empty, f"every state is zero in: {list(bad.index)}"
say(f"   {len(incidence):,} state-year rows; sources: {sorted(incidence['Source'].unique())}")

#---STEP2: Rates per 100,000---
# Calculates the rate of disease incidence per 100,000 people
# Population estimates only available from 1993-2023
# Years before 1993 have no population, so no rate
say("Step 2: adding rates per 100,000")
population = pd.read_csv(RAW / "population_1993-2023.csv")
# Make sure Population is a number: remove commas, then convert (anything that is not a number becomes missing)
population["Population"] = pd.to_numeric(population["Population"].astype(str).str.replace(",", ""), errors="coerce")
incidence = incidence.merge(population, on=["State", "Year"], how="left")   # keeps all rows
incidence["Rate_per_100k"] = incidence["Cases"] / incidence["Population"] * 100_000

#---STEP3: Coverage---
# Read both coverage sources and combines it into one file
# Checks if there are duplicate rows
# If duplicates are found, the script stops
# Prints a dummary of number of rows, number of ages appear, and counts the different dose labels
say("Step 3: reading coverage")
coverage = pd.concat([read_childvaxview(), read_nis()], ignore_index=True)
key = ["State", "Year", "Vaccine", "Dose", "Age", "Coverage_Source"]
duplicates = coverage.duplicated(key).sum()
assert duplicates == 0, f"{duplicates} duplicate coverage rows"
say(f"   {len(coverage):,} coverage rows "
    f"({coverage['Age'].nunique()} different ages, {coverage['Dose'].nunique()} different doses)")

#---STEP4: Link Disease and Coverage---
# Determines which vaccine goes with which disease
# Salmonellosis is the NEGATIVE CONTROL
# The vaccines should have no effect on it
vaccine_for = pd.DataFrame([("Measles", "MMR"), ("Mumps", "MMR"), ("Rubella", "MMR"),
                            ("Hepatitis B (acute)", "HepB"),
                            ("Salmonellosis", "MMR"), ("Salmonellosis", "HepB")],
                           columns=["Disease", "Vaccine"])

say("Step 4: linking disease and coverage")

# Version 1: ChildVaxView matched by Year = birth year + the offset for its age
linked_offset = link(incidence, vaccine_for, coverage)

# Version 2: NO offset. ChildVaxView matched by plain birth year. (NIS rows are unchanged)
# Coverage is matched to disease by the birth year
# Copie birth year into the birth column if childvaxview is the source
# Updates off set to 0
# Prints the number of rows with age offsets and rows without
no_offset = coverage.copy()
is_cvv = no_offset["Coverage_Source"] == "ChildVaxView"
no_offset.loc[is_cvv, "Year"] = no_offset.loc[is_cvv, "Birth_Year"].astype(int)
no_offset.loc[is_cvv, "Offset_Years"] = 0
linked_plain = link(incidence, vaccine_for, no_offset)
say(f"   with age offsets: {len(linked_offset):,} rows;  no offset: {len(linked_plain):,} rows")

#---STEP5: Save---
# Saves four finished tables and prints a done message
# Incidince table: Cases, population, and rate per 100,000 for every disease
# Coverage table: Coverage for every state, year, vaccine, dose, age and source
# Linked_offset: disease and coverage joined with ChildVaxView matched by birthyear plus age offset
# Linked_plain: same join but without offset
incidence.to_csv(OUT / "incidence_state_year.csv", index=False)
coverage.to_csv(OUT / "coverage_state_year.csv", index=False)
linked_offset.to_csv(OUT / "linked_state_year_age_offsets.csv", index=False)
linked_plain.to_csv(OUT / "linked_state_year_no_offset.csv", index=False)
say(f"Done. Files written to {OUT}")





