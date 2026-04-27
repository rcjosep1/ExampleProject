from __future__ import annotations

import numpy as np
import pandas as pd


def clean_sample_name(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.replace('="', "", regex=False)
        .str.replace('"', "", regex=False)
        .str.strip()
    )


def to_num(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="float64")
    return pd.to_numeric(series, errors="coerce")


def first_valid(series: pd.Series):
    cleaned = series.dropna()
    if cleaned.empty:
        return np.nan
    return cleaned.iloc[0]


def collapse(df: pd.DataFrame, key: str) -> pd.DataFrame:
    cols = [column for column in df.columns if column != key]
    return df.groupby(key, as_index=False)[cols].agg(first_valid)


def standardize_setting(value) -> str | float:
    if pd.isna(value):
        return np.nan

    text = str(value).upper()
    if "SPREADING" in text or "RIDGE" in text:
        return "MOR"
    if "ARC" in text:
        return "ARC"
    if "OCEAN ISLAND" in text or "SEAMOUNT" in text:
        return "HOTSPOT"
    return "OTHER"


def compute_age(row: pd.Series):
    age = row.get("Geologic Age")
    if pd.notna(age):
        return age

    min_age = row.get("Geologic Age Min (Ma)")
    max_age = row.get("Geologic Age Max (Ma)")

    if pd.notna(min_age) and pd.notna(max_age):
        return (min(min_age, max_age) + max(min_age, max_age)) / 2
    if pd.notna(min_age):
        return min_age
    if pd.notna(max_age):
        return max_age
    return np.nan
