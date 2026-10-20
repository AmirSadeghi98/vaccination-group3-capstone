import pandas as pd

# Retrieve historical CDC childhood vaccination coverage
url = "https://archive.cdc.gov/www_cdc_gov/vaccines/imz-managers/coverage/nis/child/figures/2014-map.html"

tables = pd.read_html(url)

print("\nNumber of tables found:", len(tables))

for i, table in enumerate(tables):
    print(f"\nTable {i}")
    print("Shape:", table.shape)
    print(table.head(5).to_string(index=False))

# Clean historical HepB vaccination coverage dataset (1994–2014)
coverage = tables[0][["Unnamed: 0", "HepB (3+)"]].copy()

coverage = coverage.rename(columns={"Unnamed: 0": "survey_year", "HepB (3+)": "hepb_3dose_coverage"})

# Ensure only numeric values are present in the coverage columns
coverage["survey_year"] = pd.to_numeric(coverage["survey_year"], errors="coerce")
coverage["hepb_3dose_coverage"] = pd.to_numeric(coverage["hepb_3dose_coverage"], errors="coerce")
coverage["source"] = "CDC NIS-Child, 1994–2014"

# Validate results 
print("\nHistorical Coverage Dataset:")
print("Shape:", coverage.shape)

print("\nMissing Values:")
print(coverage.isna().sum())

print("\nYear Range:")
print(coverage["survey_year"].min(), "-", coverage["survey_year"].max())

print("\nComplete Coverage Dataset:")
print(coverage.to_string(index=False))

# Save cleaned dataset
coverage.to_csv("HepB_Historical_Coverage_1994_2014.csv", index=False, encoding="utf-8-sig")

# Visualize historical HepB vaccination coverage
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))

plt.plot(coverage["survey_year"], coverage["hepb_3dose_coverage"], marker="o", linewidth=2)

plt.title("National HepB Three-Dose Vaccination Coverage\n" "Children Aged 19–35 Months, 1994–2014")

plt.xlabel("Survey Year")
plt.ylabel("Vaccination Coverage (%)")
plt.xticks(range(1994, 2015, 2))
plt.ylim(0, 100)
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("HepB_Historical_Coverage_Trends.png", dpi=300)

plt.show()