from pathlib import Path

import pandas as pd


folder = Path(r"C:\Users\ramse\Documents\AnacondaProjects\ExampleProject\data\Data")

files = {
    "MORB": ("2022_09-0SVW6S_Stracke_MORB.csv", 3),
    "HOTSPOT": ("2022_09-0SVW6S_Stracke_OIB.csv", 0),
    "ARC": ("2021-12_SS1TYI_Woerner_data.csv", 1),
    "ARC_AGE": ("2023-005_e_Pilger_Andean-Igneous-Radiometric-Dates.csv", 0),
}


def load_dataset(fname: str, header_row: int) -> pd.DataFrame:
    df = pd.read_csv(folder / fname, header=header_row, low_memory=False)
    df.columns = [str(col).strip() for col in df.columns]
    return df


def get_numeric(df: pd.DataFrame, candidates: list[str]) -> pd.Series:
    for col in candidates:
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(index=df.index, dtype="float64")


def build_age(df: pd.DataFrame) -> pd.Series:
    age = get_numeric(df, ["Age", "AGE", "Age (Ma)", "Published Age", "Corrected age"])
    min_age = get_numeric(df, ["MIN AGE", "Min Age", "Geologic Age Min (Ma)"])
    max_age = get_numeric(df, ["MAX AGE", "Max Age", "Geologic Age Max (Ma)"])

    return age.where(
        age.notna(),
        min_age.where(
            min_age.notna() & max_age.isna(),
            max_age.where(
                max_age.notna() & min_age.isna(),
                (min_age + max_age) / 2,
            ),
        ),
    )


def extract_basic(df, setting):
    out = pd.DataFrame()

    # ---- Chemistry ----
    if "SIO2" in df.columns:
        out["SiO2"] = pd.to_numeric(df["SIO2"], errors="coerce")

    if "MG0" in df.columns:  # sometimes typo, just in case
        out["MgO"] = pd.to_numeric(df["MG0"], errors="coerce")
    elif "MGO" in df.columns:
        out["MgO"] = pd.to_numeric(df["MGO"], errors="coerce")

    if "TIO2" in df.columns:
        out["TiO2"] = pd.to_numeric(df["TIO2"], errors="coerce")

    # ---- Age handling ----
    age = None

    if "AGE" in df.columns:
        age = pd.to_numeric(df["AGE"], errors="coerce")

    if "MIN AGE" in df.columns and "MAX AGE" in df.columns:
        min_age = pd.to_numeric(df["MIN AGE"], errors="coerce")
        max_age = pd.to_numeric(df["MAX AGE"], errors="coerce")

        midpoint = (min_age + max_age) / 2

        # fill missing AGE with midpoint
        if age is not None:
            age = age.fillna(midpoint)
        else:
            age = midpoint

    out["Age_Ma"] = age

    # ---- Setting ----
    out["Setting"] = setting

    return out


def extract_arc(df):
    out = pd.DataFrame()

    out["SiO2"] = pd.to_numeric(df["SiO2"], errors="coerce")
    out["MgO"] = pd.to_numeric(df["MgO"], errors="coerce")
    out["TiO2"] = pd.to_numeric(df["TiO2"], errors="coerce")

    # NOTE: exact column name from your output
    out["Age_Ma"] = pd.to_numeric(df["Age  (Ma)"], errors="coerce")

    out["Setting"] = "ARC"

    return out

def extract_arc_age(df):
    out = pd.DataFrame()

    # key column from your output
    out["Age_Ma"] = pd.to_numeric(df["Age"], errors="coerce")

    out["Setting"] = "ARC"

    return out



dfs = {key: load_dataset(fname, header_row) for key, (fname, header_row) in files.items()}

print({k: v.shape for k, v in dfs.items()})

arc_age = extract_arc_age(dfs["ARC_AGE"])

for name, df in dfs.items():
    print("\n====", name, "====")
    print(df.columns.tolist()[:25])


morb = extract_basic(dfs["MORB"], "MOR")
oib = extract_basic(dfs["HOTSPOT"], "HOTSPOT")
arc = extract_arc(dfs["ARC"])

df_all = pd.concat([morb, oib, arc, arc_age], ignore_index=True)

df_all = df_all.dropna(subset=["SiO2", "Age_Ma"])

print(df_all.head())
print(df_all[["SiO2", "MgO", "TiO2", "Age_Ma", "Setting"]].notna().sum())

df_all = df_all.dropna(subset=["SiO2", "Age_Ma"]).copy()

bin_size = 50
df_all["Age_Bin"] = (df_all["Age_Ma"] // bin_size) * bin_size

stats = (
    df_all.groupby(["Setting", "Age_Bin"])["SiO2"]
    .agg(
        median="median",
        q25=lambda x: x.quantile(0.25),
        q75=lambda x: x.quantile(0.75),
    )
    .reset_index()
)

print(stats.head())


import matplotlib.pyplot as plt

plt.figure(figsize=(8,5))

for setting in stats["Setting"].unique():
    sub = stats[stats["Setting"] == setting]
    
    plt.plot(sub["Age_Bin"], sub["median"], marker="o", label=setting)
    plt.fill_between(sub["Age_Bin"], sub["q25"], sub["q75"], alpha=0.2)

plt.gca().invert_xaxis()
plt.xlabel("Age (Ma)")
plt.ylabel("SiO2")
plt.legend()
plt.show()