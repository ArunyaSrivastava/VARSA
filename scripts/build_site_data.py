#!/usr/bin/env python3
"""
build_site_data.py — export VARSA data as compact JSON for the static web app.

Reads the repo's data layers and writes everything site/data/ needs:
  subdivisions.json — 36 IMD subdivision polygons (already simplified)
  values.json       — {(season): {(year): {(division): [mm, dep, layer]}}}
  national.json     — all-India annual + monsoon series 1901-2026
  meta.json         — KPIs, 2026 banner values, season definitions

Run after fetch_observed.py; regenerates any time the data changes.

Usage:
    python scripts/build_site_data.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
SITE = BASE / "site" / "data"
GEO = BASE / "data" / "geo" / "imd_subdivisions.geojson"
PIPE = BASE / "data" / "raw" / "india_rainfall.csv"
OBS = BASE / "data" / "raw" / "imd_observed_subdivisions.csv"
MON = BASE / "data" / "raw" / "imd_all_india_monsoon.csv"
ANN = BASE / "data" / "raw" / "imd_all_india_monthly.csv"

SEASON_MAP = {  # display label -> (pipeline season, observed season)
    "Monsoon": ("JAS", "MONSOON"),
    "Annual": ("ANNUAL", "ANNUAL"),
    "Winter": ("DJF", "WINTER"),
    "Pre-monsoon": ("MAM", "PREMONSOON"),
    "Post-monsoon": ("OND", "POSTMONSOON"),
}

DIV_MAP = {
    "Orissa": "ODISHA", "Coastal Odisha": "ODISHA",
    "Uttarakhand": "UTTARAKHAND", "Uttaranchal": "UTTARAKHAND",
    "Gangetic West Bengal": "GANGETIC W.B.",
    "Sub-Montane West Bengal": "SUB-HIMALAYAN W.B. & SIKKIM",
    "Sikkim": "SUB-HIMALAYAN W.B. & SIKKIM",
    "Jammu & Kashmir": "JAMMU & KASHMIR", "Ladakh": "JAMMU & KASHMIR",
    "Cold Desert (HP & UK)": "HIMACHAL PRADESH",
    "Haryana, Delhi & Chandigarh": "HARYANA-CHD-DELHI",
    "East Uttar Pradesh": "EAST U.P.", "West Uttar Pradesh": "WEST U.P.",
    "North West Uttar Pradesh": "WEST U.P.",
    "East Rajasthan": "EAST RAJASTHAN", "West Rajasthan": "WEST RAJASTHAN",
    "Madhya Bharat": "WEST M.P.", "Madhya Maharashtra": "MADHYA MAHARASHTRA",
    "Chhattisgarh": "CHHATTISGARH", "Bihar": "BIHAR", "Jharkhand": "JHARKHAND",
    "Coast Andhra Pradesh": "COASTAL A.P.",
    "Telangana": "TELANGANA", "Rayalaseema": "RAYALASEEMA",
    "Tamil Nadu": "TAMIL NADU", "Coastal Karnataka": "COASTAL KARNATAKA",
    "North Interior Karnataka": "NORTH INTERIOR KARNATAKA",
    "South Interior Karnataka": "SOUTH INTERIOR KARNATAKA",
    "Kerala": "KERALA", "Lakshadweep": "LAKSHADWEEP",
    "Arunachal Pradesh": "ARUNACHAL PRADESH", "Assam & Meghalaya": "ASSAM & MEGHALAYA",
    "Himachal Pradesh": "HIMACHAL PRADESH", "Punjab": "PUNJAB",
    "Gujarat Region": "GUJARAT REGION", "Konkan & Goa": "KONKAN & GOA",
    "Vidarbha": "VIDARBHA", "Marathwada": "MARATHAWADA",
}


def main():
    SITE.mkdir(parents=True, exist_ok=True)

    # ── polygons ────────────────────────────────────────────────────────────
    geo = json.loads(GEO.read_text(encoding="utf-8"))
    polys = []
    for f in geo["features"]:
        g = f["geometry"]
        rings = [g["coordinates"]] if g["type"] == "Polygon" else \
            [p for p in g["coordinates"] if p and len(p[0]) >= 4]
        flat = []
        for ring in rings:
            flat.append([[round(pt[0], 4), round(pt[1], 4)] for pt in ring[0]])
        polys.append({"division": f["properties"]["division"],
                      "region": f["properties"]["region"], "rings": flat})
    (SITE / "subdivisions.json").write_text(json.dumps(polys))
    print(f"subdivisions.json: {len(polys)} divisions "
          f"({(SITE / 'subdivisions.json').stat().st_size / 1e6:.2f} MB)")

    # ── unified values ──────────────────────────────────────────────────────
    pipe = pd.read_csv(PIPE)
    frames = []
    for label, (p_season, _o) in SEASON_MAP.items():
        q = pipe[pipe["season"] == p_season][["year", "division", "rainfall_mm"]]
        frames.append(pd.DataFrame({
            "year": q["year"], "division": q["division"].map(lambda d: DIV_MAP.get(d, d.upper())),
            "season": label, "mm": q["rainfall_mm"], "dep": np.nan, "obs": 0}))
    unified = pd.concat(frames, ignore_index=True)

    if OBS.exists():
        obs = pd.read_csv(OBS)
        inv = {o: label for label, (_p, o) in SEASON_MAP.items()}
        frames = []
        for label, (_p, o_season) in SEASON_MAP.items():
            q = obs[obs["season"] == o_season]
            frames.append(pd.DataFrame({
                "year": q["year"], "division": q["division"], "season": label,
                "mm": q["actual_mm"], "dep": q["pct_dep"], "obs": 1}))
        obs_u = pd.concat(frames, ignore_index=True)
        unified = pd.concat([unified[unified["year"] <= 2015], obs_u[obs_u["year"] > 2015]],
                            ignore_index=True)
    # aggregate divisions that fold together (J&K+Ladakh etc.); mean values
    unified = unified.groupby(["season", "year", "division"], as_index=False).agg(
        mm=("mm", "mean"), dep=("dep", "mean"), obs=("obs", "max"))
    # pipeline anomaly vs long-run division mean, per season
    pipe_mask = unified["obs"] == 0
    means = unified[pipe_mask].groupby(["season", "division"])["mm"].mean()
    def _anom(r):
        if r["obs"] == 1 or (r["season"], r["division"]) not in means.index:
            return r["dep"]
        m = means.loc[(r["season"], r["division"])]
        return 100 * (r["mm"] - m) / m if m else None
    unified["dep"] = unified.apply(_anom, axis=1)

    values = {}
    for (season, year), grp in unified.groupby(["season", "year"]):
        values.setdefault(season, {})[str(int(year))] = {
            r["division"]: [round(r["mm"], 1) if pd.notna(r["mm"]) else None,
                            round(r["dep"], 1) if pd.notna(r["dep"]) else None,
                            int(r["obs"])]
            for _i, r in grp.iterrows()}
    (SITE / "values.json").write_text(json.dumps(values))
    print(f"values.json: {sum(len(y) for s in values.values() for y in s.values())} cells "
          f"({(SITE / 'values.json').stat().st_size / 1e6:.2f} MB)")

    # ── national series ─────────────────────────────────────────────────────
    ann = pd.read_csv(ANN)
    ai_annual = ann[(ann["region"] == "ALL INDIA") & (ann["month"] == "ANNUAL")] \
        .set_index("year")["rainfall_mm"]
    mon = pd.read_csv(MON)
    ai_mon = mon[mon["region"] == "ALL INDIA"].set_index("year")
    years = sorted(set(ai_annual.index) | set(ai_mon.index))
    national = {
        "years": [int(y) for y in years],
        "annual": [round(float(ai_annual.get(y, np.nan)), 1) if y in ai_annual.index else None
                   for y in years],
        "monsoon": [round(float(ai_mon["jun_sep"].get(y, np.nan)), 1) if y in ai_mon.index else None
                    for y in years],
        "monsoon_dep": [round(float(ai_mon["jun_sep_dep"].get(y, np.nan)), 1) if y in ai_mon.index else None
                        for y in years],
    }
    (SITE / "national.json").write_text(json.dumps(national))
    print(f"national.json: {len(years)} years")

    # ── meta (KPIs + live banner) ───────────────────────────────────────────
    latest = ai_mon.iloc[-1]
    meta = {
        "seasons": list(SEASON_MAP.keys()),
        "latest_year": int(ai_mon.index.max()),
        "latest_monsoon_mm": round(float(latest["jun_sep"]), 1),
        "latest_monsoon_dep": round(float(latest["jun_sep_dep"]), 1),
        "kpis": [
            {"v": "73.7%", "l": "of rain falls Jun–Sep", "note": "seasonality"},
            {"v": "η² = 0.861", "l": "variance explained by region", "note": "Welch ANOVA"},
            {"v": "13.6–70.3%", "l": "CV across subdivisions", "note": "Kerala → Ladakh"},
            {"v": "15.8%", "l": "1-in-20-yr level, W. Rajasthan", "note": "drought risk is local"},
            {"v": "0 / 36", "l": "trends after BH correction", "note": "null result, reported"},
        ],
    }
    (SITE / "meta.json").write_text(json.dumps(meta))
    print("meta.json: banner", meta["latest_year"], meta["latest_monsoon_dep"], "%")


if __name__ == "__main__":
    main()
