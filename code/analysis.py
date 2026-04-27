from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from utils import clean_sample_name, collapse, compute_age, standardize_setting, to_num


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
FIGURES_DIR = ROOT_DIR / "figures"

CHEM_PATH = RAW_DIR / "earthchem_export_apr22_26_0128.csv"
META_PATH = RAW_DIR / "earthchem_export_apr22_26_0128_sample_metadata.csv"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def binned_plot(df: pd.DataFrame, var: str, output_name: str) -> None:
    grouped = df.groupby(["Setting", "Age_Bin"])[var]

    stats = grouped.median().reset_index(name="median")
    q1 = grouped.quantile(0.25).reset_index(name="q1")
    q3 = grouped.quantile(0.75).reset_index(name="q3")

    stats = stats.merge(q1, on=["Setting", "Age_Bin"])
    stats = stats.merge(q3, on=["Setting", "Age_Bin"])

    plt.figure(figsize=(10, 6))

    for setting in stats["Setting"].dropna().unique():
        subset = stats[stats["Setting"] == setting].sort_values("Age_Bin")
        plt.plot(subset["Age_Bin"], subset["median"], marker="o", label=setting)
        plt.fill_between(subset["Age_Bin"], subset["q1"], subset["q3"], alpha=0.2)

    plt.gca().invert_xaxis()
    plt.xlabel("Age (Ma)")
    plt.ylabel(var)
    plt.title(f"{var} vs Age (binned)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / output_name, dpi=200)
    plt.close()


def main() -> None:
    chem = pd.read_csv(CHEM_PATH, encoding="utf-8-sig", low_memory=False)
    meta = pd.read_csv(META_PATH, encoding="utf-8-sig", low_memory=False)

    chem["sample_key"] = clean_sample_name(chem["Sample Name"])
    meta["sample_key"] = clean_sample_name(meta["Analyzed Sample Name"])

    chem = collapse(chem, "sample_key")
    meta = collapse(meta, "sample_key")

    df = chem.merge(meta, on="sample_key", how="inner")

    for column in ["Geologic Age", "Geologic Age Min (Ma)", "Geologic Age Max (Ma)"]:
        if column in df.columns:
            df[column] = to_num(df[column])

    df["Age_Ma"] = df.apply(compute_age, axis=1)

    df["SiO2"] = to_num(df.get("SiO2 (wt%)"))
    df["MgO"] = to_num(df.get("MgO (wt%)"))
    df["TiO2"] = to_num(df.get("TiO2 (wt%)"))
    df["K2O"] = to_num(df.get("K2O (wt%)"))
    df["FeOT"] = (
        to_num(df.get("FeOT (wt%)"))
        .fillna(to_num(df.get("Fe2O3T (wt%)")))
        .fillna(to_num(df.get("FeO (wt%)")))
        .fillna(to_num(df.get("Fe2O3 (wt%)")))
    )

    df = df[df["Age_Ma"].notna()]
    df = df[df["SiO2"].notna()]

    if "Tectonic Setting" in df.columns:
        df["Setting"] = df["Tectonic Setting"].apply(standardize_setting)
    else:
        df["Setting"] = "OTHER"

    bin_size = 100
    df["Age_Bin"] = (df["Age_Ma"] // bin_size) * bin_size

    df.to_csv(PROCESSED_DIR / "earthchem_cleaned_poc.csv", index=False)

    binned_plot(df, "SiO2", "sio2_vs_age.png")
    binned_plot(df, "MgO", "mgo_vs_age.png")
    binned_plot(df, "TiO2", "tio2_vs_age.png")


if __name__ == "__main__":
    main()
