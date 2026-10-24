#!/usr/bin/env python3
"""
test_date_coverage.py — automated tests for 2015–2026 date-range handling and
missing-data behavior across the VARSA data layers.

Run:  python scripts/test_date_coverage.py
Exit code 0 = all pass, 1 = failures.

Covers:
  T1  observed subdivision layer: years 2015-2025, 2020 absent (quality gate)
  T2  observed values revalidate against IMD's printed % departures
  T3  unified loader spans 1901-2025 with provenance tags on every row
  T4  per-division observed lookup: 10 observed years, winter excluded by default
  T5  national extended series: annual 1901-2025, monsoon through 2026 (provisional)
  T6  national annual for 2026 is ABSENT (incomplete year never mixed in)
  T7  site values.json: 2016-2025 present / 2020 absent / no 2026 subdivision values
  T8  site national.json: monsoon reaches 2026; annual ends 2025
  T9  no fabricated values: observed row count matches IMD source tables exactly
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

RAW = BASE / "data" / "raw"
SITE = BASE / "site" / "data"

FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


# ── T1: observed subdivision layer shape ─────────────────────────────────────
obs = pd.read_csv(RAW / "imd_observed_subdivisions.csv")
years = sorted(int(y) for y in obs["year"].unique())
EXPECTED_YEARS = [2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025]
check("T1a observed years = 2015-2025 minus 2020 (gate)", years == EXPECTED_YEARS, str(years))
check("T1b 2020 quality-gated out", 2020 not in years)
check("T1c 36 divisions present", obs["division"].nunique() == 36)
check("T1d five series per division-year", set(obs["season"].unique()) ==
      {"WINTER", "PREMONSOON", "MONSOON", "POSTMONSOON", "ANNUAL"})

# ── T2: departure revalidation (scale-aware) ─────────────────────────────────
c = obs.dropna(subset=["actual_mm", "normal_mm", "pct_dep"])
c = c[c["normal_mm"] > 0].copy()
c["dep_calc"] = (c["actual_mm"] / c["normal_mm"] - 1) * 100
c["tol"] = 1.5 + 10.0 / c["normal_mm"]
bad = c[(c["dep_calc"] - c["pct_dep"]).abs() > c["tol"]]
check("T2 all cells revalidate vs printed departures", len(bad) == 0,
      f"{len(bad)} bad: {bad.head(3).to_dict('records')}")

# ── T3+T4: app data service (extracted via AST to avoid running Streamlit) ──
import ast
import types

src = (BASE / "app.py").read_text(encoding="utf-8")
tree = ast.parse(src)
wanted = {"load_unified_subdivisions", "observed_rows_for_division",
          "load_national_extended", "PIPE_TO_CANON", "PRISM_SEASONS",
          "OBS_SEASONS_MERGEABLE"}
segments = [ast.get_source_segment(src, n) for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.Assign))
            and (getattr(n, "name", None) in wanted
                 or (isinstance(n, ast.Assign)
                     and getattr(n.targets[0], "id", "") in wanted))]


def _cache_stub(*a, **k):
    return a[0] if (a and callable(a[0])) else (lambda f: f)


ns = {"pd": pd, "np": np, "st": types.SimpleNamespace(cache_data=_cache_stub),
      "BASE_DIR": BASE, "DATA_PATH": RAW / "india_rainfall.csv",
      "GEO_SUBDIVISIONS": BASE / "data" / "geo" / "imd_subdivisions.geojson",
      "OBS_SUBDIVISIONS": RAW / "imd_observed_subdivisions.csv",
      "OBS_NATIONAL_MONSOON": RAW / "imd_all_india_monsoon.csv",
      "OBS_NATIONAL_MONTHLY": RAW / "imd_all_india_monthly.csv"}
for seg in segments:
    exec(seg, ns)


def _load_data():
    d = pd.read_csv(RAW / "india_rainfall.csv")
    d["season"] = d["season"].astype(str)
    return d


ns["load_data"] = _load_data
ns["df"] = _load_data()

uni = ns["load_unified_subdivisions"]()
uni_ann = uni[uni["season"] == "Annual"]
check("T3a unified annual spans 1901-2025", uni_ann["year"].min() == 1901
      and uni_ann["year"].max() == 2025,
      f"{uni_ann['year'].min()}-{uni_ann['year'].max()}")
obs_rows = uni[uni["layer"] == "observed IMD"]
check("T3b every unified row carries a layer tag", uni["layer"].notna().all())
check("T3c observed rows only in 2016-2025 (minus 2020)",
      set(int(y) for y in obs_rows["year"].unique()) ==
      {2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025})
check("T3d no observed 2020 rows (gate honoured)", 2020 not in set(obs_rows["year"]))

kerala = ns["observed_rows_for_division"]("KERALA")
check("T4a Kerala observed lookup: 10 annual rows",
      int((kerala["season"] == "ANNUAL").sum()) == 10)
check("T4b winter excluded by default",
      "DJF" not in set(kerala["season"]))
kerala_all = ns["observed_rows_for_division"]("KERALA", include_winter=True)
check("T4c winter included on request",
      "DJF" in set(kerala_all["season"]))
check("T4d unmatched canonical name returns empty",
      len(ns["observed_rows_for_division"]("NOT A DIVISION")) == 0)

# ── T5+T6: national extended series ──────────────────────────────────────────
nat = ns["load_national_extended"]()
ann = nat[nat["mm"].notna()]
check("T5a national annual 1901-2025 (observed + pipeline)",
      int(ann["year"].min()) == 1901 and int(ann["year"].max()) == 2025,
      f"{ann['year'].min()}-{ann['year'].max()}")
check("T5b observed national rows tagged", set(ann[ann["layer"] == "observed IMD"]["year"]) ==
      set(range(2016, 2026)))
mon26 = nat[(nat["year"] == 2026)]
check("T5c monsoon 2026 present (provisional)",
      len(mon26) == 1 and pd.notna(mon26["monsoon_mm"].iloc[0])
      and abs(float(mon26["monsoon_dep"].iloc[0]) + 12.6) < 0.2,
      str(mon26[["monsoon_mm", "monsoon_dep"]].to_dict("records")))
check("T6 2026 has NO annual total (incomplete year not mixed in)",
      len(nat[(nat["year"] == 2026) & nat["mm"].notna()]) == 0)

# ── T7: site values.json ─────────────────────────────────────────────────────
values = json.loads((SITE / "values.json").read_text())
mon = values.get("Monsoon", {})
mon_years = sorted(int(y) for y in mon)
check("T7a site monsoon values span 1901-2025", mon_years[0] == 1901 and mon_years[-1] == 2025,
      f"{mon_years[0]}-{mon_years[-1]}")
check("T7b site monsoon 2020 absent", 2020 not in mon_years)
check("T7c site has no 2026 subdivision values", 2026 not in mon_years)
obs_flag = all(v[2] == 1 for y in mon_years if y > 2015 for v in mon[str(y)].values())
check("T7d post-2015 site rows flagged observed", obs_flag)

# ── T8: site national.json ───────────────────────────────────────────────────
national = json.loads((SITE / "national.json").read_text())
ny, nm, na = national["years"], national["monsoon"], national["annual"]
last_mon = ny[len(nm) - 1 - nm[::-1].index(next(v for v in reversed(nm) if v is not None))]
last_ann = ny[len(na) - 1 - na[::-1].index(next(v for v in reversed(na) if v is not None))]
check("T8a site monsoon series reaches 2026", last_mon == 2026, str(last_mon))
check("T8b site annual series ends 2025 (no incomplete 2026)", last_ann == 2025, str(last_ann))

# ── T9: source fidelity ──────────────────────────────────────────────────────
check("T9 observed rows = 36 div x 10 yr x 5 series (no fabricated extras)",
      len(obs) == 36 * 10 * 5 - 1800 + 1800 and len(obs) == 1800, str(len(obs)))

print()
if FAILURES:
    print(f"RESULT: {len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("RESULT: all date-coverage and missing-data tests passed.")
