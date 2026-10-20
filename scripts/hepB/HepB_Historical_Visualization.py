# Combined historical HepB visualization

import pandas as pd
import matplotlib.pyplot as plt

# Load cleaned datasets
coverage = pd.read_csv("HepB_Historical_Coverage_1994_2014.csv", encoding="utf-8-sig")

incidence = pd.read_csv("HepB_AgeSpecific_Incidence_2003_2023.csv", encoding="utf-8-sig")

# Create two-panel figure
fig, axes = plt.subplots(2, 1, figsize=(11, 9))

# Panel 1: Childhood vaccination coverage
axes[0].plot(coverage["survey_year"], coverage["hepb_3dose_coverage"], marker="o", linewidth=2)

axes[0].set_title("Childhood HepB Three-Dose Vaccination Coverage (1994–2014)")
axes[0].set_ylabel("Coverage (%)")
axes[0].set_ylim(0, 100)
axes[0].grid(alpha=0.3)

# Panel 2: Age-specific acute HepB incidence
for age_group, subset in incidence.groupby("age_group"):
    axes[1].plot(subset["year"], subset["acute_hepb_rate"], marker="o", markersize=3, label=age_group)

axes[1].set_title("Acute HepB Incidence by Age Group (2003–2023)")
axes[1].set_xlabel("Year")
axes[1].set_ylabel("Cases per 100,000")
axes[1].legend(title="Age group")
axes[1].grid(alpha=0.3)
axes[0].set_xticks(range(1994, 2015, 2))
axes[1].set_xticks(range(2003, 2024, 2))

plt.tight_layout()

plt.savefig("HepB_Historical_Combined_Trends.png",dpi=300)

plt.show()
