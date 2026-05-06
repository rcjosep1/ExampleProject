# Data

## Directory Structure

- `raw/`
  - Contains original source datasets used in the project.
  - Includes:
    - EarthChem / GEOROC exports
      - MORB (Stracke)
      - OIB / hotspot (Stracke)
      - ARC (Woerner)
    - ARC age compilation dataset (Pilger)
    - Qin major-element compilation
    - PetDB compilation dataset
    - Targeted literature datasets:
      - McCoy-West (2010) — Lookout Volcanics
      - Tornare (2016) — Canary Islands volcanics
  - Files are stored in CSV format for compatibility with pandas.

---

## Root (`data/`)

- `cleaned_dataset.csv`
  - Final merged dataset used for:
    - oxide-vs-age analysis
    - tectonic comparisons
    - mapping workflows

---

## Core Datasets

| Dataset | Tectonic Context |
|---|---|
| MORB (Stracke) | Divergent |
| OIB / hotspot (Stracke) | Intraplate |
| ARC (Woerner) | Convergent |
| ARC_AGE (Pilger) | ARC radiometric age compilation |
| PetDB | Mixed tectonic settings |

---

## Supplementary Datasets

| Dataset | Purpose |
|---|---|
| McCoy-West (2010) | Mid-Cretaceous intraplate basalt coverage |
| Tornare (2016) | Miocene intraplate volcanic coverage |
| Qin (2024) | Large igneous province / hotspot extension |

These supplementary datasets were incorporated to improve temporal coverage of intraplate systems.

---

## Qin Dataset Handling

The Qin compilation was filtered to isolate large igneous province and hotspot-related systems, including:

- Ontong Java Plateau
- Kerguelen Plateau
- Ethiopian Plateau
- Karoo–Ferrar Province

Additional filtering steps:
- removal of plutonic material
- removal of xenolith/peridotite samples
- downsampling of large localities to reduce sampling bias

Representative system ages were assigned where direct radiometric ages were unavailable.

---

## Data Handling Decisions

- Only whole-rock geochemistry datasets were included.
- Mineral chemistry datasets (e.g., EPMA, LA-ICP-MS spot analyses) were excluded.
- Arc datasets were filtered toward basaltic and basaltic-andesite compositions.
- Matrix-style supplementary spreadsheets were parsed manually in Python.

---

## Analytical Workflow

The merged dataset is used to:

- calculate 50 Ma age bins
- compute median oxide compositions
- compute interquartile ranges
- compare tectonic settings through time
- generate geographic sample maps

Oxides analyzed include:
- SiO2
- MgO
- TiO2
- K2O

---

## Mapping

Interactive geographic maps are generated for:
- MORB / divergent settings
- ARC / convergent settings
- hotspot / intraplate settings

Samples are colored by 50 Ma age bins.

---

## Size and Version Control

- Large EarthChem exports are excluded from GitHub version control due to file size limitations.
- Smaller curated datasets and scripts are included for reproducibility.

---

## Output

Primary output dataset:

```text
data/cleaned_dataset.csv