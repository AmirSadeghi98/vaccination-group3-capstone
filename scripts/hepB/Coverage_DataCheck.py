from pathlib import Path

# Folders (this file is in scripts/hepB/, so the repository folder is two levels up)
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "hepB" / "raw"
SHARED = ROOT / "data" / "shared"          # ChildVaxView file used by both pipelines
CLEAN = ROOT / "data" / "hepB" / "cleaned"
FIGS = ROOT / "documents" / "figures" / "hepB"
CLEAN.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

import pandas as pd

# Load original CDC vaccination coverage data
df = pd.read_csv(
    SHARED / "ChildVaxView_Vaccination_Coverage_0-35_Months_20261019.csv"
)

print("Dataset shape:", df.shape)
print("Number of rows:", len(df))
print("Number of columns:", len(df.columns))

print("\nFirst 5 rows:")
print(df.head())