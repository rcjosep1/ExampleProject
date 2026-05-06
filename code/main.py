from pathlib import Path
import re
import webbrowser

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


# ============================================================
# Helper functions
# ============================================================

def first_number(series: pd.Series) -> pd.Series:
    """
    Extract the first numeric value from a text field.
    Used for ages that appear as text like '12.3 ± 0.4'.
    """
    extracted = series.astype(str).str.extract(r"(-?\d+(?:\.\d+)?)")[0]
    return pd.to_numeric(extracted, errors="coerce")


def first_numeric(df: pd.DataFrame, candidates: list[str]) -> pd.Series:
    """
    Return the first numeric column that exists from a list of possible names.
    Useful when source files use slightly different headers.
    """
    for col in candidates:
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(index=df.index, dtype="float64")


def get_numeric(df: pd.DataFrame, candidates: list[str]) -> pd.Series:
    """
    As above, but intended for source files where the field may have several variants.
    """
    for col in candidates:
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(index=df.index, dtype="float64")


def mean_numeric_columns(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    """
    Compute the row-wise mean of the columns that exist.
    """
    existing = [c for c in columns if c in df.columns]
    if not existing:
        return pd.Series(index=df.index, dtype="float64")
    numeric = df[existing].apply(pd.to_numeric, errors="coerce")
    return numeric.mean(axis=1)


def geologic_age_to_ma(value):
    """
    Convert broad geological age labels to a representative age in Ma.
    This is a coarse fallback for ARC rows where only era/period labels exist.
    """
    s = str(value).lower()

    mapping = {
        "quaternary": 1,
        "pliocene": 3,
        "miocene": 10,
        "oligocene": 30,
        "eocene": 45,
        "paleocene": 60,
        "cretaceous": 100,
        "jurassic": 170,
        "triassic": 230,
        "permian": 270,
        "carboniferous": 320,
        "devonian": 390,
        "silurian": 430,
        "ordovician": 470,
        "cambrian": 510,
        "proterozoic": 1200,
        "archean": 2600,
    }

    for key, val in mapping.items():
        if key in s:
            return val

    return pd.NA


def build_age(df: pd.DataFrame) -> pd.Series:
    """
    Build a single age series from common age columns.
    Preference order:
    - Age
    - AGE
    - Age (Ma)
    - Published Age
    - Corrected age
    If only min/max ages exist, use the midpoint.
    """
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


# ============================================================
# Paths and source files
# ============================================================

BASE_DIR = Path(r"C:\Users\ramse\Documents\AnacondaProjects\TermProject")
DATA_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DATA = BASE_DIR / "data"
FIG_DIR = BASE_DIR / "figures"
MAP_DIR = FIG_DIR

folder = DATA_DIR

files = {
    "MORB": ("2022_09-0SVW6S_Stracke_MORB.csv", 3),
    "HOTSPOT": ("2022_09-0SVW6S_Stracke_OIB.csv", 0),
    "ARC": ("2021-12_SS1TYI_Woerner_data.csv", 1),
    "ARC_AGE": ("2023-005_e_Pilger_Andean-Igneous-Radiometric-Dates.csv", 0),
}


def load_dataset(fname: str, header_row: int) -> pd.DataFrame:
    """
    Load a source CSV and normalise its column labels.
    """
    df = pd.read_csv(folder / fname, header=header_row, low_memory=False)
    df.columns = [str(col).strip() for col in df.columns]
    return df


# ============================================================
# Core extractors
# ============================================================

def extract_basic(df: pd.DataFrame, setting: str) -> pd.DataFrame:
    """
    Generic extractor for Stracke-style whole-rock compilations.
    Used for MORB and the baseline hotspot file.
    """
    out = pd.DataFrame()

    out["SiO2"] = get_numeric(df, ["SIO2", "SiO2", "SIO2 %", "SiO2 %"])
    out["MgO"] = get_numeric(df, ["MGO", "MgO", "MGO %", "MgO %"])
    out["TiO2"] = get_numeric(df, ["TIO2", "TiO2", "TIO2 %", "TiO2 %"])
    out["K2O"] = get_numeric(df, ["K2O", "K2O %"])

    out["Age_Ma"] = build_age(df)

    out["Latitude"] = first_numeric(df, ["LATITUDE", "Latitude", "Latitude (Y)"])
    out["Longitude"] = first_numeric(df, ["LONGITUDE", "Longitude", "Longitude (X)"])

    out["Setting"] = setting
    return out


def extract_arc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the Woerner ARC compilation and keep only the chemistry/age fields
    needed for the project. Arc ages are taken from the numeric age column when
    present, otherwise converted from broad geological-age labels.
    """
    out = pd.DataFrame()

    out["SiO2"] = pd.to_numeric(df["SiO2"], errors="coerce")
    out["MgO"] = pd.to_numeric(df["MgO"], errors="coerce")
    out["TiO2"] = pd.to_numeric(df["TiO2"], errors="coerce")
    out["K2O"] = get_numeric(df, ["K2O", "K2O %", "K2O(WT%)"])

    age_numeric = first_number(df["Age  (Ma)"])
    age_fallback = (
        df["Geologycal_age"].apply(geologic_age_to_ma)
        if "Geologycal_age" in df.columns
        else pd.Series(pd.NA, index=df.index)
    )
    out["Age_Ma"] = age_numeric.fillna(age_fallback)

    out["Latitude"] = first_numeric(df, ["Latitude (Y)", "Latitude", "LATITUDE"])
    out["Longitude"] = first_numeric(df, ["Longitude (X)", "Longitude", "LONGITUDE"])

    out["Setting"] = "ARC"
    return out


def extract_arc_age(df: pd.DataFrame) -> pd.DataFrame:
    """
    Age-only ARC compilation. This is loaded for reference, but it does not
    contribute to the current chemistry plots because it has no SiO2 column.
    """
    out = pd.DataFrame()
    out["Age_Ma"] = first_number(df["Age"])
    out["Setting"] = "ARC"
    return out


# ============================================================
# Proxy coordinates for datasets without explicit lat/lon
# ============================================================

# Tornare: Fuerteventura, Canary Islands
TORNARE_LAT = 28.3587
TORNARE_LON = -14.0537

# McCoy-West: Middlehurst Stream / Marlborough, South Island, New Zealand
MCCOY_LAT = -(41 + 58 / 60 + 41.9 / 3600)   # -41.9783056
MCCOY_LON = 173 + 30 / 60                   # 173.5


def extract_tornare() -> pd.DataFrame:
    """
    Extract Tornare major-element data and attach a single proxy location.
    """
    raw = pd.read_csv(folder / "tornare_wholerock.csv", header=None, low_memory=False)
    raw = raw.dropna(how="all").reset_index(drop=True)

    sample_names = raw.iloc[1, 2:].dropna().astype(str).str.strip().tolist()
    first_col = raw.iloc[:, 0].astype(str).str.strip()

    def get_row(label: str):
        idx = raw.index[first_col.eq(label)]
        return raw.loc[idx[0]] if len(idx) else None

    rows = {
        "SiO2": get_row("SiO2"),
        "TiO2": get_row("TiO2"),
        "MgO": get_row("MgO"),
        "K2O": get_row("K2O"),
    }

    out = []
    for col_idx, sample in enumerate(sample_names, start=2):
        rec = {
            "Sample": sample,
            "Age_Ma": 19.5,
            "Latitude": TORNARE_LAT,
            "Longitude": TORNARE_LON,
            "Setting": "HOTSPOT",
            "Source": "Tornare 2016",
        }

        for out_col, row in rows.items():
            if row is not None and col_idx < len(row):
                rec[out_col] = pd.to_numeric(row.iloc[col_idx], errors="coerce")
            else:
                rec[out_col] = pd.NA

        out.append(rec)

    return pd.DataFrame(out)


def extract_mccoy() -> pd.DataFrame:
    """
    Extract McCoy-West whole-rock data and attach a single proxy location.
    """
    raw = pd.read_csv(folder / "mccoy_lookout_wholerock.csv", header=None, low_memory=False)
    raw = raw.dropna(how="all").reset_index(drop=True)

    print("\nMcCoy raw preview:")
    print(raw.iloc[:8, :10])

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
        "K2O": find_row("K2O"),
    }

    out = []
    for col_idx, sample in enumerate(sample_names, start=1):
        rec = {
            "Sample": sample,
            "Age_Ma": 91.0,
            "Latitude": MCCOY_LAT,
            "Longitude": MCCOY_LON,
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


def extract_petdb() -> pd.DataFrame:
    """
    Extract the Reese/PetDB CSV and map PetDB geologic environments into the
    project-wide settings.
    """
    df = pd.read_csv(folder / "PetDB Data.csv", header=2, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]

    out = pd.DataFrame()

    out["SiO2"] = pd.to_numeric(df["SiO2 %"], errors="coerce")
    out["TiO2"] = pd.to_numeric(df["TiO2 %"], errors="coerce")
    out["MgO"] = pd.to_numeric(df["MgO %"], errors="coerce")
    out["K2O"] = pd.to_numeric(df["K2O %"], errors="coerce")

    out["Age_Ma"] = pd.to_numeric(df["Age(Ma)"], errors="coerce")
    out["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    out["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

    geo = df["Geologic Environment"].astype(str).str.lower()

    out["Setting"] = pd.NA
    out.loc[geo.str.contains("spreading center|off axis spreading center", na=False), "Setting"] = "MOR"
    out.loc[geo.str.contains("volcanic arc|convergent margin", na=False), "Setting"] = "ARC"
    out.loc[geo.str.contains("seamount|intraplate craton|intraplate off-craton", na=False), "Setting"] = "HOTSPOT"

    out = out.dropna(subset=["Setting", "SiO2", "Age_Ma"]).copy()
    return out


# ============================================================
# Qin hotspot subset
# ============================================================

qin = pd.read_csv(folder / "2024-007_AVAW2Y_Qin_Major Elements.csv", header=3, low_memory=False)
qin.columns = [c.strip() for c in qin.columns]


def find_col(df, candidates):
    lookup = {c.strip().lower(): c for c in df.columns}
    for cand in candidates:
        key = cand.strip().lower()
        if key in lookup:
            return lookup[key]
    raise KeyError(f"None of these columns were found: {candidates}")


location_col = find_col(qin, ["LOCATION", "Location", "location"])
setting_col = find_col(qin, ["TECTONIC SETTING", "Tectonic Setting", "TECTONIC_SETTING"])

lat_min_col = find_col(qin, ["LATITUDE (MIN.)"])
lat_max_col = find_col(qin, ["LATITUDE (MAX.)"])
lon_min_col = find_col(qin, ["LONGITUDE (MIN.)"])
lon_max_col = find_col(qin, ["LONGITUDE (MAX.)"])

qin[location_col] = qin[location_col].astype(str).str.upper()
qin[setting_col] = qin[setting_col].astype(str).str.upper()

# Broad hotspot / LIP / intraplate candidates.
hotspot_keywords = [
    "ONTONG JAVA",
    "KERGUELEN",
    "ETHIOPIAN PLATEAU",
    "HYBLEAN PLATEAU",
    "CAMEROON LINE",
    "ADAMAWA",
    "KAPSIKI PLATEAU",
    "MANIHIKI",
    "CARIBBEAN",
    "SHATSKY",
    "KAROO",
    "FERRAR",
]

hotspot_pattern = "|".join(re.escape(k) for k in hotspot_keywords)
hotspot_settings = [
    "OCEANIC PLATEAU",
    "INTRAPLATE VOLCANICS",
    "OCEAN ISLAND",
    "SEAMOUNT",
    "CONTINENTAL FLOOD BASALT",
]

mask = (
    qin[location_col].str.contains(hotspot_pattern, na=False)
    & qin[setting_col].isin(hotspot_settings)
)

qin_hotspot = qin.loc[mask].copy()

# Remove obvious mantle / xenolith material.
bad_keywords = ["XENOLITH", "PERIDOTITE", "HARZBURGITE", "LHERZOLITE"]
bad_pattern = "|".join(re.escape(k) for k in bad_keywords)
qin_hotspot = qin_hotspot.loc[~qin_hotspot[location_col].str.contains(bad_pattern, na=False)].copy()

print("=== Qin hotspot subset: LOCATION ===")
print(qin_hotspot[location_col].value_counts().head(20))

print("\n=== Qin hotspot subset: SETTINGS ===")
print(qin_hotspot[setting_col].value_counts())

print("\n=== Qin hotspot subset: SAMPLE COUNT ===")
print(len(qin_hotspot))
print(qin_hotspot[location_col].value_counts().head(20))

# Keep only the systems currently used in the project.
keep_mask = (
    qin_hotspot[location_col].str.contains("ONTONG JAVA", na=False) |
    qin_hotspot[location_col].str.contains("KERGUELEN", na=False) |
    qin_hotspot[location_col].str.contains("ETHIOPIAN", na=False) |
    qin_hotspot[location_col].str.contains("KAROO|FERRAR", na=False)
)

qin_hotspot = qin_hotspot.loc[keep_mask].copy()

# Exclude intrusive/plutonic and xenolith material.
qin_hotspot = qin_hotspot[
    ~qin_hotspot[location_col].str.contains("GABBRO|PLUTONIC", na=False)
].copy()

qin_hotspot = qin_hotspot[
    ~qin_hotspot[location_col].str.contains("XENOLITH", na=False)
].copy()

# Balance the largest systems so they do not dominate the quartiles.
max_per_group = 40
parts = []
for _, grp in qin_hotspot.groupby(location_col):
    parts.append(grp.sample(min(len(grp), max_per_group), random_state=0))
qin_hotspot = pd.concat(parts, ignore_index=True)

print("\n=== After downsampling ===")
print(qin_hotspot[location_col].value_counts())


def assign_age(loc):
    """
    Assign a representative age to each chosen Qin hotspot system.
    """
    if "ONTONG JAVA" in loc:
        return 122
    elif "KERGUELEN" in loc:
        return 115
    elif "ETHIOPIAN" in loc:
        return 30
    elif "KAROO" in loc or "FERRAR" in loc:
        return 180
    else:
        return None


qin_hotspot["Age_Ma"] = qin_hotspot[location_col].apply(assign_age)
qin_hotspot["Setting"] = "HOTSPOT"

# Use the midpoint of latitude/longitude ranges as a plotting proxy.
qin_hotspot["Latitude"] = mean_numeric_columns(qin_hotspot, [lat_min_col, lat_max_col])
qin_hotspot["Longitude"] = mean_numeric_columns(qin_hotspot, [lon_min_col, lon_max_col])

qin_hotspot["SiO2"] = pd.to_numeric(qin_hotspot["SIO2(WT%)"], errors="coerce")
qin_hotspot["TiO2"] = pd.to_numeric(qin_hotspot["TIO2(WT%)"], errors="coerce")
qin_hotspot["MgO"] = pd.to_numeric(qin_hotspot["MGO(WT%)"], errors="coerce")

qin_hotspot = qin_hotspot[
    ["SiO2", "TiO2", "MgO", "Age_Ma", "Latitude", "Longitude", "Setting"]
]


# ============================================================
# Load the compiled source datasets
# ============================================================

dfs = {key: load_dataset(fname, header_row) for key, (fname, header_row) in files.items()}
print({k: v.shape for k, v in dfs.items()})

arc_age = extract_arc_age(dfs["ARC_AGE"])
tornare = extract_tornare()
mccoy = extract_mccoy()
petdb = extract_petdb()

print("\n==== PETDB ====")
print(petdb.shape)
print(petdb["Setting"].value_counts())
print(petdb.head())

print("\n==== TORNARE ====")
print(tornare.shape)
print(tornare.head())

print("\n==== MCCOY ====")
print(mccoy.shape)
print(mccoy.head())

morb = extract_basic(dfs["MORB"], "MOR")
oib = extract_basic(dfs["HOTSPOT"], "HOTSPOT")
arc = extract_arc(dfs["ARC"])

# ARC rock-type filter: keep the basaltic / basaltic-andesite subset.
if "Rock_type" in dfs["ARC"].columns:
    arc["Rock_type"] = dfs["ARC"]["Rock_type"].reset_index(drop=True).astype(str)
    arc = arc.reset_index(drop=True)

    print("\nARC rock types:")
    print(arc["Rock_type"].value_counts().head(30))

    keep = arc["Rock_type"].str.contains(
        r"basalt|basaltic|tholeiit|tholeiite|basaltic andesite",
        case=False,
        na=False
    )
    arc = arc.loc[keep].copy()


# ============================================================
# Merge the cleaned data into one table
# ============================================================

df_all = pd.concat(
    [
        morb,
        oib,
        arc,
        arc_age,      # age-only reference; currently dropped later because it lacks SiO2
        tornare,
        mccoy,
        qin_hotspot,
        petdb,
    ],
    ignore_index=True
)

df_all = df_all.dropna(subset=["SiO2", "Age_Ma"]).copy()

print(df_all["Setting"].value_counts())
print(df_all.groupby("Setting")[["Latitude", "Longitude"]].count())

# Save the cleaned dataset. Move this below Age_Bin if you want the bin column in the CSV.
OUTPUT_DATA.mkdir(parents=True, exist_ok=True)
df_all.to_csv(OUTPUT_DATA / "cleaned_dataset.csv", index=False)
print("Saved cleaned dataset to:", OUTPUT_DATA / "cleaned_dataset.csv")

# 50 Ma age bins, centred on the midpoint of each bin.
bin_size = 50
df_all["Age_Bin"] = ((df_all["Age_Ma"] // bin_size) * bin_size) + (bin_size / 2)


# ============================================================
# Map plotting
# ============================================================

MAP_DIR.mkdir(parents=True, exist_ok=True)

map_df = df_all.dropna(subset=["Latitude", "Longitude", "Age_Bin"]).copy()
map_df["Setting"] = map_df["Setting"].replace({"MOR": "MORB"})

bin_order = sorted(map_df["Age_Bin"].dropna().unique().tolist())

for setting in ["MORB", "ARC", "HOTSPOT"]:
    sub = map_df[map_df["Setting"] == setting].copy()

    if sub.empty:
        print(f"No coordinate data available for {setting}")
        continue

    sub["Age_Bin"] = pd.Categorical(sub["Age_Bin"], categories=bin_order, ordered=True)

    fig = px.scatter_geo(
        sub,
        lat="Latitude",
        lon="Longitude",
        color="Age_Bin",
        category_orders={"Age_Bin": bin_order},
        color_discrete_sequence=px.colors.qualitative.Bold,
        projection="natural earth",
        title=f"{setting} samples coloured by 50 Ma age bin",
        hover_data=["Age_Ma", "Age_Bin", "SiO2", "TiO2", "MgO", "Source"],
    )

    fig.update_traces(
        marker=dict(
            size=8,
            opacity=1.0,
            line=dict(width=0.8, color="black")
        )
    )
    fig.update_geos(
        showland=True,
        landcolor="rgb(240,240,240)",
        showcountries=True,
        showocean=True,
        oceancolor="rgb(220,235,245)",
    )

    out_html = MAP_DIR / f"{setting.lower()}_map.html"
    fig.write_html(out_html)
    print(f"Saved map to {out_html}")
    webbrowser.open_new_tab(out_html.as_uri())


# ============================================================
# Element-versus-age plots
# ============================================================

def plot_element_vs_age(df: pd.DataFrame, element: str, outpath: Path, ylabel: str | None = None):
    """
    Plot median and interquartile range of one element versus age bin.
    """
    if ylabel is None:
        ylabel = element

    stats = (
        df.dropna(subset=[element, "Age_Bin"])
        .groupby(["Setting", "Age_Bin"])[element]
        .agg(
            median="median",
            q25=lambda x: x.quantile(0.25),
            q75=lambda x: x.quantile(0.75),
        )
        .reset_index()
        .sort_values(["Setting", "Age_Bin"])
    )

    plt.figure(figsize=(8, 5))

    for setting in stats["Setting"].unique():
        sub = stats[stats["Setting"] == setting]

        plt.plot(sub["Age_Bin"], sub["median"], marker="o", label=setting)
        plt.fill_between(sub["Age_Bin"], sub["q25"], sub["q75"], alpha=0.2)

    plt.gca().invert_xaxis()
    plt.xlabel("Age (Ma, bin center)")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.show()


# Generate the element plots used in the notebook/report.
plot_element_vs_age(df_all, "SiO2", FIG_DIR / "sio2_vs_age.png", ylabel="SiO2")
plot_element_vs_age(df_all, "MgO", FIG_DIR / "mgo_vs_age.png", ylabel="MgO")
plot_element_vs_age(df_all, "TiO2", FIG_DIR / "tio2_vs_age.png", ylabel="TiO2")
plot_element_vs_age(df_all, "K2O", FIG_DIR / "k2o_vs_age.png", ylabel="K2O")