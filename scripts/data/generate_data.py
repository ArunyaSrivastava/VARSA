#!/usr/bin/env python3
"""
generate_data.py — Generate a realistic IMD-style rainfall dataset for 36
meteorological subdivisions of India (1901–2015).

This script produces `data/raw/india_rainfall.csv` which is the single source
of truth for the Streamlit dashboard. Values are synthetic but statistically
plausible: each subdivision gets a distinct mean, seasonal cycle, and trend,
so the dashboard can show meaningful differences between regions.
"""

import numpy as np
import pandas as pd

# --- 36 Meteorological Subdivisions of India (IMD) ---
SUB_DIVISIONS = [
    "Arunachal Pradesh",
    "Assam & Meghalaya",
    "Coastal Karnataka",
    "Coast Andhra Pradesh",
    "Coastal Odisha",
    "Cold Desert (HP & UK)",
    "East Rajasthan",
    "East Uttar Pradesh",
    "Gujarat Region",
    "Haryana, Delhi & Chandigarh",
    "Himachal Pradesh",
    "Jammu & Kashmir",
    "Jharkhand",
    "Kerala",
    "Konkan & Goa",
    "Lakshadweep",
    "Madhya Maharashtra",
    "Madhya Bharat",
    "North Interior Karnataka",
    "North West Uttar Pradesh",
    "Orissa",
    "Rayalaseema",
    "South Interior Karnataka",
    "Tamil Nadu",
    "Telangana",
    "West Rajasthan",
    "West Uttar Pradesh",
    "Bihar",
    "Chhattisgarh",
    "Gangetic West Bengal",
    "Ladakh",
    "Sikkim",
    "Sub-Montane West Bengal",
    "Uttarakhand",
    "Vidarbha",
    "Marathwada",
]

# Rough climatology: mean annual rainfall (mm) and CV% for each subdivision
CLIMATOLOGY = {
    "Arunachal Pradesh": (3000, 0.20),
    "Assam & Meghalaya": (2500, 0.15),
    "Coastal Karnataka": (3200, 0.22),
    "Coast Andhra Pradesh": (1000, 0.24),
    "Coastal Odisha": (1200, 0.23),
    "Cold Desert (HP & UK)": (500, 0.35),
    "East Rajasthan": (600, 0.33),
    "East Uttar Pradesh": (800, 0.28),
    "Gujarat Region": (600, 0.30),
    "Haryana, Delhi & Chandigarh": (650, 0.26),
    "Himachal Pradesh": (1200, 0.25),
    "Jammu & Kashmir": (650, 0.32),
    "Jharkhand": (1100, 0.26),
    "Kerala": (3000, 0.14),
    "Konkan & Goa": (3500, 0.20),
    "Lakshadweep": (1200, 0.28),
    "Madhya Maharashtra": (1200, 0.28),
    "Madhya Bharat": (800, 0.28),
    "North Interior Karnataka": (600, 0.30),
    "North West Uttar Pradesh": (600, 0.30),
    "Orissa": (1200, 0.25),
    "Rayalaseema": (500, 0.32),
    "South Interior Karnataka": (700, 0.28),
    "Tamil Nadu": (900, 0.25),
    "Telangana": (750, 0.27),
    "West Rajasthan": (300, 0.40),
    "West Uttar Pradesh": (700, 0.27),
    "Bihar": (1000, 0.26),
    "Chhattisgarh": (1100, 0.27),
    "Gangetic West Bengal": (1400, 0.24),
    "Ladakh": (100, 0.50),
    "Sikkim": (2000, 0.22),
    "Sub-Montane West Bengal": (1800, 0.21),
    "Uttarakhand": (1500, 0.24),
    "Vidarbha": (800, 0.29),
    "Marathwada": (500, 0.31),
}

SEASONS = {
    "JAS": "Monsoon (Jun–Sep)",
    "OND": "Post-Monsoon (Oct–Dec)",
    "MAM": "Pre-Monsoon (Mar–May)",
    "DJF": "Winter (Dec–Feb)",
    "ANNUAL": "Annual",
}


def generate_subdivision_years(seed: int, n_years: int = 115):
    """Generate annual rainfall for one subdivision across n_years (1901-based)."""
    rng = np.random.default_rng(seed)
    base_mean, cv = CLIMATOLOGY[list(CLIMATOLOGY.keys())[seed % len(CLIMATOLOGY)]]
    trend = rng.uniform(-0.3, 0.8)  # mm/year change
    years = np.arange(1901, 1901 + n_years)
    annual = base_mean * (1 + rng.normal(0, cv, n_years))
    annual = annual + trend * (years - 1901)
    annual = annual + 200 * np.sin(2 * np.pi * (years - 1901) / 30)
    annual = np.clip(annual, 50, None)
    return pd.DataFrame({
        "year": years,
        "division": list(CLIMATOLOGY.keys())[seed % len(CLIMATOLOGY)],
        "rainfall_mm": annual.astype(float),
    })


def generate_seasonal_data(seed: int, n_years: int = 115):
    """Generate seasonal rainfall for one subdivision."""
    rng = np.random.default_rng(seed + 1000)
    base_mean, cv = CLIMATOLOGY[list(CLIMATOLOGY.keys())[seed % len(CLIMATOLOGY)]]
    years = np.arange(1901, 1901 + n_years)
    sub = list(CLIMATOLOGY.keys())[seed % len(CLIMATOLOGY)]
    jas_frac = rng.uniform(0.68, 0.80)
    ond_frac = rng.uniform(0.10, 0.16)
    mam_frac = rng.uniform(0.05, 0.09)
    djf_frac = 1.0 - jas_frac - ond_frac - mam_frac
    jas = base_mean * jas_frac * (1 + rng.normal(0, cv * 0.5, n_years))
    ond = base_mean * ond_frac * (1 + rng.normal(0, cv * 0.6, n_years))
    mam = base_mean * mam_frac * (1 + rng.normal(0, cv * 0.5, n_years))
    djf = base_mean * djf_frac * (1 + rng.normal(0, cv * 0.5, n_years))
    return pd.DataFrame({
        "year": np.tile(years, 4),
        "division": sub,
        "season": ["JAS"] * n_years + ["OND"] * n_years + ["MAM"] * n_years + ["DJF"] * n_years,
        "rainfall_mm": np.concatenate([jas, ond, mam, djf]),
    })


def main():
    n_years = 115  # 1901 to 2015 inclusive = 115 years
    all_data = []
    for i, subdivision in enumerate(SUB_DIVISIONS):
        ann = generate_subdivision_years(i, n_years)
        all_data.append(ann)
        seas = generate_seasonal_data(i, n_years)
        all_data.append(seas)
    df = pd.concat(all_data, ignore_index=True)
    df = df.sort_values(["season", "division", "year"]).reset_index(drop=True)
    out_path = "data/raw/india_rainfall.csv"
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} rows -> {out_path}")
    print(f"  Years: {df['year'].min()} - {df['year'].max()}")
    print(f"  Divisions: {df['division'].nunique()}")
    print(f"  Seasons: {sorted(df['season'].unique())}")


if __name__ == "__main__":
    main()
