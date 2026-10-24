#!/usr/bin/env python3
"""
build_subdivision_geo.py — Build the IMD 36-subdivision boundary GeoJSON.

Source: IMD's own district boundary file (675 districts, each tagged with its
meteorological subdivision and homogeneous region), mirrored at
https://gist.github.com/planemad/d347ad7485344fb0ba4b470721825427
(original: https://mausam.imd.gov.in/imd_latest/contents/district_shapefile).

Dissolves districts into the 36 official subdivisions, simplifies the
geometry for fast WebGL rendering, maps names to VARSA's canonical scheme
(the same names used by scripts/data/fetch_observed.py), and writes
data/geo/imd_subdivisions.geojson.

Usage:
    python scripts/data/build_subdivision_geo.py
"""

import json
import re
import urllib.request
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

BASE = Path(__file__).resolve().parent.parent.parent
CACHE = BASE / "data" / "cache"
OUT = BASE / "data" / "geo" / "imd_subdivisions.geojson"

DISTRICTS_URL = ("https://gist.githubusercontent.com/planemad/"
                 "d347ad7485344fb0ba4b470721825427/raw/"
                 "209d887d681cc1112dd85cc63df0b2858ec97c6f/india-district-imd.geojson")

SIMPLIFY_TOL = 0.015  # degrees (~1.7 km) — plenty for country-level WebGL

# canonical name (same scheme as fetch_observed.py) + IMD homogeneous region
CANON = {
    "A & N Island": ("A & N ISLANDS", "South Peninsula"),
    "Arunachal Pradesh": ("ARUNACHAL PRADESH", "East And North East India"),
    "Assam & Meghalaya": ("ASSAM & MEGHALAYA", "East And North East India"),
    "N M M T": ("NAGALAND-MANIPUR-MIZO-TRIPURA", "East And North East India"),
    "Shwb & Sikkim": ("SUB-HIMALAYAN W.B. & SIKKIM", "East And North East India"),
    "Gangetic West Bengal": ("GANGETIC W.B.", "East And North East India"),
    "Orissa": ("ODISHA", "Central India"),
    "Jharkhand": ("JHARKHAND", "East And North East India"),
    "Bihar": ("BIHAR", "East And North East India"),
    "East Uttar Pradesh": ("EAST U.P.", "North West India"),
    "West Uttar Pradesh": ("WEST U.P.", "North West India"),
    "Uttarakhand": ("UTTARAKHAND", "North West India"),
    "Har. Chd & Delhi": ("HARYANA-CHD-DELHI", "North West India"),
    "Punjab": ("PUNJAB", "North West India"),
    "Himachal Pradesh": ("HIMACHAL PRADESH", "North West India"),
    "Jammu & Kashmir": ("JAMMU & KASHMIR", "North West India"),
    "West Rajasthan": ("WEST RAJASTHAN", "North West India"),
    "East Rajasthan": ("EAST RAJASTHAN", "North West India"),
    "West Madhya Pradesh": ("WEST M.P.", "Central India"),
    "East Madhya Pradesh": ("EAST M.P.", "Central India"),
    "Gujarat Region": ("GUJARAT REGION", "Central India"),
    "Saurashtra & Kutch": ("SAURASHTRA & KUTCH", "Central India"),
    "Konkan & Goa": ("KONKAN & GOA", "Central India"),
    "Madhya Maharashtra": ("MADHYA MAHARASHTRA", "Central India"),
    "Marathwada": ("MARATHAWADA", "Central India"),
    "Vidarbha": ("VIDARBHA", "Central India"),
    "Chhattisgarh": ("CHHATTISGARH", "Central India"),
    "Coastal Andhra Pradesh": ("COASTAL A.P.", "South Peninsula"),
    "Telangana": ("TELANGANA", "South Peninsula"),
    "Rayalaseema": ("RAYALASEEMA", "South Peninsula"),
    "Tamilnadu & Pondichery": ("TAMIL NADU", "South Peninsula"),
    "Coastal Karnataka": ("COASTAL KARNATAKA", "South Peninsula"),
    "N. I. Karnataka": ("NORTH INTERIOR KARNATAKA", "South Peninsula"),
    "S. I. Karnataka": ("SOUTH INTERIOR KARNATAKA", "South Peninsula"),
    "Kerala": ("KERALA", "South Peninsula"),
    "Lakshadweep": ("LAKSHADWEEP", "South Peninsula"),
}


def _squash(s):
    return re.sub(r"[^A-Z0-9]", "", str(s).upper())


SQUASH = {_squash(k): v for k, v in CANON.items()}


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    src = CACHE / "india-district-imd.geojson"
    if not src.exists():
        print(f"downloading {DISTRICTS_URL}")
        req = urllib.request.Request(DISTRICTS_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=180) as r, open(src, "wb") as f:
            f.write(r.read())
    raw = json.loads(src.read_text(encoding="utf-8"))
    feats = raw["features"]
    print(f"districts: {len(feats)}")

    # group district polygons by subdivision
    groups = {}
    regions = {}
    for f in feats:
        p = f["properties"]
        key = _squash(p["subdivision"])
        if key not in SQUASH:
            raise SystemExit(f"unmapped subdivision name: {p['subdivision']!r}")
        canon_name, region = SQUASH[key]
        groups.setdefault(canon_name, []).append(f["geometry"])
        regions[canon_name] = region
    print(f"subdivisions: {len(groups)}")

    out_features = []
    for canon_name, geoms in sorted(groups.items()):
        # repair invalid district polygons before unioning (buffer(0) fix)
        polys = [shape(g).buffer(0) for g in geoms if g]
        polys = [p for p in polys if not p.is_empty]
        merged = unary_union(polys)
        simple = merged.simplify(SIMPLIFY_TOL, preserve_topology=True)
        out_features.append({
            "type": "Feature",
            "properties": {
                "division": canon_name,
                "region": regions[canon_name],
            },
            "geometry": mapping(simple),
        })

    # order features west -> east for nicer hover order (by centroid longitude)
    out_features.sort(key=lambda f: shape(f["geometry"]).centroid.x)

    fc = {"type": "FeatureCollection", "features": out_features}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fc), encoding="utf-8")
    size_mb = OUT.stat().st_size / 1e6
    print(f"wrote {OUT} ({size_mb:.2f} MB, {len(out_features)} subdivisions)")

    # validation: every canonical division present exactly once
    import collections
    names = collections.Counter(f["properties"]["division"] for f in out_features)
    expected = {v[0] for v in CANON.values()}
    missing = expected - set(names)
    dupes = [n for n, c in names.items() if c > 1]
    print("missing:", sorted(missing) or "none")
    print("duplicates:", dupes or "none")


if __name__ == "__main__":
    main()
