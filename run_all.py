"""
run_all.py

WHAT IT DOES?
Runs every script in the project, one after the other, in the right order.

HOW TO RUN (from the repository folder)
    python run_all.py

NEEDS INTERNET: 3 of the scripts download archived CDC web pages.
"""
import os
import subprocess
import sys
from pathlib import Path

# ======================================================================================================================
# SETTINGS
# ======================================================================================================================
ROOT = Path(__file__).resolve().parent       # the repository folder

# Scripts to run, in order. They need to run in this order because later scripts use files made by earlier ones.
SCRIPTS = [
    "scripts/mmr/cleaning_data.py",
    "scripts/mmr/analysis.py",
    "scripts/hepB/HepB_Data_Cleaning.py",
    "scripts/hepB/HepB_Incidence_Cleaning.py",        # downloads a CDC web page
    "scripts/hepB/HepB_Harmonization.py",
    "scripts/hepB/HepB_Historical_Analysis.py",       # downloads a CDC web page
    "scripts/hepB/HepB_Historical_Coverage.py",       # downloads a CDC web page
    "scripts/hepB/HepB_Historical_Visualization.py",
    "scripts/hepB/HepB_Statistical_Analysis.py",
    "scripts/mmr/mumps and mmr analysis.py",
]

# Tells matplotlib to save figures to files instead of opening windows
settings = dict(os.environ, MPLBACKEND="Agg")

# ======================================================================================================================
# RUN
# ======================================================================================================================
for script in SCRIPTS:
    print("\nRunning", script)
    result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, env=settings)

    # A return code other than 0 means the script had an error, so stop here
    if result.returncode != 0:
        print("\nFAILED:", script)
        sys.exit(1)

print("\nAll scripts finished.")
