from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


file_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "mock_earthchem_dataset.csv"

df = pd.read_csv(file_path)

min_age = pd.to_numeric(df["Geologic Age Min (Ma)"], errors="coerce")
max_age = pd.to_numeric(df["Geologic Age Max (Ma)"], errors="coerce")

df["Age_Ma"] = np.where(
    min_age.notna() & max_age.notna(),
    (min_age + max_age) / 2,
    np.where(min_age.notna(), min_age, max_age),
)

df["SiO2"] = pd.to_numeric(df["SiO2 (wt%)"], errors="coerce")
df = df.dropna(subset=["Age_Ma", "SiO2", "Tectonic Setting"]).copy()
df["Tectonic Setting"] = df["Tectonic Setting"].astype(str).str.upper().str.strip()

bin_size = 500
df["Age_Bin"] = (df["Age_Ma"] // bin_size) * bin_size

stats = (
    df.groupby(["Tectonic Setting", "Age_Bin"])["SiO2"]
    .agg(
        median="median",
        q25=lambda x: x.quantile(0.25),
        q75=lambda x: x.quantile(0.75),
        count="count",
    )
    .reset_index()
    .sort_values(["Tectonic Setting", "Age_Bin"])
)

plt.figure(figsize=(8, 5))

settings_order = ["MOR", "ARC", "HOTSPOT"]
colors = {
    "MOR": "tab:orange",
    "ARC": "tab:blue",
    "HOTSPOT": "tab:green",
}

for setting in settings_order:
    subset = stats[stats["Tectonic Setting"] == setting].sort_values("Age_Bin")
    if subset.empty:
        continue

    plt.plot(
        subset["Age_Bin"],
        subset["median"],
        marker="o",
        linewidth=2,
        label=setting,
        color=colors.get(setting),
    )
    plt.fill_between(
        subset["Age_Bin"],
        subset["q25"],
        subset["q75"],
        alpha=0.18,
        color=colors.get(setting),
    )

plt.gca().invert_xaxis()
plt.xlabel("Age (Ma)")
plt.ylabel("SiO2 (wt%)")
plt.title("SiO2 by tectonic setting through time")
plt.legend()
plt.tight_layout()
plt.show()
