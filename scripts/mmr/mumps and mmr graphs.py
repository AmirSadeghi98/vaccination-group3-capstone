from pathlib import Path

# Folders (this file is in scripts/mmr/, so the repository folder is two levels up)
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "mmr" / "raw"
CLEAN = ROOT / "data" / "mmr" / "cleaned"

import pandas as pd
from scipy.stats import pearsonr, spearmanr

# read  dataset
df = pd.read_csv(
    CLEAN / "mumps mmr merge with population 2000-2021_final.csv")



# graph mumps incidence 2000-2021

import matplotlib.pyplot as plt

time_data = df[
    df["Year"].between(2000, 2021)].copy()

yearly_incidence = (
    time_data
    .groupby("Year")
    .agg(
        Total_Cases=("Mumps_Cases", "sum"),
        Total_Population=("State_Population", "sum"))
    .reset_index())

yearly_incidence["Mumps_per_100K"] = (
    yearly_incidence["Total_Cases"] /
    yearly_incidence["Total_Population"]) * 100000

plt.figure(figsize=(10, 6))

plt.plot(
    yearly_incidence["Year"],
    yearly_incidence["Mumps_per_100K"],
    marker="o")

plt.xlabel("Year")
plt.ylabel("mumps incidence per 100,000")
plt.title("Average US Mumps Incidence, 2000-2021")

plt.xticks(
    range(2000, 2022),
    rotation=45)

plt.grid(alpha=0.3)
plt.tight_layout()

plt.show()


# graph MMR coverage 2000-2021

yearly_mmr = (
    df.groupby("Year")["MMR_Coverage"]
    .mean())

plt.figure(figsize=(10, 5))

plt.plot(
    yearly_mmr.index,
    yearly_mmr.values,
    marker="o")

plt.title("Average State MMR Coverage, 2000–2021")
plt.xlabel("Year")
plt.ylabel("Average MMR Coverage (%)")

plt.xticks(range(2000,2022), rotation=45)

plt.xlim(2000, 2021)
plt.grid(True)
plt.tight_layout()
plt.show()


# scatterplot MMR coverage vs mumps incidence

analysis = df.dropna(
    subset=["MMR_Coverage", "Mumps_per_100K"])

plt.figure(figsize=(10, 6))

plt.scatter(
    analysis["MMR_Coverage"],
    analysis["Mumps_per_100K"],
    alpha=0.5)

plt.title("MMR Coverage vs. Mumps Incidence")
plt.xlabel("MMR Coverage (%)")
plt.ylabel("Mumps Cases per 100,000")

plt.grid(True)
plt.tight_layout()
plt.show()



