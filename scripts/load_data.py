#!/usr/bin/env python3
"""load_data.py — Load and prep the rainfall dataset for analysis & dashboard."""
import pandas as pd
import sys
sys.path.insert(0, ".")

DATA_PATH = "./data/raw/india_rainfall.csv"

def load_data():
    df = pd.read_csv(DATA_PATH)
    df["season"] = df["season"].astype(str)
    df["division"] = df["division"].astype(str)
    df["year"] = df["year"].astype(int)
    df["rainfall_mm"] = df["rainfall_mm"].astype(float)
    return df

def get_national_trend(df):
    """Compute yearly national average (all divisions)."""
    return (
        df[df["season"] == "ANNUAL"]
        .groupby("year")["rainfall_mm"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={"mean": "national_annual_mean", "std": "national_annual_std"})
    )

if __name__ == "__main__":
    df = load_data()
    trend = get_national_trend(df)
    print(f"Loaded {len(df)} rows")
    print(f"Divisions: {df['division'].nunique()}")
    print(f"Years: {df['year'].min()} – {df['year'].max()}")
    print(f"Seasons: {sorted(df['season'].unique())}")
    print("\nNational annual trend:")
    print(trend.head(5).to_string())
    print("...")
    print(trend.tail(5).to_string())
