import pandas as pd

# load datasets
mumps = pd.read_csv(
    "mumps cases 1923-2021_final.csv")

mmr = pd.read_csv(
    "mmr coverage combined 1995-2025.csv")

# standardize state names

mumps["State"] = (
    mumps["State"]
    .astype(str)
    .str.upper()
    .str.strip())

mmr["State"] = (
    mmr["State"]
    .astype(str)
    .str.upper()
    .str.strip())

# standardize year

mumps["Year"] = pd.to_numeric(
    mumps["Year"],
    errors="coerce").astype("Int64")

mmr["Year"] = pd.to_numeric(
    mmr["Year"],
    errors="coerce").astype("Int64")

# MMR coverage numeric

mmr["MMR_Coverage"] = pd.to_numeric(
    mmr["MMR_Coverage"],
    errors="coerce")

# check for duplicates

print("MMR duplicates:")
print(mmr.duplicated(["State", "Year"]).sum())

print("\nmumps duplicates:")
print(mumps.duplicated(["State", "Year"]).sum())


# merge

combined = pd.merge(
    mmr,
    mumps,
    on=["State", "Year"],
    how="left",
    validate="one_to_one")

# sort

combined = combined.sort_values(
    ["State", "Year"]).reset_index(drop=True)

# check

print("\nstates:")
print(combined["State"].nunique())

print("\nrange:")
print(
    combined["Year"].min(),
    "-",
    combined["Year"].max())

print("\nmissing MMR coverage:")
print(combined["MMR_Coverage"].isna().sum())

print("\nmissing mumps cases:")
print(combined["Mumps_Cases"].isna().sum())

# check overlap by year

overlap = combined[
    combined["MMR_Coverage"].notna() &
    combined["Mumps_Cases"].notna()]

print("\nusable states by year:")
print(
    overlap.groupby("Year")["State"]
    .nunique()
    .to_string())

# show unmatched records

print("\nMMR records without matching mumps data:")

print(
    combined[
        combined["MMR_Coverage"].notna() &
        combined["Mumps_Cases"].isna()
    ][
        ["State", "Year", "MMR_Coverage", "Mumps_Cases"]
    ].to_string(index=False))

# save 

combined.to_csv(
    "mumps mmr merge final.csv",
    index=False)
