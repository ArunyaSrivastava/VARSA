#!/usr/bin/env bash
# =============================================================================
# fetch_data.sh — Download / fetch all data needed for prob_project.
#
# This version fetches the IMD subdivision rainfall dataset for the VARSA study
# (India, 36 divisions, 1901–2015). The data is synthetic (generated locally)
# but follows IMD climatological norms.
#
# Usage:
#   bash scripts/fetch_data.sh          # generate the rainfall CSV
#   bash scripts/fetch_data.sh --dry    # only show what would happen
# =============================================================================
set -euo pipefail

BASH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$BASH_DIR/.." && pwd)"

# Data output dir
mkdir -p "$PROJECT_DIR/data/raw"

echo "=== Fetching VARSA India rainfall data ==="

if [[ "${1:-}" == "--dry" ]]; then
    echo "[dry-run] Would generate data/raw/india_rainfall.csv"
    echo "  Rows: ~20,700 (36 divisions × 115 years × 5 seasons)"
    echo "  Divisions: 36 meteorological subdivisions"
    echo "  Date range: 1901–2015"
else
    echo "[1/1] Generating IMD-style rainfall dataset..."
    python3 "$PROJECT_DIR/scripts/data/generate_data.py"
    echo "   Saved to data/raw/india_rainfall.csv"
fi

echo "=== Data fetch complete ==="
echo "Run: python3 scripts/load_data.py   (or just start the Streamlit app)"
