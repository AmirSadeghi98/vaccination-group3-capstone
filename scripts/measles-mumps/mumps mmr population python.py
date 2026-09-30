import pandas as pd

# load files

mumps_mmr = pd.read_csv(
    "mumps mmr merge final.csv")

population = pd.read_csv(
    "us population 2000-2021.csv")


# standardize names

mumps_mmr["State"] = (
    mumps_mmr["State"]
    .astype(str)
    .str.upper()
    .str.strip())

population["State"] = (
    population["State"]
    .astype(str)
    .str.upper()
    .str.strip())


# merge

final = pd.merge(
    mumps_mmr,
    population[["Year", "State", "State_Population"]],
    on=["State", "Year"],
    how="left",
    validate="one_to_one")


# mumps cases numeric

final["Mumps_Cases"] = pd.to_numeric(
    final["Mumps_Cases"],
    errors="coerce")


# calculate mumps cases per 100,000

final["Mumps_per_100K"] = (
    final["Mumps_Cases"] /
    final["State_Population"]) * 100000


# check

print(
    final[
        [
            "Year",
            "State",
            "Mumps_Cases",
            "MMR_Coverage",
            "State_Population",
            "Mumps_per_100K"]
    ].head(20))


# save

final.to_csv(
    "mumps mmr merge with population.csv",
    index=False)



