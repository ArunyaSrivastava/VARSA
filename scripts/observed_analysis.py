#!/usr/bin/env python3
"""
observed_analysis.py — VARSA analysis of the OBSERVED post-2015 IMD layer.

Runs against the outputs of scripts/data/fetch_observed.py:
  data/raw/imd_observed_subdivisions.csv   (36 divisions x 5 seasons, 2015-2025)
  data/raw/imd_all_india_monthly.csv       (5 regions, monthly, 1901-2026)
  data/raw/imd_all_india_monsoon.csv       (5 regions, Jun-Sep, 1901-2026)

Produces (review_3/):
  fig8_extended_national_series.png — all-India annual & monsoon 1901-2026,
                                      with the recovered 2016-2026 decade highlighted
  fig9_observed_departures.png      — subdivision x year %departure heatmap (monsoon)
  observed_results.json             — every number quoted in the report update

Usage:
    python scripts/fetch_observed.py        # first (downloads + parses)
    python scripts/observed_analysis.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
R3 = BASE / "review_3"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#FBFCFE",
    "axes.edgecolor": "#334155",
    "axes.labelcolor": "#0F172A",
    "text.color": "#0F172A",
    "xtick.color": "#334155",
    "ytick.color": "#334155",
    "axes.grid": True,
    "grid.color": "#E2E8F0",
    "grid.linewidth": 0.7,
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "figure.dpi": 200,
})

C_MONSOON = "#15803D"
C_BLUE = "#1D4ED8"
C_AMBER = "#D97706"
C_RED = "#DC2626"
C_MUTED = "#64748B"

RES = {}
LINES = []


def say(msg=""):
    print(msg)
    LINES.append(str(msg))


sub = pd.read_csv(RAW / "imd_observed_subdivisions.csv")
monthly = pd.read_csv(RAW / "imd_all_india_monthly.csv")
monsoon = pd.read_csv(RAW / "imd_all_india_monsoon.csv")

# ══════════════════════════════════════════════════════════════════════════════
# A. EXTENDED NATIONAL RECORD (1901-2026, observed IMD CMPG values)
# ══════════════════════════════════════════════════════════════════════════════
say("=== A. EXTENDED NATIONAL RECORD (observed, 1901-2026) ===")
ai_annual = monthly[(monthly["region"] == "ALL INDIA") & (monthly["month"] == "ANNUAL")] \
    .set_index("year")["rainfall_mm"].sort_index()
ai_mon = monsoon[monsoon["region"] == "ALL INDIA"].set_index("year")["jun_sep"].sort_index()

old = ai_annual[ai_annual.index <= 2015]
new = ai_annual[ai_annual.index >= 2016]
say(f"annual series: {ai_annual.index.min()}-{ai_annual.index.max()} (complete years); "
    f"2026 in progress (monthly through Sep, monsoon complete)")
say(f"1901-2015 mean {old.mean():.1f} mm | 2016-2025 mean {ai_annual[ai_annual.index <= 2025].mean():.1f} mm")

# OLS + Mann-Kendall on the extended OBSERVED annual series (1901-2025 complete years)
complete = ai_annual[ai_annual.index <= 2025]
x = complete.index.values.astype(float)
lr = stats.linregress(x, complete.values)
mk = stats.kendalltau(x, complete.values)
say(f"observed annual trend 1901-2025: {lr.slope:+.3f} mm/yr ({lr.slope*100:+.1f} mm/century), "
    f"p={lr.pvalue:.3f} | MK tau={mk.statistic:.3f}, p={mk.pvalue:.3f}")

# same for the pre-2015 window (for comparison)
lr_old = stats.linregress(old.index.values.astype(float), old.values)
say(f"observed annual trend 1901-2015: {lr_old.slope:+.3f} mm/yr "
    f"({lr_old.slope*100:+.1f} mm/century), p={lr_old.pvalue:.3f}")

# decade means
dec = complete.groupby((complete.index // 10) * 10).mean()
say("decadal means (mm):")
say(dec.round(1).to_string())

RES["national"] = {
    "mean_1901_2015": round(float(old.mean()), 1),
    "mean_2016_2025": round(float(ai_annual[(ai_annual.index >= 2016) & (ai_annual.index <= 2025)].mean()), 1),
    "trend_1901_2025_mm_per_century": round(float(lr.slope * 100), 1),
    "trend_1901_2025_p": round(float(lr.pvalue), 3),
    "trend_1901_2015_mm_per_century": round(float(lr_old.slope * 100), 1),
    "trend_1901_2015_p": round(float(lr_old.pvalue), 3),
    "mk_tau_1901_2025": round(float(mk.statistic), 3),
    "mk_p_1901_2025": round(float(mk.pvalue), 3),
    "monsoon_2026_mm": round(float(ai_mon.loc[2026]), 1),
    "monsoon_2026_dep": round(float(
        monsoon[(monsoon["region"] == "ALL INDIA") & (monsoon["year"] == 2026)]["jun_sep_dep"].iloc[0]), 1),
    "wettest_recent_year": int(ai_annual[ai_annual.index >= 2016].idxmax()),
    "wettest_recent_mm": round(float(ai_annual[ai_annual.index >= 2016].max()), 1),
    "driest_recent_year": int(ai_annual[ai_annual.index >= 2016].idxmin()),
    "driest_recent_mm": round(float(ai_annual[ai_annual.index >= 2016].min()), 1),
}

# ── Figure 8: extended national series ────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
ax = axes[0]
ax.bar(ai_annual.index, ai_annual.values,
       color=["#93C5FD" if y <= 2015 else C_AMBER for y in ai_annual.index], width=0.8)
recent_mean = ai_annual[ai_annual.index >= 2016].mean()
ax.axhline(old.mean(), color=C_BLUE, ls="--", lw=1.3)
ax.axhline(recent_mean, color=C_RED, ls=":", lw=1.3)
ax.text(0.985, old.mean() + 16, f"1901-2015 mean {old.mean():.0f} mm",
        transform=ax.get_yaxis_transform(), ha="right", fontsize=8, color=C_BLUE,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
ax.text(0.985, recent_mean - 42, f"2016-2026 mean {recent_mean:.0f} mm",
        transform=ax.get_yaxis_transform(), ha="right", fontsize=8, color=C_RED,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
ax.set_xlabel("Year")
ax.set_ylabel("All-India annual rainfall (mm)")
ax.set_title("A. All-India annual rainfall, 1901-2026 (observed IMD)")
ax.set_xlim(1900, 2027)

ax = axes[1]
ax.bar(ai_mon.index, ai_mon.values,
       color=["#86EFAC" if v >= 0.9 * ai_mon[ai_mon.index <= 2015].mean()
              else C_AMBER for v in ai_mon.values], width=0.8)
mon_old_mean = ai_mon[ai_mon.index <= 2015].mean()
ax.axhline(mon_old_mean, color=C_MONSOON, ls="--", lw=1.3)
ax.text(0.985, mon_old_mean + 16, f"1901-2015 mean {mon_old_mean:.0f} mm",
        transform=ax.get_yaxis_transform(), ha="right", fontsize=8, color=C_MONSOON,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
ax.annotate(f"2026: {ai_mon.loc[2026]:.0f} mm (−13%)",
            xy=(2026, ai_mon.loc[2026]), xytext=(1998, 1010),
            fontsize=9, color=C_RED, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.2))
ax.set_xlabel("Year")
ax.set_ylabel("All-India Jun-Sep rainfall (mm)")
ax.set_title("B. All-India monsoon rainfall, 1901-2026")
ax.set_xlim(1900, 2027)
fig.savefig(R3 / "fig8_extended_national_series.png", bbox_inches="tight")
plt.close(fig)
say("[figure] fig8_extended_national_series.png")

# ══════════════════════════════════════════════════════════════════════════════
# B. OBSERVED SUBDIVISION LAYER (2015-2025)
# ══════════════════════════════════════════════════════════════════════════════
say("\n=== B. OBSERVED SUBDIVISIONS (2015-2025, ACS Table 1) ===")
mon_obs = sub[sub["season"] == "MONSOON"].pivot(index="division", columns="year",
                                                values="pct_dep")
# order divisions by 2025 monsoon departure (wettest top)
order = mon_obs.mean(axis=1).sort_values(ascending=False).index
mon_obs = mon_obs.loc[order]

extreme_cells = []
for year in [2016, 2019, 2021, 2022, 2023, 2024, 2025]:
    if year in mon_obs.columns:
        col = mon_obs[year].dropna()
        extreme_cells.append({
            "year": year,
            "wettest": f"{col.idxmax()} ({col.max():+.0f}%)",
            "driest": f"{col.idxmin()} ({col.min():+.0f}%)",
        })
say("monsoon %departure extremes by year:")
for e in extreme_cells:
    say(f"  {e['year']}: wettest {e['wettest']} | driest {e['driest']}")

mean_dep = sub[sub["season"] == "MONSOON"].groupby("year")["pct_dep"].mean()
say("\nmean subdivision monsoon %departure by year:")
say(mean_dep.round(1).to_string())

RES["subdivisions"] = {
    "years": sorted(int(y) for y in sub["year"].unique()),
    "divisions": int(sub["division"].nunique()),
    "mean_monsoon_dep_by_year": {int(k): round(float(v), 1)
                                 for k, v in mean_dep.items()},
    "extremes": extreme_cells,
    "kerala_2023_dep": round(float(
        sub[(sub["division"] == "KERALA") & (sub["year"] == 2023)
            & (sub["season"] == "MONSOON")]["pct_dep"].iloc[0]), 1),
}

# ── Figure 9: subdivision x year monsoon departure heatmap ────────────────────
fig, ax = plt.subplots(figsize=(9.6, 8.6))
data = mon_obs.values
im = ax.imshow(data, cmap="RdYlGn", vmin=-60, vmax=60, aspect="auto")
ax.set_xticks(range(len(mon_obs.columns)))
ax.set_xticklabels([str(y) for y in mon_obs.columns], fontsize=9)
ax.set_yticks(range(len(mon_obs.index)))
ax.set_yticklabels(mon_obs.index, fontsize=7.2)
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        v = data[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v:+.0f}", ha="center", va="center", fontsize=6.4,
                    color="#0F172A")
ax.set_title("Monsoon (Jun-Sep) rainfall % departure from normal\n"
             "observed IMD subdivisions, 2015-2025 (2020 not machine-verifiable)",
             fontsize=11)
cb = fig.colorbar(im, ax=ax, shrink=0.85)
cb.set_label("% departure", fontsize=9)
ax.grid(False)
fig.savefig(R3 / "fig9_observed_departures.png", dpi=150, bbox_inches="tight")
plt.close(fig)
say("[figure] fig9_observed_departures.png")

# ══════════════════════════════════════════════════════════════════════════════
# C. WHAT THE EXTRA DECADE CHANGES
# ══════════════════════════════════════════════════════════════════════════════
say("\n=== C. WHAT THE EXTRA DECADE CHANGES ===")
two_era_obs = stats.ttest_ind(ai_annual[(ai_annual.index >= 2016) & (ai_annual.index <= 2025)],
                              ai_annual[ai_annual.index <= 2015], equal_var=False)
say(f"2016-2025 vs 1901-2015 (observed annual): "
    f"{ai_annual[(ai_annual.index >= 2016) & (ai_annual.index <= 2025)].mean():.1f} vs "
    f"{old.mean():.1f} mm, Welch p={two_era_obs.pvalue:.3f}")
mon_recent = ai_mon[(ai_mon.index >= 2016) & (ai_mon.index <= 2025)]
mon_old = ai_mon[ai_mon.index <= 2015]
say(f"monsoon: 2016-2025 mean {mon_recent.mean():.1f} vs 1901-2015 mean "
    f"{mon_old.mean():.1f} mm (diff {mon_recent.mean()-mon_old.mean():+.1f} mm, "
    f"{100*(mon_recent.mean()/mon_old.mean()-1):+.1f}%)")
lr_mon = stats.linregress(ai_mon[ai_mon.index <= 2025].index.values.astype(float),
                          ai_mon[ai_mon.index <= 2025].values)
say(f"observed monsoon trend 1901-2025: {lr_mon.slope*100:+.1f} mm/century, p={lr_mon.pvalue:.3f}")

RES["comparison"] = {
    "annual_2016_2025_mean": round(float(ai_annual[(ai_annual.index >= 2016) & (ai_annual.index <= 2025)].mean()), 1),
    "annual_1901_2015_mean": round(float(old.mean()), 1),
    "welch_p": round(float(two_era_obs.pvalue), 3),
    "monsoon_2016_2025_mean": round(float(mon_recent.mean()), 1),
    "monsoon_1901_2015_mean": round(float(mon_old.mean()), 1),
    "monsoon_diff_mm": round(float(mon_recent.mean() - mon_old.mean()), 1),
    "monsoon_diff_pct": round(float(100 * (mon_recent.mean() / mon_old.mean() - 1)), 1),
    "monsoon_trend_1901_2025_mm_per_century": round(float(lr_mon.slope * 100), 1),
    "monsoon_trend_p": round(float(lr_mon.pvalue), 3),
}

with open(R3 / "observed_results.json", "w") as f:
    json.dump(RES, f, indent=2)
say("\n[json] review_3/observed_results.json")
(BASE / "research" / "_observed_analysis_raw.txt").write_text(
    "\n".join(LINES) + "\n", encoding="utf-8")
say("[log] research/_observed_analysis_raw.txt")
say("Observed-layer analysis complete.")
