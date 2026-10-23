import pandas as pd

# open data files
mumps_1923 = pd.read_csv(
    "mumps cases combined 1923-2021.csv")

mumps_2002= pd.read_csv(
    "mumps cases 2002-2010.csv")

# standardize state names
mumps_1923["State"] = (
    mumps_1923["State"]
    .astype(str)
    .str.upper()
    .str.strip())

mumps_2002["State"] = (
    mumps_2002["State"]
    .astype(str)
    .str.upper()
    .str.strip())

# check year numeric
mumps_1923["Year"] = pd.to_numeric(
    mumps_1923["Year"],
    errors="coerce")

mumps_2002["Year"] = pd.to_numeric(
    mumps_2002["Year"],
    errors="coerce")

# combine
mumps_all = pd.concat(
    [
        mumps_1923,
        mumps_2002],
    ignore_index=True)

# sort by state and year
mumps_all = mumps_all.sort_values(
    ["State", "Year"]).reset_index(drop=True)

# check dataset
print("rows:")
print(len(mumps_all))

print("\nstates:")
print(mumps_all["State"].nunique())

print("\nrange:")
print(
    mumps_all["Year"].min(),
    "-",
    mumps_all["Year"].max())

# check for duplicates
duplicates = mumps_all.duplicated(
    subset=["State", "Year"]).sum()

print("\nduplicates:")
print(duplicates)

# check missing values
print("\nmissing values:")
print(mumps_all["Mumps_Cases"].isna().sum())

# save

mumps_all.to_csv("mumps cases cleaned 1923-2021_final",
    index=False)


