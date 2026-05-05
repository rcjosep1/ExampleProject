# Data

## Directory Structure

- `raw/`
  - Contains original source datasets used in the project.
  - Includes:
    - EarthChem / GEOROC exports (MORB, OIB, ARC)
    - ARC age compilation dataset
    - Targeted literature datasets:
      - McCoy-West (2010) — Lookout Volcanics (whole-rock)
      - Tornare (2016) — Canary Islands (whole-rock)
  - Files are stored in CSV format for compatibility with pandas.


- Root (`data/`)
  - `cleaned_dataset.csv`
    - Final merged dataset used for analysis and plotting.

---

## Notes on Data Sources

### Core Datasets
- **MORB (Stracke)** — divergent settings
- **OIB / hotspot (Stracke)** — intraplate settings
- **ARC (Woerner)** — convergent settings
- **ARC_AGE (Pilger)** — radiometric age compilation

### Supplementary Datasets
- **McCoy-West (2010)** — mid-Cretaceous intraplate basalts
- **Tornare (2016)** — Miocene intraplate volcanics

These supplementary datasets were added to improve temporal coverage of hotspot systems.

---

## Data Handling Decisions

- Only **whole-rock geochemistry** datasets are included in the analysis.
- Mineral chemistry datasets (e.g., EPMA, LA-ICP-MS) are excluded to maintain consistency.
- Matrix-style spreadsheets (samples as columns, oxides as rows) are parsed manually in code.

---

## Size and Version Control

- Large EarthChem exports are **excluded from version control** due to GitHub file size limits.
- Smaller curated datasets (McCoy, Tornare) are included for reproducibility.

---

## Output

The final dataset used in analysis is:

```text
data/cleaned_dataset.csv