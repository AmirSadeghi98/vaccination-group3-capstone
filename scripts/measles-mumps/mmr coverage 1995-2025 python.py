import pandas as pd

# read cleaned mmr coverage file
coverage_1995 = pd.read_csv(
    "mumps vaccination coverage 1995-2008.csv")

coverage_2009 = pd.read_csv(
    "cdc cleaned MMR coverage 2009-2025.csv")

# organize column name

def column_name(mmr):
    rename_dict = {"Coverage %": "MMR_Coverage"}         

    return mmr.rename(columns=rename_dict)  

coverage_1995 = column_name(coverage_1995)
coverage_2009 = column_name(coverage_2009)

# combine all the files
coverage_all = pd.concat(
    [
        coverage_1995,
        coverage_2009],
    ignore_index=True)


# sort by state and year
coverage_all = coverage_all.sort_values(
    ["State", "Year"])

# reset row numbersm
coverage_all = coverage_all.reset_index(drop=True)

# check 
print("data:")
print(coverage_all.head(50))

print("\nrows:")
print(len(coverage_all))

print("\nstates:")
print(coverage_all["State"].nunique())

print("\nyears:")
print(coverage_all["Year"].min(), "to", coverage_all["Year"].max())


# save file
coverage_all.to_csv(
    "mmr coverage combined 1995-2025.csv",
    index=False)
