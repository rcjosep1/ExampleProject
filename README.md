# SES230 Group Project

Repository scaffold for the SES230 final project submission.

## Current contents

- `SES230_GroupNumber_FinalReport.ipynb`: current notebook report placeholder. Replace `GroupNumber` in the filename when your repository name is finalized.
- `code/analysis.py`: main EarthChem analysis workflow.
- `code/utils.py`: shared cleaning and helper functions.
- `code/prototype_plot.py`: earlier proof-of-concept plotting script kept for reference.
- `data/raw/`: source data and acquisition notes.
- `data/processed/`: cleaned outputs ready for analysis.
- `figures/`: generated figures for the report.
- `docs/additional_notes.md`: project notes and GitHub setup reminders.
- `zotero/SES230_GroupNumber_ZoteroLibrary.bib`: placeholder bibliography export file.

## Setup

```bash
pip install -r requirements.txt
python code/analysis.py
```

## Important note on data

The full EarthChem export is larger than GitHub's normal file-size limit, so the repository excludes the biggest raw files by default. Keep those files locally, use Git LFS, or provide a download workflow if your instructor requires the full dataset in version control.
