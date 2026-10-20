import pandas as pd

# Load original CDC vaccination coverage data
df = pd.read_csv(
    "Vaccination_Coverage_among_Young_Children_(0-35_Months)_20260924.csv"
)

print("Dataset shape:", df.shape)
print("Number of rows:", len(df))
print("Number of columns:", len(df.columns))

print("\nFirst 5 rows:")
print(df.head())