from pathlib import Path

import pandas as pd

BASE_DIR = Path(r"C:\Users\ramse\Documents\AnacondaProjects\TermProject")

DATA_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DATA = BASE_DIR / "data"
FIG_DIR = BASE_DIR / "figures"

folder = DATA_DIR

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

    if "SIO2" in df.columns:
        out["SiO2"] = pd.to_numeric(df["SIO2"], errors="coerce")

    if "MGO" in df.columns:
        out["MgO"] = pd.to_numeric(df["MGO"], errors="coerce")

    if "TIO2" in df.columns:
        out["TiO2"] = pd.to_numeric(df["TIO2"], errors="coerce")

    age = None

    if "AGE" in df.columns:
        age = pd.to_numeric(df["AGE"], errors="coerce")

    if "MIN AGE" in df.columns and "MAX AGE" in df.columns:
        min_age = pd.to_numeric(df["MIN AGE"], errors="coerce")
        max_age = pd.to_numeric(df["MAX AGE"], errors="coerce")
        midpoint = (min_age + max_age) / 2
        if age is not None:
            age = age.fillna(midpoint)
        else:
            age = midpoint

    out["Age_Ma"] = age
    out["Setting"] = setting
    return out


def extract_arc(df):
    out = pd.DataFrame()
    out["SiO2"] = pd.to_numeric(df["SiO2"], errors="coerce")
    out["MgO"] = pd.to_numeric(df["MgO"], errors="coerce")
    out["TiO2"] = pd.to_numeric(df["TiO2"], errors="coerce")
    out["Age_Ma"] = pd.to_numeric(df["Age  (Ma)"], errors="coerce")
    out["Setting"] = "ARC"
    return out


def extract_arc_age(df):
    out = pd.DataFrame()
    out["Age_Ma"] = pd.to_numeric(df["Age"], errors="coerce")
    out["Setting"] = "ARC"
    return out


def extract_tornare() -> pd.DataFrame:
    raw = pd.read_csv(folder / "tornare_wholerock.csv", header=None, low_memory=False)
    raw = raw.dropna(how="all").reset_index(drop=True)

    # Row 1 contains sample names, starting in column 2
    sample_names = raw.iloc[1, 2:].dropna().astype(str).str.strip().tolist()

    first_col = raw.iloc[:, 0].astype(str).str.strip()

    def get_row(label: str):
        idx = raw.index[first_col.eq(label)]
        return raw.loc[idx[0]] if len(idx) else None

    rows = {
        "SiO2": get_row("SiO2"),
        "TiO2": get_row("TiO2"),
        "MgO": get_row("MgO"),
    }

    out = []
    for col_idx, sample in enumerate(sample_names, start=2):
        rec = {
            "Sample": sample,
            "Age_Ma": 19.5,   # midpoint of ~14–25 Ma
            "Setting": "HOTSPOT",
            "Source": "Tornare 2016",
        }

        for out_col, row in rows.items():
            if row is not None and col_idx < len(row):
                rec[out_col] = pd.to_numeric(row.iloc[col_idx], errors="coerce")
            else:
                rec[out_col] = pd.NA

        out.append(rec)

    df = pd.DataFrame(out)
    return df

def extract_mccoy() -> pd.DataFrame:
    raw = pd.read_csv(folder / "mccoy_lookout_wholerock.csv", header=None, low_memory=False)
    raw = raw.dropna(how="all").reset_index(drop=True)

    print("\nMcCoy raw preview:")
    print(raw.iloc[:8, :10])

    # Row 1 contains sample names
    sample_names = raw.iloc[1, 1:].dropna().astype(str).str.strip().tolist()

    first_col = raw.iloc[:, 0].astype(str).str.strip()

    def find_row(label: str):
        matches = first_col.str.contains(label, case=False, na=False)
        idx = raw.index[matches]
        return raw.loc[idx[0]] if len(idx) else None

    rows = {
        "SiO2": find_row("SiO2"),
        "TiO2": find_row("TiO2"),
        "MgO": find_row("MgO"),
    }

    print("McCoy sample row: 1")
    for k, v in rows.items():
        print(f"McCoy {k} row:", "FOUND" if v is not None else "MISSING")

    out = []
    for col_idx, sample in enumerate(sample_names, start=1):
        rec = {
            "Sample": sample,
            "Age_Ma": 91.0,   # midpoint of ~82–100 Ma
            "Setting": "HOTSPOT",
            "Source": "McCoy-West 2010",
        }

        for out_col, row in rows.items():
            if row is not None and col_idx < len(row):
                rec[out_col] = pd.to_numeric(row.iloc[col_idx], errors="coerce")
            else:
                rec[out_col] = pd.NA

        out.append(rec)

    df = pd.DataFrame(out)

    df = df.dropna(subset=["SiO2", "TiO2", "MgO"], how="all").copy()

    if "MgO" in df.columns:
        df = df[df["MgO"].isna() | (df["MgO"] < 10)].copy()

    return df

dfs = {key: load_dataset(fname, header_row) for key, (fname, header_row) in files.items()}

print({k: v.shape for k, v in dfs.items()})

arc_age = extract_arc_age(dfs["ARC_AGE"])
tornare = extract_tornare()
mccoy = extract_mccoy()

print("\n==== TORNARE ====")
print(tornare.shape)
print(tornare.head())

print("\n==== MCCOY ====")
print(mccoy.shape)
print(mccoy.head())

morb = extract_basic(dfs["MORB"], "MOR")
oib = extract_basic(dfs["HOTSPOT"], "HOTSPOT")
arc = extract_arc(dfs["ARC"])

df_all = pd.concat([morb, oib, arc, arc_age, tornare, mccoy], ignore_index=True)

df_all = df_all.dropna(subset=["SiO2", "Age_Ma"]).copy()

# ---- SAVE CLEANED DATA ----
OUTPUT_DATA.mkdir(parents=True, exist_ok=True)
df_all.to_csv(OUTPUT_DATA / "cleaned_dataset.csv", index=False)

print("Saved cleaned dataset to:", OUTPUT_DATA / "cleaned_dataset.csv")

bin_size = 50
df_all["Age_Bin"] = ((df_all["Age_Ma"] // bin_size) * bin_size) + (bin_size / 2)

stats = (
    df_all.groupby(["Setting", "Age_Bin"])["SiO2"]
    .agg(
        median="median",
        q25=lambda x: x.quantile(0.25),
        q75=lambda x: x.quantile(0.75),
    )
    .reset_index()
)

print(mccoy.shape)
print(mccoy.head(10))
print(df_all["Setting"].value_counts())

import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))

for setting in stats["Setting"].unique():
    sub = stats[stats["Setting"] == setting]
    plt.plot(sub["Age_Bin"], sub["median"], marker="o", label=setting)
    plt.fill_between(sub["Age_Bin"], sub["q25"], sub["q75"], alpha=0.2)

plt.gca().invert_xaxis()
plt.xlabel("Age (Ma)")
plt.ylabel("SiO2")
plt.legend()
FIG_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(FIG_DIR / "sio2_vs_age.png", dpi=300)
plt.show()