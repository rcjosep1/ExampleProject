# SES230 Group Project

## Project Team

- **PI:** Ramsey Joseph  
- **Literature Reviewer:** Cambria Leben  
- **Data Manager:** Reese Woodward  
- **Coders:** Amanda Byrd, Bryan Kemp  

---

## Project Overview

This project investigates how major-element geochemistry varies through time across broad tectonic settings. We compare whole-rock volcanic compositions from divergent, convergent, and intraplate environments using compiled geochemical datasets.

The primary tectonic groupings are:

- **MOR / MORB** — divergent settings
- **ARC** — convergent-margin settings
- **HOTSPOT** — intraplate, ocean-island, oceanic plateau, and large igneous province settings

The main geochemical variables analyzed are:

- SiO2
- MgO
- TiO2
- K2O

The project produces both:

- oxide-versus-age plots
- geographic maps of sample locations colored by age bin

---

## Repository Structure

```text
SES230_Jupiter_TermProject/
│
├── code/
│   ├── main.py
│   ├── analysis.py
│   ├── prototype_plot.py
│   └── utils.py
│
├── data/
│   ├── cleaned_dataset.csv
│   ├── README.md
│   ├── SES 230 Jupiter - Sheet1 (1).csv
│   └── raw/
│       ├── 2021-10-FWQ7DT_Martin_data.csv
│       ├── 2021-12_SS1TYI_Woerner_data.csv
│       ├── 2022_09-0SVW6S_Stracke_MORB.csv
│       ├── 2022_09-0SVW6S_Stracke_OIB.csv
│       ├── 2022-2-FLV19S_Tappe_data_v2024.csv
│       ├── 2023-005_e_Pilger_Andean-Igneous-Radiometric-Dates.csv
│       ├── 2024-007_AVAW2Y_Qin_Major Elements.csv
│       ├── 2024-007_AVAW2Y_Qin_Trace Elements.csv
│       ├── mccoy_lookout_wholerock.csv
│       ├── PetDB Data.csv
│       └── tornare_wholerock.csv
│
├── figures/
│   ├── arc_map.html
│   ├── hotspot_map.html
│   ├── morb_map.html
│   ├── arc.png
│   ├── hotspot.png
│   ├── morb.png
│   ├── sio2_vs_age.png
│   ├── mgo_vs_age.png
│   ├── tio2_vs_age.png
│   ├── k2o_vs_age.png
│   └── Code_Diagram.drawio.png
│
├── zotero/
│   ├── SES 230 Term Project Leben 3.bib
│   └── SES230_Jupiter_ZoteroLibrary.bib
│
├── SES230_FinalReport_Jupiter.ipynb
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore


```
## Setup

Install dependencies:

```bash
pip install -r requirements.txt

Run the main analysis workflow from the repository root:
python code/main.py

This regenerates:
data/cleaned_dataset.csv

figures/sio2_vs_age.png
figures/mgo_vs_age.png
figures/tio2_vs_age.png
figures/k2o_vs_age.png

figures/morb_map.html
figures/arc_map.html
figures/hotspot_map.html


Notebook Report
Open:
SES230_FinalReport_Jupiter.ipynb

The notebook reads:
data/cleaned_dataset.csv
and reproduces the principal figures and maps without rerunning the full extraction workflow.
