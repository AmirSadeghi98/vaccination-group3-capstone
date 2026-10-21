import pandas as pd

# load files
merged = pd.read_csv(
    "mumps mmr merge with population.csv")

mumps = pd.read_csv(
    "mumps cases cleaned 1923-2021_final.csv")

mmr = pd.read_csv(
    "mmr coverage 1995-2025.csv")


# keep 2000-2021

merged_2000_2021 = merged[
    merged["Year"].between(2000, 2021)].copy()

mumps_2000_2021 = mumps[
    mumps["Year"].between(2000, 2021)].copy()

mmr_2000_2021 = mmr[
    mmr["Year"].between(2000, 2021)].copy()


# sort

merged_2000_2021 = merged_2000_2021.sort_values(
    ["Year", "State"]).reset_index(drop=True)

mumps_2000_2021 = mumps_2000_2021.sort_values(
    ["Year", "State"]).reset_index(drop=True)

mmr_2000_2021 = mmr_2000_2021.sort_values(
    ["Year", "State"]).reset_index(drop=True)


# save

merged_2000_2021.to_csv(
    "mumps mmr merge with population 2000-2021_final.csv",
    index=False)

mumps_2000_2021.to_csv(
    "mumps cases 2000-2021_final.csv",
    index=False)

mmr_2000_2021.to_csv(
    "mmr coverage 2000-2021_final.csv",
    index=False)


# check
print("merged:")
print(merged_2000_2021.shape)
print(merged_2000_2021.groupby("Year")["State"].nunique())

print("\nmumps:")
print(mumps_2000_2021.shape)
print(mumps_2000_2021.groupby("Year")["State"].nunique())

print("\nMMR:")
print(mmr_2000_2021.shape)
print(mmr_2000_2021.groupby("Year")["State"].nunique())
