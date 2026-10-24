#!/usr/bin/env python3
"""
fetch_observed.py — Download and parse OBSERVED post-2015 IMD rainfall data.

The Review 3 report identified "acquire post-2015 data" as the top next step.
This script does exactly that from three official, public IMD sources:

  1. Annual Climate Summary reports (imdpune.gov.in, CMPG)
     https://www.imdpune.gov.in/cmpg/Product/Annual_Climate_Summary/annual_summary_YYYY.pdf
     Table 1 = "Meteorological sub-divisionwise seasonal and annual rainfall
     statistics" — all 36 subdivisions x {winter, pre-monsoon, monsoon,
     post-monsoon, annual} x {actual mm, normal mm, % departure, category}.
     Parsed for 2015-2025 (2015 kept for verification against the 1901-2015
     record).

  2. IMD CMPG homogeneous-regions page (monthly, 1901-2026)
     https://www.imdpune.gov.in/cmpg/Product/homo.html
     All-India + 4 homogeneous regions, monthly Jan-Dec + annual, actual mm.

  3. IMD CMPG rainfall-data page (monsoon months, 1901-2026)
     https://www.imdpune.gov.in/cmpg/Product/Rainfall_Data.html
     All-India + 4 regions, Jun/Jul/Aug/Sep + Jun-Sep, actual mm and % dep.

Outputs (data/raw/):
  imd_observed_subdivisions.csv  — year, division, season, actual_mm, normal_mm,
                                   pct_dep, category (36 div x 5 seasons x years)
  imd_all_india_monthly.csv      — year, month, region, rainfall_mm (1901-2026)
  imd_all_india_monsoon.csv      — year, region, jun..sep, seasonal_mm, dep_pct

A verification report is written to research/_observed_verification.txt.
Every parsed cell is validated against IMD's own printed % departure
(|(act/norm-1)*100 - dep| tolerance) before it is accepted.

Usage:
    python scripts/data/fetch_observed.py            # download if missing, parse
    python scripts/data/fetch_observed.py --no-download   # use cache only
"""

import argparse
import io
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import pdfplumber

BASE = Path(__file__).resolve().parent.parent.parent
CACHE = BASE / "data" / "cache"
RAW = BASE / "data" / "raw"
RES = BASE / "research"

ACS_URL = "https://www.imdpune.gov.in/cmpg/Product/Annual_Climate_Summary/annual_summary_{year}.pdf"
HOMO_URL = "https://www.imdpune.gov.in/cmpg/Product/homo.html"
RFDATA_URL = "https://www.imdpune.gov.in/cmpg/Product/Rainfall_Data.html"

ACS_YEARS = list(range(2015, 2026))  # 2015 kept for verification

SEASONS = ["WINTER", "PREMONSOON", "MONSOON", "POSTMONSOON", "ANNUAL"]

# IMD's 36 meteorological subdivisions (canonical names) + aliases used
# across report years.
CANONICAL = {
    "A & N ISLANDS": "A & N ISLANDS",
    "ARUNACHAL PRADESH": "ARUNACHAL PRADESH",
    "ASSAM & MEGHALAYA": "ASSAM & MEGHALAYA",
    "NAG.,MANI.,MIZO.,TRIP": "NAGALAND-MANIPUR-MIZO-TRIPURA",
    "S.H.W.B.&SIKKIM": "SUB-HIMALAYAN W.B. & SIKKIM",
    "GANGETIC W.B.": "GANGETIC W.B.",
    "ODISHA": "ODISHA",
    "JHARKHAND": "JHARKHAND",
    "BIHAR": "BIHAR",
    "EAST U.P.": "EAST U.P.",
    "WEST U.P.": "WEST U.P.",
    "UTTARAKHAND": "UTTARAKHAND",
    "HAR., CHANDI., DELHI": "HARYANA-CHD-DELHI",
    "PUNJAB": "PUNJAB",
    "HIMACHAL PRADESH": "HIMACHAL PRADESH",
    "JAMMU & KASHMIR": "JAMMU & KASHMIR",
    "WEST RAJASTHAN": "WEST RAJASTHAN",
    "EAST RAJASTHAN": "EAST RAJASTHAN",
    "WEST M.P.": "WEST M.P.",
    "EAST M.P.": "EAST M.P.",
    "GUJARAT REGION": "GUJARAT REGION",
    "SAURASHTRA & KUTCH": "SAURASHTRA & KUTCH",
    "KONKAN & GOA": "KONKAN & GOA",
    "MADHYA M'RASHTRA": "MADHYA MAHARASHTRA",
    "MARATHAWADA": "MARATHAWADA",
    "VIDARBHA": "VIDARBHA",
    "CHHATTISGARH": "CHHATTISGARH",
    "COASTAL A.P.": "COASTAL A.P.",
    "TELANGANA": "TELANGANA",
    "RAYALASEEMA": "RAYALASEEMA",
    "TAMIL NADU": "TAMIL NADU",
    "COASTAL KARNATAKA": "COASTAL KARNATAKA",
    "N.I.KARNATAKA": "NORTH INTERIOR KARNATAKA",
    "S.I.KARNATAKA": "SOUTH INTERIOR KARNATAKA",
    "KERALA": "KERALA",
    "LAKSHADWEEP": "LAKSHADWEEP",
}
ALIASES = {
    "ORISSA": "ODISHA",
    "UTTARANCHAL": "UTTARAKHAND",
    "GANGATIC W.B.": "GANGETIC W.B.",
    "CHATTISGARH": "CHHATTISGARH",
    "TELENGANA": "TELANGANA",
    "HAR., CHANDI., DELHI": "HARYANA-CHD-DELHI",
    "HAR.,CHANDI.&DELHI": "HARYANA-CHD-DELHI",
    "ASSAM &MEGHALAYA": "ASSAM & MEGHALAYA",
    "ASSAM&MEGHALAYA": "ASSAM & MEGHALAYA",
    "NAG., MANI., MIZO., TRIP": "NAGALAND-MANIPUR-MIZO-TRIPURA",
    "S.H.W.B. & SIKKIM": "SUB-HIMALAYAN W.B. & SIKKIM",
    "MADHYA M RASHTRA": "MADHYA MAHARASHTRA",
    "N. I. KARNATAKA": "NORTH INTERIOR KARNATAKA",
    "N.I. KARNATAKA": "NORTH INTERIOR KARNATAKA",
    "S.I. KARNATAKA": "SOUTH INTERIOR KARNATAKA",
    "A &N ISLANDS": "A & N ISLANDS",
    "A&N ISLANDS": "A & N ISLANDS",
    "ANDAMAN & NICOBAR ISLANDS": "A & N ISLANDS",
    "JAMMU &KASHMIR": "JAMMU & KASHMIR",
    "JAMMU&KASHMIR": "JAMMU & KASHMIR",
    "GUJARAT REG., DD & NH": "GUJARAT REGION",
    "GUJARAT REG. & DDNH": "GUJARAT REGION",
    "TAMIL NADU & PUDUCHERRY": "TAMIL NADU",
    "TAMILNADU&PUDU.": "TAMIL NADU",
    "COASTAL ANDHRA PRADESH & YANAM": "COASTAL A.P.",
    "TAMIL NADU, PUDUCHERRY & KARAIKAL": "TAMIL NADU",
    "KERALA & MAHE": "KERALA",
}

# Whitespace/punctuation-insensitive lookup (older PDFs strip spaces in cells)
def _squash(s):
    return re.sub(r"[^A-Z0-9]", "", str(s).upper())


SQUASH_MAP = {}
for _k, _v in {**CANONICAL, **ALIASES}.items():
    SQUASH_MAP[_squash(_k)] = _v

# 2018's PDF scrambles some names by transposition; an exact anagram match
# disambiguates where fuzzy matching ties (e.g. N.I. vs S.I. KARNATAKA).
ANAGRAM_MAP = {}
for _k, _v in SQUASH_MAP.items():
    ANAGRAM_MAP.setdefault("".join(sorted(_k)), set()).add(_v)

LOG = []


def say(msg=""):
    print(msg)
    LOG.append(str(msg))


def canon(name: str) -> str | None:
    s = _squash(name)
    exact = SQUASH_MAP.get(s)
    if exact:
        return exact
    anagram = ANAGRAM_MAP.get("".join(sorted(s)))
    if anagram and len(anagram) == 1:
        return next(iter(anagram))
    # last resort: close-text match (guarded by length and uniqueness)
    if len(s) >= 5:
        import difflib
        close = difflib.get_close_matches(s, SQUASH_MAP.keys(), n=2, cutoff=0.75)
        if len(close) == 1:
            return SQUASH_MAP[close[0]]
        if close:
            r = difflib.SequenceMatcher(None, s, close[0]).ratio()
            r2 = difflib.SequenceMatcher(None, s, close[1]).ratio()
            if r > r2 + 0.05:  # clear winner only
                return SQUASH_MAP[close[0]]
    return None


def rev(s):
    """Reverse a mirrored cell string (older IMD PDFs store rotated text)."""
    return re.sub(r"\s+", "", str(s))[::-1]


def to_float(s):
    try:
        return float(str(s).strip())
    except (ValueError, TypeError):
        return None


# ══════════════════════════════════════════════════════════════════════════════
# 1. ANNUAL CLIMATE SUMMARY PDFs
# ══════════════════════════════════════════════════════════════════════════════

def download_all(force=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    for year in ACS_YEARS:
        path = CACHE / f"annual_summary_{year}.pdf"
        if path.exists() and not force:
            continue
        say(f"[download] {ACS_URL.format(year=year)}")
        req = urllib.request.Request(ACS_URL.format(year=year),
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
        say(f"    -> {path} ({path.stat().st_size:,} bytes)")


def dedupe_names(names):
    """Guard against fuzzy-matching two different columns to the same
    division: keep the first occurrence, blank the rest."""
    seen = set()
    out = []
    for n in names:
        if n is None or n in seen:
            out.append(None)
        else:
            seen.add(n)
            out.append(n)
    return out


def find_table_page(pdf):
    """Return (page_index, table) for the subdivision statistics table.
    Accepts either orientation: divisions-as-rows (38 x 22) or the older
    transposed layout (17 x 38) whose labels are mirrored and sometimes
    misspelt, so detection is shape + numeric-density based."""
    for i, page in enumerate(pdf.pages):
        for t in page.extract_tables():
            if not t or not t[0]:
                continue
            rows, cols = len(t), len(t[0])
            if not ((cols >= 20 and rows < 20) or (rows >= 20 and cols >= 15)):
                continue
            num = sum(1 for row in t for c in row
                      if c and (to_float(c) is not None or to_float(rev(c)) is not None))
            if num > 120:
                return i, t
    return None, None


TRIPLE_ORDER = ["ANNUAL", "POSTMONSOON", "MONSOON", "PREMONSOON", "WINTER"]
ROW_TYPE = {"%DEP": "dep", "NORMAL": "norm", "ACT": "act", "ACTUAL": "act"}


def parse_transposed(t, year):
    """2015-2019 & 2021 layout: transposed with mirrored strings.
    Structure is rigid across all these years:
      rows 0-14  = 5 season blocks x 3 rows (dep, normal, actual) in the
                   fixed order ANNUAL, POSTMONSOON, MONSOON, PREMONSOON, WINTER
      row 15     = division names (mirrored), columns 2..37 = 36 divisions
      row 16     = serial numbers
    The block's value type is marked in column 1 (mirrored '%DEP' etc.)."""
    # locate the division-names row: columns 2+ are mostly non-numeric text
    names_idx = None
    for r_i, r in enumerate(t):
        cells = [c for c in r[2:] if c and str(c).strip()]
        if len(cells) < 20:
            continue
        nonnum = sum(1 for c in cells
                     if to_float(rev(c)) is None and to_float(c) is None)
        if nonnum >= 25:
            names_idx = r_i
            break
    if names_idx is None:
        return []
    names = dedupe_names([canon(rev(c)) if c else None for c in t[names_idx][2:]])

    data_rows = t[max(0, names_idx - 15):names_idx]
    if len(data_rows) < 15:
        return []
    records = []
    for block_i, season in enumerate(TRIPLE_ORDER):
        block = data_rows[block_i * 3: block_i * 3 + 3]
        by_type = {}
        for r in block:
            marker = rev(r[1]).upper() if r[1] else ""
            # tolerate stray characters around %DEP / NORMAL / ACT
            for key, typ in ROW_TYPE.items():
                if marker == key or (key != "ACT" and key in marker):
                    by_type[typ] = r
                    break
        if not {"dep", "norm", "act"} <= set(by_type):
            continue
        for c_i, div in enumerate(names):
            if div is None:
                continue
            dep = to_float(rev(by_type["dep"][c_i + 2])) if by_type["dep"][c_i + 2] else None
            norm = to_float(rev(by_type["norm"][c_i + 2])) if by_type["norm"][c_i + 2] else None
            act = to_float(rev(by_type["act"][c_i + 2])) if by_type["act"][c_i + 2] else None
            records.append({"year": year, "division": div, "season": season,
                            "actual_mm": act, "normal_mm": norm,
                            "pct_dep": dep, "category": ""})
    return records


def parse_normal_orientation(t, year):
    """2022-2025 layout: 38 rows (divisions) x 22 cols.
    [S.NO, SUB-DIVISION, (ACT, NORMAL, %DEP, CAT) x 5 seasons]"""
    records = []
    for row in t:
        if not row or len(row) < 6:
            continue
        div = canon(row[1] or "")
        if div is None:
            continue
        for s_i, season in enumerate(SEASONS):
            base = 2 + s_i * 4
            act, norm = to_float(row[base]), to_float(row[base + 1])
            dep = to_float(row[base + 2])
            cat = str(row[base + 3] or "").strip() if len(row) > base + 3 else ""
            if act is None and norm is None:
                continue
            records.append({"year": year, "division": div, "season": season,
                            "actual_mm": act, "normal_mm": norm,
                            "pct_dep": dep, "category": cat})
    return records


def parse_2020(pdf, page_index):
    """The 2020 ACS text layer is fragmented (per-character words) and the
    table mixes 'updated' and 'real time' values. Reconstruct from word
    coordinates: group words into lines, split each line into a name zone
    (x < 138: serial + division) and a number zone (x >= 138), cluster the
    number tokens into 15 season/value columns by x-position."""
    page = pdf.pages[page_index]
    words = page.extract_words()
    # --- group words into lines by top coordinate
    lines = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if lines and abs(w["top"] - lines[-1][0]["top"]) < 4.5:
            lines[-1].append(w)
        else:
            lines.append([w])

    # --- collect data lines: serial (1-36) + name letters in the name zone
    data_rows = []
    for line in lines:
        line = sorted(line, key=lambda w: w["x0"])
        name_zone = [w for w in line if w["x0"] < 138]
        num_zone = [w for w in line if w["x0"] >= 138]
        if not name_zone:
            continue
        serial = next((to_float(w["text"]) for w in name_zone
                       if to_float(w["text"]) is not None and 1 <= to_float(w["text"]) <= 36),
                      None)
        if serial is None:
            continue
        name = "".join(w["text"] for w in name_zone if to_float(w["text"]) is None)
        div = canon(name)
        if div is None:
            continue
        data_rows.append({"division": div, "nums": num_zone})
    # dedupe (fuzzy matches may collide); keep the row with more numbers
    by_div = {}
    for r in data_rows:
        if r["division"] not in by_div or len(r["nums"]) > len(by_div[r["division"]]["nums"]):
            by_div[r["division"]] = r
    data_rows = list(by_div.values())
    if len(data_rows) < 30:
        return []

    # --- cluster numeric token CENTERS into 15 columns (numbers are centred,
    #     so x0 alone smears clusters; token centers stay tight)
    def _center(w):
        return (w["x0"] + w["x1"]) / 2

    xs = sorted(_center(w) for r in data_rows for w in r["nums"])
    clusters = []
    for x in xs:
        if clusters and x - clusters[-1][-1] < 8:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    centers = [np.mean(c) for c in clusters]

    def col_values(num_zone):
        """Assign each fragment to its column, then join fragments in
        x-order to rebuild the printed number."""
        cols = {}
        for w in num_zone:
            c = int(np.argmin([abs(_center(w) - m) for m in centers]))
            cols.setdefault(c, []).append(w)
        out = {}
        for c, ws in cols.items():
            ws.sort(key=lambda w: w["x0"])
            out[c] = to_float("".join(w["text"] for w in ws))
        return out

    records = []
    order = ["WINTER", "PREMONSOON", "MONSOON", "POSTMONSOON", "ANNUAL"]
    cols_sorted = sorted(range(len(centers)), key=lambda c: centers[c])
    if len(cols_sorted) < 15:
        return []
    mapping = {}
    for idx, col in enumerate(cols_sorted[:15]):
        season = order[idx // 3]
        field = ["actual_mm", "normal_mm", "pct_dep"][idx % 3]
        mapping[col] = (season, field)
    for r in data_rows:
        vals = col_values(r["nums"])
        fields = {}
        for col, v in vals.items():
            if col in mapping and mapping[col][1] not in fields.get(mapping[col][0], {}):
                fields.setdefault(mapping[col][0], {})[mapping[col][1]] = v
        for season in order:
            if season in fields:
                f = fields[season]
                records.append({"year": 2020, "division": r["division"], "season": season,
                                "actual_mm": f.get("actual_mm"),
                                "normal_mm": f.get("normal_mm"),
                                "pct_dep": f.get("pct_dep"), "category": ""})
    return records


def parse_acs_year(path, year):
    with pdfplumber.open(path) as pdf:
        pno, t = find_table_page(pdf)
        recs, style = [], ""
        if t is not None:
            n_rows, n_cols = len(t), len(t[0])
            if n_cols > n_rows:                  # transposed (17 x 38)
                recs = parse_transposed(t, year)
                style = "transposed/mirrored"
            else:                                 # normal (38 x 22)
                recs = parse_normal_orientation(t, year)
                style = "normal"
        if len(recs) < 120 or len({r["division"] for r in recs}) < 30:
            # fall back to word-coordinate reconstruction (e.g. the 2020 PDF)
            say(f"[{year}] structured parse incomplete "
                f"({len({r['division'] for r in recs})} divisions) -> word reconstruction")
            recs2 = []
            for i, page in enumerate(pdf.pages):
                txt = (page.extract_text() or "").upper()
                if "SUB-DIVISIONWISE" in txt.replace(" ", "") or \
                   ("SUB-DIVISION" in txt and "STATISTICS" in txt):
                    recs2 = parse_2020(pdf, i)
                    if recs2:
                        break
            if len(recs2) > len(recs):
                recs, style = recs2, "word-reconstruction"
        ok = len({r["division"] for r in recs})
        say(f"[{year}] page {pno} ({style}): {ok} divisions, {len(recs)} cells")
        return recs


# ══════════════════════════════════════════════════════════════════════════════
# 2. VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

def validate(df):
    """Cross-check every cell against IMD's own %departure column.
    Tolerance scales with the normal: IMD prints values to 0.1 mm, so a
    tiny winter normal (e.g. 0.6 mm) amplifies rounding into several
    percentage points of departure."""
    say("\n=== VALIDATION ===")
    checks = df.dropna(subset=["actual_mm", "normal_mm", "pct_dep"])
    checks = checks[checks["normal_mm"] > 0]
    checks = checks.copy()
    checks["dep_calc"] = (checks["actual_mm"] / checks["normal_mm"] - 1) * 100
    checks["err"] = (checks["dep_calc"] - checks["pct_dep"]).abs()
    checks["tol"] = 1.5 + 10.0 / checks["normal_mm"]
    bad = checks[checks["err"] > checks["tol"]]
    say(f"cells with act+norm+dep: {len(checks)}")
    say(f"cells failing the scale-aware departure check: {len(bad)}")
    if len(bad):
        say(bad.groupby(["year", "season"]).size().to_string())

    # season sum vs annual
    piv = df[df["season"] != "ANNUAL"].pivot_table(
        index=["year", "division"], columns="season", values="actual_mm")
    if {"WINTER", "PREMONSOON", "MONSOON", "POSTMONSOON"}.issubset(piv.columns):
        annual = df[df["season"] == "ANNUAL"].set_index(["year", "division"])["actual_mm"]
        joined = piv.join(annual.rename("ANNUAL"), how="inner")
        joined["sum4"] = joined[["WINTER", "PREMONSOON", "MONSOON", "POSTMONSOON"]].sum(axis=1)
        joined["diff_pct"] = (100 * (joined["sum4"] - joined["ANNUAL"]).abs()
                              / joined["ANNUAL"].replace(0, np.nan))
        worst = joined["diff_pct"].nlargest(5)
        say("\nseason-sum vs annual (worst 5, % difference):")
        say(worst.round(2).to_string())
        ok_frac = (joined["diff_pct"] <= 2.0).mean()
        say(f"rows within 2%: {ok_frac * 100:.1f}%")

    # division counts per year
    say("\ndivisions per year:")
    say(df.groupby("year")["division"].nunique().to_string())
    return bad


# ══════════════════════════════════════════════════════════════════════════════
# 3. HTML SOURCES (all-India + homogeneous regions)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="ignore")


REGION_NAMES = ["ALL INDIA", "NORTH WEST INDIA", "NORTH EAST INDIA",
                "CENTRAL INDIA", "SOUTH PENINSULAR INDIA"]


def scrape_monthly(html):
    """homo.html -> long monthly table 1901-2026 for 5 regions."""
    tables = pd.read_html(io.StringIO(html))
    frames = []
    for i, t in enumerate(tables[:5]):
        t = t[t.iloc[:, 1].astype(str).str.upper() == "ACTL"].copy()
        t = t.rename(columns={t.columns[0]: "year"})
        t["region"] = REGION_NAMES[i] if i < len(REGION_NAMES) else f"REGION {i}"
        frames.append(t)
    all_t = pd.concat(frames, ignore_index=True)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
              "Oct", "Nov", "Dec"]
    long = all_t.melt(id_vars=["year", "region"], value_vars=months,
                      var_name="month", value_name="rainfall_mm")
    long["year"] = long["year"].astype(int)
    long["rainfall_mm"] = pd.to_numeric(long["rainfall_mm"], errors="coerce")
    ann = all_t.melt(id_vars=["year", "region"], value_vars=["Annual"],
                     var_name="month", value_name="rainfall_mm")
    ann["month"] = "ANNUAL"
    long = pd.concat([long, ann], ignore_index=True)
    long["year"] = pd.to_numeric(long["year"], errors="coerce")
    long["rainfall_mm"] = pd.to_numeric(long["rainfall_mm"], errors="coerce")
    return long.dropna(subset=["year", "rainfall_mm"]).sort_values(["region", "year", "month"])


def scrape_monsoon(html):
    """Rainfall_Data.html -> monsoon-month table 1901-2026 for 5 regions."""
    tables = pd.read_html(io.StringIO(html))
    frames = []
    for i, t in enumerate(tables[:5]):
        t.columns = [c[-1] for c in t.columns]  # flatten 2-level header
        act = t.iloc[:, 0:6].copy()
        dep = t.iloc[:, 6:12].copy()
        for frame, suffix in ((act, ""), (dep, "_dep")):
            frame.columns = ["year"] + [f"{c}{suffix}" for c in
                                        ["jun", "jul", "aug", "sep", "jun_sep"]]
            frame["region"] = REGION_NAMES[i] if i < len(REGION_NAMES) else f"REGION {i}"
            frames.append(frame)
    out = None
    for i in range(0, len(frames), 2):
        merged = frames[i].merge(frames[i + 1].drop(columns=["region"]), on="year")
        out = pd.concat([out, merged], ignore_index=True) if out is not None else merged
    for c in out.columns:
        if c not in ("region",):
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out.dropna(subset=["jun_sep"]).sort_values(["region", "year"])


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    RES.mkdir(parents=True, exist_ok=True)
    LOG.clear()
    say("VARSA — observed post-2015 IMD data fetch")
    say("=" * 60)

    if not args.no_download:
        download_all()

    # ── ACS subdivision tables ──────────────────────────────────────────────
    say("\n=== ANNUAL CLIMATE SUMMARIES (subdivision tables) ===")
    records = []
    for year in ACS_YEARS:
        path = CACHE / f"annual_summary_{year}.pdf"
        if not path.exists():
            say(f"[{year}] missing (skipped)")
            continue
        records.extend(parse_acs_year(path, year))
    sub = pd.DataFrame(records)
    if sub.empty:
        say("No subdivision records parsed — aborting.")
        sys.exit(1)

    bad = validate(sub)
    # drop cells that fail the departure cross-check (parse errors, not data)
    if len(bad):
        mask = sub.set_index(["year", "division", "season"]).index.isin(
            bad.set_index(["year", "division", "season"]).index)
        sub = sub[~mask]
        say(f"\ndropped {mask.sum()} inconsistent cells")

    # ── per-year quality gate ───────────────────────────────────────────────
    # A year is rejected when too many cells fail the departure check or when
    # division-level season sums disagree with the annual value: both indicate
    # a broken source table (the 2020 ACS mixes 'real time' preliminary
    # values with a fragmented text layer and fails this gate).
    cell_total = pd.DataFrame(records)
    gate_fail = {}
    for year in sorted(cell_total["year"].unique()):
        ydf = cell_total[cell_total["year"] == year]
        n_cells = len(ydf)
        n_bad_year = int(len(bad[bad["year"] == year])) if len(bad) else 0
        fail_rate = n_bad_year / max(n_cells, 1)
        piv = ydf[ydf["season"] != "ANNUAL"].pivot_table(
            index=["year", "division"], columns="season", values="actual_mm")
        bad_sums = 0
        if {"WINTER", "PREMONSOON", "MONSOON", "POSTMONSOON"} <= set(piv.columns):
            annual = ydf[ydf["season"] == "ANNUAL"].set_index(
                ["year", "division"])["actual_mm"]
            j = piv.join(annual.rename("ANNUAL"), how="inner")
            j["sum4"] = j[["WINTER", "PREMONSOON", "MONSOON", "POSTMONSOON"]].sum(axis=1)
            j["diff"] = (100 * (j["sum4"] - j["ANNUAL"]).abs()
                         / j["ANNUAL"].replace(0, np.nan))
            bad_sums = int((j["diff"] > 5.0).sum())
        reason = None
        if fail_rate > 0.02:
            reason = f"{100 * fail_rate:.1f}% of cells fail the departure check"
        elif bad_sums > 2:
            reason = f"{bad_sums} divisions' season sums deviate >5% from annual"
        if reason:
            gate_fail[year] = reason
    for year, reason in gate_fail.items():
        n = int((sub["year"] == year).sum())
        sub = sub[sub["year"] != year]
        say(f"\n[gate] year {year} REJECTED and excluded ({n} cells): {reason}")
        say(f"       (national/region series for {year} remain available from "
            f"the CMPG HTML sources)")

    sub = sub.sort_values(["year", "division", "season"])
    sub.to_csv(RAW / "imd_observed_subdivisions.csv", index=False)
    say(f"\nwrote data/raw/imd_observed_subdivisions.csv ({len(sub)} rows)")
    say(f"  years: {sorted(sub['year'].unique())}")
    say(f"  divisions: {sub['division'].nunique()}")

    # ── HTML sources ────────────────────────────────────────────────────────
    say("\n=== CMPG homo.html (all-India monthly) ===")
    homo_html = fetch_url(HOMO_URL)
    monthly = scrape_monthly(homo_html)
    monthly.to_csv(RAW / "imd_all_india_monthly.csv", index=False)
    say(f"wrote data/raw/imd_all_india_monthly.csv ({len(monthly)} rows, "
        f"{monthly['year'].min()}-{monthly['year'].max()})")

    say("\n=== CMPG Rainfall_Data.html (monsoon months) ===")
    rf_html = fetch_url(RFDATA_URL)
    monsoon = scrape_monsoon(rf_html)
    monsoon.to_csv(RAW / "imd_all_india_monsoon.csv", index=False)
    say(f"wrote data/raw/imd_all_india_monsoon.csv ({len(monsoon)} rows, "
        f"{monsoon['year'].min()}-{monsoon['year'].max()})")

    # ── cross-checks between sources ────────────────────────────────────────
    say("\n=== CROSS-SOURCE CHECKS ===")
    ai = monthly[(monthly["region"] == "ALL INDIA") & (monthly["month"] == "ANNUAL")]
    ai_recent = ai[ai["year"] >= 2016]
    say("All-India annual (homo.html), 2016-2026:")
    say(ai_recent.to_string(index=False))
    mj = monsoon[(monsoon["region"] == "ALL INDIA") & (monsoon["year"] >= 2016)]
    say("\nAll-India Jun-Sep (Rainfall_Data.html), 2016-2026:")
    say(mj[["year", "jun", "jul", "aug", "sep", "jun_sep", "jun_sep_dep"]].to_string(index=False))
    # homo monthly Jun-Sep sum vs monsoon page seasonal
    hom = monthly[(monthly["region"] == "ALL INDIA") & (monthly["year"] >= 2016)
                  & (monthly["month"].isin(["Jun", "Jul", "Aug", "Sep"]))]
    hom_sum = hom.groupby("year")["rainfall_mm"].sum()
    for y, s in hom_sum.items():
        ref = monsoon[(monsoon["region"] == "ALL INDIA") & (monsoon["year"] == y)]["jun_sep"]
        if len(ref):
            d = abs(s - float(ref.iloc[0]))
            flag = "OK" if d < 1.0 else f"MISMATCH ({d:.1f} mm)"
            say(f"  {y}: homo sum {s:.1f} vs monsoon page {ref.iloc[0]:.1f} -> {flag}")

    (RES / "_observed_verification.txt").write_text("\n".join(LOG) + "\n",
                                                    encoding="utf-8")
    say("\nlog -> research/_observed_verification.txt")


if __name__ == "__main__":
    main()
