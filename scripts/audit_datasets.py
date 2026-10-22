#!/usr/bin/env python3
"""
audit_datasets.py — Full dataset audit script.

Scans each data source, reports schema, quality, duplicates, missingness, and
summary statistics. Output is tee'd to research/_audit_raw.txt for Review 2.

Usage:
    python scripts/audit_datasets.py
    python scripts/audit_datasets.py --source spotify
    python scripts/audit_datasets.py --source india
"""

import argparse
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
REPORT_DIR = BASE_DIR / "research"


def audit_csv(path: Path, name: str) -> dict:
    """Run a basic audit on a CSV/Excel file and return a report dict."""
    df = pd.read_csv(path)
    report = {
        "source": name,
        "file": str(path.relative_to(BASE_DIR)),
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
        "missing_total": int(df.isna().sum().sum()),
        "missing_per_column": {str(k): int(v) for k, v in df.isna().sum().items() if v > 0},
        "duplicate_rows": int(df.duplicated().sum()),
        "describe": df.describe(include="all").to_dict(),
    }
    # Duplicate rows check
    if report["duplicate_rows"] > 0:
        report["duplicate_ratio"] = round(report["duplicate_rows"] / len(df), 4)
    return report


def audit_pkl(path: Path, name: str) -> dict:
    """Audit a Python pickle file (assumption: pandas DataFrame)."""
    df = pd.read_pickle(path)
    report = {
        "source": name,
        "file": str(path.relative_to(BASE_DIR)),
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
        "missing_total": int(df.isna().sum().sum()),
        "missing_per_column": {str(k): int(v) for k, v in df.isna().sum().items() if v > 0},
        "duplicate_rows": int(df.duplicated().sum()),
        "describe": df.describe(include="all").to_dict(),
    }
    if report["duplicate_rows"] > 0:
        report["duplicate_ratio"] = round(report["duplicate_rows"] / len(df), 4)
    return report


def main():
    parser = argparse.ArgumentParser(description="Audit project datasets.")
    parser.add_argument("--source", choices=["spotify", "india", "all"], default="all",
                        help="Which source to audit (default: all)")
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines = []

    if args.source in ("spotify", "all"):
        spotify_file = DATA_DIR / "spotify_tracks.csv"
        if spotify_file.exists():
            r = audit_csv(spotify_file, "Spotify")
            lines.append(json.dumps(r, indent=2, default=str))

    if args.source in ("india", "all"):
        india_file = DATA_DIR / "india_rainfall.csv"
        if india_file.exists():
            r = audit_csv(india_file, "India Rainfall")
            lines.append(json.dumps(r, indent=2, default=str))

    if not lines:
        print("No data files found in data/raw/. Run fetch_data.sh first.")
        return

    for l in lines:
        print(l)
        print("-" * 60)


if __name__ == "__main__":
    main()
