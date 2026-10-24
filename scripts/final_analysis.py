#!/usr/bin/env python3
"""
final_analysis.py — VARSA Review 3: the complete, reproducible statistical pipeline.

Runs every analysis reported in review_3/final_report.md against
data/raw/india_rainfall.csv (the project's single source of truth, generated
by scripts/data/generate_data.py via scripts/fetch_data.sh) and produces:

  1. Seven publication-ready figures (PNG, 200 dpi) -> review_3/fig*.png
  2. A machine-readable results file               -> review_3/analysis_results.json
  3. A full raw log for the appendix               -> research/_final_analysis_raw.txt

Analyses (one per report section):
  A. Dataset audit          — schema, completeness, duplicates, summary stats
  B. Seasonality            — monsoon (Jun-Sep) share of the rainfall year
  C. Regional variability   — CV by division, one-way ANOVA, Levene, Welch ANOVA, eta^2
  D. Distribution fits      — Normal vs Gamma vs Lognormal (KS distance), skew, kurtosis
  E. Trend analysis         — OLS + Mann-Kendall per division, Sen's slope, BH correction
  F. Drought & extremes     — deficit years, 1-in-20-year (5th percentile) levels
  G. Spatial correlation    — Pearson r between all division pairs
  H. Two-era comparison     — 1950-1980 vs 1981-2015 national test

Usage:
    python scripts/final_analysis.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "raw" / "india_rainfall.csv"
R3 = BASE / "review_3"
RES = BASE / "research"
R3.mkdir(parents=True, exist_ok=True)
RES.mkdir(parents=True, exist_ok=True)

# ── Report figure style (matches the dashboard's clean look) ──────────────────
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
C_PURPLE = "#7C3AED"
C_MUTED = "#64748B"

LINES = []          # everything printed also goes to research/_final_analysis_raw.txt
RESULTS = {}


def say(text=""):
    print(text)
    LINES.append(str(text))


def hdr(title):
    say("")
    say("=" * 78)
    say(title)
    say("=" * 78)


def savefig(fig, name):
    path = R3 / name
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    say(f"[figure] {name}")


# ══════════════════════════════════════════════════════════════════════════════
# LOAD
# ══════════════════════════════════════════════════════════════════════════════
df = pd.read_csv(DATA)
ann = df[df["season"] == "ANNUAL"].copy()
sea = df[df["season"] != "ANNUAL"].copy()
divisions = sorted(ann["division"].unique())
years = sorted(ann["year"].unique())

# National annual series = mean across the 36 divisions (as in app.py)
nat = ann.groupby("year")["rainfall_mm"].mean().sort_index()

# ══════════════════════════════════════════════════════════════════════════════
# A. DATASET AUDIT
# ══════════════════════════════════════════════════════════════════════════════
hdr("A. DATASET AUDIT")
audit = {
    "rows": int(len(df)),
    "columns": int(df.shape[1]),
    "divisions": int(ann["division"].nunique()),
    "years": int(ann["year"].nunique()),
    "year_min": int(ann["year"].min()),
    "year_max": int(ann["year"].max()),
    "series_per_division": sorted(df["season"].unique().tolist()),
    "missing_cells": int(df.isna().sum().sum()),
    "duplicate_rows": int(df.duplicated().sum()),
    "division_year_gaps": int(36 * 115 - len(ann)),
    "negative_rainfall": int((df["rainfall_mm"] < 0).sum()),
}
# Detail on negatives (generator artefact, documented in the audit section)
neg = df[df["rainfall_mm"] < 0]
audit["negative_detail"] = {
    "seasons": sorted(neg["season"].unique().tolist()),
    "divisions": sorted(neg["division"].unique().tolist()),
    "min_mm": round(float(neg["rainfall_mm"].min()), 1),
    "max_mm": round(float(neg["rainfall_mm"].max()), 1),
    "pct_of_rows": round(100 * len(neg) / len(df), 2),
}
say(f"Rows x cols            : {audit['rows']} x {audit['columns']}")
say(f"Divisions x years      : {audit['divisions']} x {audit['years']} ({audit['year_min']}-{audit['year_max']})")
say(f"Series per division    : {audit['series_per_division']}")
say(f"Missing cells          : {audit['missing_cells']}")
say(f"Duplicate rows         : {audit['duplicate_rows']}")
say(f"Missing division-years : {audit['division_year_gaps']}")
say(f"Negative rainfall      : {audit['negative_rainfall']}")

nat_desc = nat.describe()
say("\nNational annual series (mean of 36 divisions), mm:")
say(nat_desc.round(1).to_string())
audit["national_annual"] = {k: round(float(v), 2) for k, v in nat_desc.items()}
RESULTS["audit"] = audit

# ══════════════════════════════════════════════════════════════════════════════
# B. SEASONALITY — monsoon concentration
# ══════════════════════════════════════════════════════════════════════════════
hdr("B. SEASONALITY (monsoon concentration)")

# National seasonal means (mm per year, averaged over divisions & years)
seas_nat = sea.groupby("season")["rainfall_mm"].mean()
order = ["DJF", "MAM", "JAS", "OND"]
seas_nat = seas_nat.reindex(order)
seas_share = (seas_nat / seas_nat.sum() * 100).round(1)
say("National mean rainfall by season (mm/yr) and share of the rainfall year:")
for s in order:
    say(f"  {s:5s}: {seas_nat[s]:8.1f} mm   {seas_share[s]:5.1f}%")

# Per-division monsoon share, mirroring the dashboard's definition:
# mean(JAS) / mean(DJF+MAM+JAS+OND)
rows = []
for d in divisions:
    g = sea[sea["division"] == d].groupby("season")["rainfall_mm"].mean()
    tot = g.sum()
    rows.append({"division": d, "monsoon_share": 100 * g.get("JAS", 0) / tot if tot else np.nan})
share_df = pd.DataFrame(rows).sort_values("monsoon_share")
sh = share_df["monsoon_share"]
seasonality = {
    "national_monsoon_share_pct": round(float(seas_share["JAS"]), 1),
    "national_seasonal_mm": {s: round(float(seas_nat[s]), 1) for s in order},
    "national_seasonal_share_pct": {s: round(float(seas_share[s]), 1) for s in order},
    "division_monsoon_share_min": round(float(sh.min()), 1),
    "division_monsoon_share_max": round(float(sh.max()), 1),
    "division_monsoon_share_mean": round(float(sh.mean()), 1),
    "lowest_share_division": share_df.iloc[0]["division"],
    "highest_share_division": share_df.iloc[-1]["division"],
}
say(f"\nMonsoon (Jun-Sep) share of the rainfall year, by division:")
say(f"  mean {seasonality['division_monsoon_share_mean']}% | range "
    f"{seasonality['division_monsoon_share_min']}% ({seasonality['lowest_share_division']}) "
    f"to {seasonality['division_monsoon_share_max']}% ({seasonality['highest_share_division']})")
RESULTS["seasonality"] = seasonality

# One-way ANOVA: does the season explain rainfall variance? (national, per-season-year pooled)
season_values = [sea[sea["season"] == s]["rainfall_mm"].values for s in order]
F_seas, p_seas = stats.f_oneway(*season_values)
ss_total_seas = sum(((v - sea["rainfall_mm"].mean()) ** 2).sum() for v in season_values)
ss_between_seas = sum(len(v) * (v.mean() - sea["rainfall_mm"].mean()) ** 2 for v in season_values)
eta2_seas = ss_between_seas / ss_total_seas
seasonality["anova_season_F"] = round(float(F_seas), 1)
seasonality["anova_season_p"] = float(p_seas)
seasonality["anova_season_eta2"] = round(float(eta2_seas), 3)
say(f"Season effect (one-way ANOVA on seasonal totals): F={F_seas:.1f}, p={p_seas:.2e}, eta^2={eta2_seas:.3f}")

# ── Figure 1: seasonality ─────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
ax = axes[0]
labels = ["Winter\n(Dec-Feb)", "Pre-monsoon\n(Mar-May)", "Monsoon\n(Jun-Sep)", "Post-monsoon\n(Oct-Dec)"]
colors = [C_PURPLE, C_AMBER, C_MONSOON, C_BLUE]
bars = ax.bar(labels, seas_nat.values, color=colors, width=0.62)
for b, v, pct in zip(bars, seas_nat.values, seas_share.values):
    ax.text(b.get_x() + b.get_width() / 2, v + seas_nat.max() * 0.03,
            f"{v:,.0f} mm\n({pct:.0f}%)",
            ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_ylabel("Mean rainfall (mm/yr)")
ax.set_title("A. National mean rainfall by season")
ax.set_ylim(0, seas_nat.max() * 1.30)

ax = axes[1]
plot_df = share_df.sort_values("monsoon_share", ascending=False)
ax.barh(range(len(plot_df)), plot_df["monsoon_share"], color=C_MONSOON, height=0.72)
ax.set_yticks(range(len(plot_df)))
ax.set_yticklabels(plot_df["division"], fontsize=6.2)
ax.invert_yaxis()
ax.set_ylim(37.2, -0.8)
ax.axvline(seasonality["national_monsoon_share_pct"], color=C_RED, ls="--", lw=1.2)
ax.text(seasonality["national_monsoon_share_pct"] + 0.6, 36.4,
        f"national {seasonality['national_monsoon_share_pct']}%", color=C_RED,
        fontsize=8.5, va="center")
ax.set_xlabel("Monsoon share of division's rainfall year (%)")
ax.set_title("B. Monsoon share by subdivision")
ax.set_xlim(0, 100)
savefig(fig, "fig1_seasonality.png")

# ══════════════════════════════════════════════════════════════════════════════
# C. REGIONAL VARIABILITY — CV, ANOVA, Levene, Welch, eta^2
# ══════════════════════════════════════════════════════════════════════════════
hdr("C. REGIONAL VARIABILITY")
div_stats = []
for d in divisions:
    s = ann[ann["division"] == d]["rainfall_mm"]
    m, sd = s.mean(), s.std(ddof=1)
    div_stats.append({
        "division": d, "mean": m, "std": sd, "cv": 100 * sd / m,
        "min": s.min(), "max": s.max(),
        "skew": stats.skew(s), "kurtosis": stats.kurtosis(s),
        "p5": np.percentile(s, 5), "p95": np.percentile(s, 95),
        "drought_pct": 100 * (s < 0.75 * m).mean(),
        "deficit_pct": 100 * (s < 0.90 * m).mean(),
    })
div_df = pd.DataFrame(div_stats).set_index("division")

say("Per-division annual statistics (top/bottom 5 by CV):")
cols = ["mean", "cv", "deficit_pct", "drought_pct"]
say(div_df[cols].round(1).sort_values("cv", ascending=False).head(5).to_string())
say("  ...")
say(div_df[cols].round(1).sort_values("cv", ascending=False).tail(5).to_string())

# Group values for ANOVA
groups = [ann[ann["division"] == d]["rainfall_mm"].values for d in divisions]

# Classical one-way ANOVA (for reference) + Levene variance homogeneity
F_cl, p_cl = stats.f_oneway(*groups)
lev_W, lev_p = stats.levene(*groups, center="median")
grand = ann["rainfall_mm"].mean()
ss_total = ((ann["rainfall_mm"] - grand) ** 2).sum()
ss_between = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
eta2 = ss_between / ss_total

# Welch ANOVA (does not assume equal variances) — Welch (1951) formulation
k = len(groups)
n_g = np.array([len(g) for g in groups])
m_g = np.array([g.mean() for g in groups])
v_g = np.array([g.var(ddof=1) for g in groups])
w = n_g / v_g
W = w.sum()
m_w = (w * m_g).sum() / W
A = (w * (m_g - m_w) ** 2).sum() / (k - 1)
B = (2.0 * (k - 2) / (k ** 2 - 1)) * (((1.0 - w / W) ** 2 / (n_g - 1)).sum())
F_w = A / (1.0 + B)
df2_w = 1.0 / ((3.0 / (k ** 2 - 1)) * (((1.0 - w / W) ** 2 / (n_g - 1)).sum()))
p_w = stats.f.sf(F_w, k - 1, df2_w)

regional = {
    "wettest_division": div_df["mean"].idxmax(),
    "wettest_mean": round(float(div_df["mean"].max()), 0),
    "driest_division": div_df["mean"].idxmin(),
    "driest_mean": round(float(div_df["mean"].min()), 0),
    "cv_min": round(float(div_df["cv"].min()), 1),
    "cv_min_division": div_df["cv"].idxmin(),
    "cv_max": round(float(div_df["cv"].max()), 1),
    "cv_max_division": div_df["cv"].idxmax(),
    "anova_F": round(float(F_cl), 1),
    "anova_p": float(p_cl),
    "levene_W": round(float(lev_W), 1),
    "levene_p": float(lev_p),
    "welch_F": round(float(F_w), 1),
    "welch_df2": round(float(df2_w), 1),
    "welch_p": float(p_w),
    "eta_squared": round(float(eta2), 3),
}
say(f"\nOne-way ANOVA (annual rainfall ~ division): F={F_cl:.1f}, p={p_cl:.2e}")
say(f"Levene (equal variances):        W={lev_W:.1f}, p={lev_p:.2e} -> variances differ, use Welch")
say(f"Welch ANOVA:                     F={F_w:.1f}, df2={df2_w:.1f}, p={p_w:.2e}")
say(f"Effect size eta^2 = {eta2:.3f}  (region explains {100*eta2:.1f}% of variance)")
say(f"Wettest: {regional['wettest_division']} ({regional['wettest_mean']:,.0f} mm/yr) | "
    f"Driest: {regional['driest_division']} ({regional['driest_mean']:,.0f} mm/yr)")
say(f"CV range: {regional['cv_min_division']} {regional['cv_min']}% (steadiest) to "
    f"{regional['cv_max_division']} {regional['cv_max']}% (least reliable)")
RESULTS["regional"] = regional

# ── Figure 2: regional means + CV ─────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.6))
ax = axes[0]
d_sorted = div_df.sort_values("mean", ascending=True)
cmap = plt.get_cmap("YlGnBu")
norm = plt.Normalize(d_sorted["cv"].min(), d_sorted["cv"].max())
ax.barh(range(len(d_sorted)), d_sorted["mean"], color=cmap(norm(d_sorted["cv"])), height=0.72)
ax.set_yticks(range(len(d_sorted)))
ax.set_yticklabels(d_sorted.index, fontsize=6.4)
ax.set_xlabel("Mean annual rainfall (mm/yr)")
ax.set_title("A. Mean annual rainfall (colour = CV)")
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cb = fig.colorbar(sm, ax=ax, pad=0.02)
cb.set_label("CV (%)", fontsize=8.5)
cb.ax.tick_params(labelsize=7.5)

ax = axes[1]
c_sorted = div_df.sort_values("cv", ascending=True)
bar_colors = [C_RED if v >= 35 else (C_AMBER if v >= 23 else C_MONSOON) for v in c_sorted["cv"]]
ax.barh(range(len(c_sorted)), c_sorted["cv"], color=bar_colors, height=0.72)
ax.set_yticks(range(len(c_sorted)))
ax.set_yticklabels(c_sorted.index, fontsize=6.4)
ax.set_xlabel("Coefficient of variation (%)")
ax.set_title("B. Rainfall reliability (CV) by subdivision")
ax.axvline(23, color=C_MUTED, ls=":", lw=1)
ax.axvline(35, color=C_MUTED, ls=":", lw=1)
ax.text(23.2, 0.2, "CV 23%", fontsize=7.5, color=C_MUTED)
ax.text(35.2, 0.2, "CV 35%", fontsize=7.5, color=C_MUTED)
savefig(fig, "fig2_regional_variability.png")

# ── Figure 3: ANOVA boxplot ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11.5, 4.8))
data_box = [ann[ann["division"] == d]["rainfall_mm"].values for d in
            div_df.sort_values("mean").index]
bp = ax.boxplot(data_box, showfliers=False, patch_artist=True, widths=0.6,
                medianprops=dict(color="white", lw=1.4),
                boxprops=dict(lw=0.8), whiskerprops=dict(color=C_MUTED, lw=0.8),
                capprops=dict(color=C_MUTED, lw=0.8))
cmap2 = plt.get_cmap("viridis")
norm2 = plt.Normalize(0, len(data_box) - 1)
for i, patch in enumerate(bp["boxes"]):
    patch.set_facecolor(cmap2(0.15 + 0.7 * i / max(len(bp["boxes"]) - 1, 1)))
ax.set_yscale("log")
ax.set_xticklabels(div_df.sort_values("mean").index, rotation=90, fontsize=6.4)
ax.set_ylabel("Annual rainfall (mm, log scale)")
ax.set_title("Annual rainfall distribution by subdivision (boxes = IQR, line = median)")
ax.text(0.985, 0.965,
        f"Welch ANOVA: F = {F_w:.0f}, p < 0.001\n$\\eta^2$ = {eta2:.3f} — region explains "
        f"{100*eta2:.0f}% of variance",
        transform=ax.transAxes, ha="right", va="top", fontsize=9.5,
        bbox=dict(boxstyle="round,pad=0.45", fc="#FEF3C7", ec=C_AMBER, lw=1))
savefig(fig, "fig3_anova_region.png")

# ══════════════════════════════════════════════════════════════════════════════
# D. DISTRIBUTION FITS — Normal vs Gamma vs Lognormal
# ══════════════════════════════════════════════════════════════════════════════
hdr("D. DISTRIBUTION FITS")


def fit_ks(x):
    """Fit Normal / Gamma / Lognormal by MLE (loc=0 for Gamma) and return KS distances."""
    out = {}
    mu, sd = stats.norm.fit(x)
    out["normal"] = stats.kstest(x, stats.norm(mu, sd).cdf).statistic
    a, loc, sc = stats.gamma.fit(x, floc=0)
    out["gamma"] = stats.kstest(x, stats.gamma(a, loc, sc).cdf).statistic
    s_ln, loc_ln, sc_ln = stats.lognorm.fit(x, floc=0)
    out["lognormal"] = stats.kstest(x, stats.lognorm(s_ln, loc_ln, sc_ln).cdf).statistic
    return out, (mu, sd), (a, loc, sc), (s_ln, loc_ln, sc_ln)


# Pooled monsoon (JAS) totals — the review-1 comparison variable
jas = sea[sea["season"] == "JAS"]["rainfall_mm"].values
ks_jas, (mu_j, sd_j), (a_j, loc_j, sc_j), (s_j, loc_j2, sc_j2) = fit_ks(jas)
skew_jas = stats.skew(jas)
kurt_jas = stats.kurtosis(jas)
sh_jas = stats.shapiro(jas)

# Pooled annual totals
annv = ann["rainfall_mm"].values
ks_ann, _, _, _ = fit_ks(annv)
skew_ann = stats.skew(annv)

# Per-division best fit (on standardised series so scale-mixing does not dominate)
best_counts = {"normal": 0, "gamma": 0, "lognormal": 0}
for d in divisions:
    s = ann[ann["division"] == d]["rainfall_mm"].values
    ks_d, _, _, _ = fit_ks(s)
    best_counts[min(ks_d, key=ks_d.get)] += 1

distributions = {
    "pooled_jas": {
        "n": int(len(jas)), "skew": round(float(skew_jas), 2),
        "excess_kurtosis": round(float(kurt_jas), 2),
        "shapiro_W": round(float(sh_jas.statistic), 3), "shapiro_p": float(sh_jas.pvalue),
        "ks_normal": round(float(ks_jas["normal"]), 3),
        "ks_gamma": round(float(ks_jas["gamma"]), 3),
        "ks_lognormal": round(float(ks_jas["lognormal"]), 3),
    },
    "pooled_annual": {
        "skew": round(float(skew_ann), 2),
        "ks_normal": round(float(ks_ann["normal"]), 3),
        "ks_gamma": round(float(ks_ann["gamma"]), 3),
        "ks_lognormal": round(float(ks_ann["lognormal"]), 3),
    },
    "best_fit_division_counts": best_counts,
}
say(f"Pooled monsoon (Jun-Sep) totals: n={len(jas)}, skew={skew_jas:.2f}, "
    f"excess kurtosis={kurt_jas:.2f}")
say(f"  Shapiro-Wilk: W={sh_jas.statistic:.3f}, p={sh_jas.pvalue:.2e} -> not normal")
say(f"  KS distance  : Normal {ks_jas['normal']:.3f} | Gamma {ks_jas['gamma']:.3f} | "
    f"Lognormal {ks_jas['lognormal']:.3f}")
say(f"Pooled annual totals: skew={skew_ann:.2f}; KS Normal {ks_ann['normal']:.3f} | "
    f"Gamma {ks_ann['gamma']:.3f} | Lognormal {ks_ann['lognormal']:.3f}")
say(f"Best fit per division (by KS): {best_counts}")
RESULTS["distributions"] = distributions

# ── Figure 4: distribution fits ───────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
ax = axes[0]
ax.hist(jas, bins=48, density=True, color="#BFDBFE", edgecolor="#60A5FA", lw=0.3, label="Observed (pooled Jun-Sep)")
xs = np.linspace(jas.min(), jas.max(), 400)
ax.plot(xs, stats.norm.pdf(xs, mu_j, sd_j), color=C_RED, lw=2,
        label=f"Normal (KS D={ks_jas['normal']:.3f})")
ax.plot(xs, stats.gamma.pdf(xs, a_j, loc_j, sc_j), color=C_MONSOON, lw=2,
        label=f"Gamma (KS D={ks_jas['gamma']:.3f})")
ax.plot(xs, stats.lognorm.pdf(xs, s_j, loc_j2, sc_j2), color=C_AMBER, lw=2, ls="--",
        label=f"Lognormal (KS D={ks_jas['lognormal']:.3f})")
ax.set_xlabel("Seasonal rainfall total (mm)")
ax.set_ylabel("Density")
ax.set_title("A. Pooled monsoon totals: candidate distributions")
ax.legend(fontsize=8.5, framealpha=0.95, loc="upper right")
ax.set_xlim(0, jas.max() * 1.02)

ax = axes[1]
labels_d = ["Normal", "Gamma", "Lognormal"]
vals_d = [best_counts["normal"], best_counts["gamma"], best_counts["lognormal"]]
bars = ax.bar(labels_d, vals_d, color=[C_RED, C_MONSOON, C_AMBER], width=0.55)
for b, v in zip(bars, vals_d):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.4, f"{v}/36", ha="center",
            fontweight="bold", fontsize=10)
ax.set_ylabel("Divisions where fit is best (KS)")
ax.set_title("B. Best-fitting model per subdivision")
ax.set_ylim(0, max(vals_d) * 1.25)
savefig(fig, "fig4_distribution_fits.png")

# ══════════════════════════════════════════════════════════════════════════════
# E. TREND ANALYSIS — OLS + Mann-Kendall + Sen's slope + BH
# ══════════════════════════════════════════════════════════════════════════════
hdr("E. TREND ANALYSIS (1901-2015)")


def sens_slope(x, y):
    """Median of pairwise slopes (Sen's estimator)."""
    n = len(x)
    sl = [(y[j] - y[i]) / (x[j] - x[i]) for i in range(n) for j in range(i + 1, n)]
    return float(np.median(sl))


def bh_adjust(pvals):
    """Benjamini-Hochberg FDR adjustment (returns adjusted q-values)."""
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    order = np.argsort(p)
    q = p[order] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.minimum(q, 1.0)
    return out


trend_rows = []
for d in divisions:
    g = ann[ann["division"] == d].sort_values("year")
    x, y = g["year"].values.astype(float), g["rainfall_mm"].values
    lr = stats.linregress(x, y)                       # OLS: slope, p
    mk = stats.kendalltau(x, y)                       # Mann-Kendall: tau, p
    trend_rows.append({
        "division": d,
        "ols_slope": lr.slope, "ols_p": lr.pvalue, "ols_r2": lr.rvalue ** 2,
        "mk_tau": mk.statistic, "mk_p": mk.pvalue,
        "sens_slope": sens_slope(x, y),
    })
tr = pd.DataFrame(trend_rows).set_index("division")
tr["bh_q"] = bh_adjust(tr["ols_p"].values)
tr["sig_raw"] = tr["ols_p"] < 0.05
tr["sig_bh"] = tr["bh_q"] < 0.05

# National trend with 95% CI on the mean response
x_nat = nat.index.values.astype(float)
y_nat = nat.values
lr_nat = stats.linregress(x_nat, y_nat)
yhat = lr_nat.slope * x_nat + lr_nat.intercept
n_nat = len(x_nat)
se_fit = np.sqrt(((y_nat - yhat) ** 2).sum() / (n_nat - 2)) * \
    np.sqrt(1 / n_nat + (x_nat - x_nat.mean()) ** 2 / ((x_nat - x_nat.mean()) ** 2).sum())
tcrit = stats.t.ppf(0.975, n_nat - 2)
ci_band = tcrit * se_fit

trends = {
    "national_slope_mm_per_yr": round(float(lr_nat.slope), 3),
    "national_p": float(lr_nat.pvalue),
    "national_slope_mm_per_century": round(float(lr_nat.slope * 100), 1),
    "national_slope_ci95_per_century": [
        round(float((lr_nat.slope - tcrit * lr_nat.stderr) * 100), 1),
        round(float((lr_nat.slope + tcrit * lr_nat.stderr) * 100), 1),
    ],
    "sig_raw_count": int(tr["sig_raw"].sum()),
    "sig_bh_count": int(tr["sig_bh"].sum()),
    "sign_agreement_ols_mk": int(((tr["ols_slope"] > 0) == (tr["mk_tau"] > 0)).sum()),
    "n_divisions": int(len(tr)),
    "mean_sens_slope": round(float(tr["sens_slope"].mean()), 3),
    "bh_significant_divisions": tr.index[tr["sig_bh"]].tolist(),
    "raw_significant_divisions": tr.index[tr["sig_raw"]].tolist(),
}
say(f"National annual series: OLS slope = {lr_nat.slope:+.3f} mm/yr "
    f"({lr_nat.slope*100:+.1f} mm/century), p = {lr_nat.pvalue:.3f}")
say(f"Divisions with p < 0.05 (uncorrected): {trends['sig_raw_count']} of 36")
say(f"Divisions significant after BH (5% FDR): {trends['sig_bh_count']} of 36 -> "
    f"{', '.join(trends['bh_significant_divisions'][:12])}"
    f"{' ...' if len(trends['bh_significant_divisions']) > 12 else ''}")
say(f"OLS and Mann-Kendall agree on trend sign: {trends['sign_agreement_ols_mk']} of 36")
say(f"Mean Sen's slope: {trends['mean_sens_slope']:+.3f} mm/yr")
say("\nStrongest trends (by |Sen's slope|):")
say(tr.assign(abs_sens=tr["sens_slope"].abs())
      .sort_values("abs_sens", ascending=False)[["ols_slope", "ols_p", "bh_q", "sens_slope"]]
      .head(6).round(4).to_string())
RESULTS["trends"] = trends

# ── Figure 5: trends ──────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
ax = axes[0]
ax.fill_between(x_nat, yhat - ci_band, yhat + ci_band, color=C_MONSOON, alpha=0.16,
                label="95% CI of trend line")
ax.plot(x_nat, y_nat, color=C_MUTED, lw=0.9, alpha=0.75, label="National annual mean")
ax.plot(x_nat, yhat, color=C_MONSOON, lw=2.2,
        label=f"OLS trend {lr_nat.slope*100:+.1f} mm/century (p={lr_nat.pvalue:.2f})")
ax.set_xlabel("Year")
ax.set_ylabel("National mean annual rainfall (mm)")
ax.set_title("A. All-India trend with uncertainty")
ax.legend(fontsize=8.5, loc="upper left", framealpha=0.95, edgecolor="#CBD5E1")

ax = axes[1]
t_sorted = tr.sort_values("ols_slope", ascending=False)
colors_t = [C_MONSOON if q else "#CBD5E1" for q in t_sorted["sig_bh"]]
ax.bar(range(len(t_sorted)), t_sorted["ols_slope"], color=colors_t, width=0.75)
ax.set_xticks(range(len(t_sorted)))
ax.set_xticklabels(t_sorted.index, rotation=90, fontsize=6.2)
ax.axhline(0, color="#334155", lw=0.9)
ax.set_ylabel("OLS slope (mm/yr)")
ax.set_title(f"B. Trend by subdivision (green = BH-significant, {trends['sig_bh_count']}/36)")
savefig(fig, "fig5_trends.png")

# ══════════════════════════════════════════════════════════════════════════════
# F. DROUGHT & EXTREMES
# ══════════════════════════════════════════════════════════════════════════════
hdr("F. DROUGHT & EXTREMES")
nat_normal = nat.mean()
below90 = nat[nat < 0.90 * nat_normal]
below75 = nat[nat < 0.75 * nat_normal]
driest_year = int(nat.idxmin())
wettest_year = int(nat.idxmax())

# 1-in-20-year level (empirical 5th percentile) as % of normal, per division
div_df["p5_pct_of_normal"] = 100 * div_df["p5"] / div_df["mean"]
vuln = div_df.sort_values("p5_pct_of_normal")

drought = {
    "national_normal_mm": round(float(nat_normal), 0),
    "national_below90_count": int(len(below90)),
    "national_below90_years": [int(y) for y in below90.index],
    "national_below75_count": int(len(below75)),
    "driest_year": driest_year,
    "driest_year_mm": round(float(nat.min()), 0),
    "driest_year_pct_of_normal": round(float(100 * nat.min() / nat_normal), 1),
    "wettest_year": wettest_year,
    "wettest_year_mm": round(float(nat.max()), 0),
    "most_vulnerable_division": vuln.index[0],
    "most_vulnerable_1in20_pct": round(float(vuln["p5_pct_of_normal"].iloc[0]), 1),
    "most_stable_division": vuln.index[-1],
    "most_stable_1in20_pct": round(float(vuln["p5_pct_of_normal"].iloc[-1]), 1),
    "mean_1in20_pct": round(float(div_df["p5_pct_of_normal"].mean()), 1),
    "divisions_with_severe_drought_years": int((div_df["drought_pct"] > 0).sum()),
    "mean_drought_frequency_pct": round(float(div_df["drought_pct"].mean()), 1),
}
say(f"National normal (1901-2015): {nat_normal:,.0f} mm")
say(f"Years below 90% of normal: {len(below90)} of {len(nat)} -> {[int(y) for y in below90.index]}")
say(f"Years below 75% of normal (severe): {len(below75)}")
say(f"Driest year: {driest_year} ({nat.min():,.0f} mm, "
    f"{100*nat.min()/nat_normal:.1f}% of normal) | Wettest: {wettest_year} ({nat.max():,.0f} mm)")
say(f"\n1-in-20-year annual level (5th percentile) as % of division normal:")
say(f"  most vulnerable : {drought['most_vulnerable_division']} "
    f"({drought['most_vulnerable_1in20_pct']}% of normal)")
say(f"  most stable     : {drought['most_stable_division']} "
    f"({drought['most_stable_1in20_pct']}% of normal)")
say(f"  mean across 36  : {drought['mean_1in20_pct']}% of normal")
say("\nFive most vulnerable divisions (1-in-20-yr level, % of normal):")
say(vuln[["mean", "cv", "p5", "p5_pct_of_normal", "drought_pct"]].head(5).round(1).to_string())
RESULTS["drought"] = drought

# ── Figure 6: drought ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
ax = axes[0]
bar_c = [C_RED if v < 0.75 * nat_normal else (C_AMBER if v < 0.90 * nat_normal else "#86EFAC")
         for v in nat.values]
ax.bar(nat.index, nat.values, color=bar_c, width=0.75)
ax.axhline(nat_normal, color=C_MONSOON, lw=1.4, ls="--")
ax.axhline(0.90 * nat_normal, color=C_AMBER, lw=1.1, ls=":")
ax.axhline(0.75 * nat_normal, color=C_RED, lw=1.1, ls=":")
ax.text(0.015, 0.03,
        f"— — normal {nat_normal:,.0f} mm\n· · · 90% of normal\n· · · 75% of normal",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=8,
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#CBD5E1", lw=0.8, alpha=0.92))
ax.set_xlabel("Year")
ax.set_ylabel("National mean annual rainfall (mm)")
ax.set_title(f"A. All-India deficit years ({len(below90)}/{len(nat)} below 90%)")

ax = axes[1]
v_plot = vuln.copy()
bar_colors = [C_RED if v < 60 else (C_AMBER if v < 72 else C_MONSOON)
              for v in v_plot["p5_pct_of_normal"]]
ax.barh(range(len(v_plot)), v_plot["p5_pct_of_normal"], color=bar_colors, height=0.72)
ax.set_yticks(range(len(v_plot)))
ax.set_yticklabels(v_plot.index, fontsize=6.2)
ax.invert_yaxis()
ax.set_ylim(37.2, -0.8)
ax.axvline(drought["mean_1in20_pct"], color="#0F172A", ls="--", lw=1)
ax.text(drought["mean_1in20_pct"] + 1.2, 36.4, f"mean {drought['mean_1in20_pct']}%",
        fontsize=8, va="center")
ax.set_xlabel("1-in-20-year rainfall level (% of division normal)")
ax.set_title("B. Drought exposure is local (lower = harsher 1-in-20-yr deficit)")
ax.set_xlim(0, 100)
savefig(fig, "fig6_drought.png")

# ══════════════════════════════════════════════════════════════════════════════
# G. SPATIAL CORRELATION
# ══════════════════════════════════════════════════════════════════════════════
hdr("G. SPATIAL CORRELATION (shared weather)")
wide = ann.pivot(index="year", columns="division", values="rainfall_mm").sort_index()
corr = wide.corr()
iu = np.triu_indices(len(divisions), k=1)
rvals = corr.values[iu]
n_pairs = len(rvals)
# Critical two-sided 5% Pearson r for n=115 (df = 113): t / sqrt(t^2 + df)
t_c = stats.t.ppf(0.975, 113)
r_crit = float(t_c / np.sqrt(t_c ** 2 + 113))
sig_pairs = int((np.abs(rvals) > r_crit).sum())

correlation = {
    "n_pairs": int(n_pairs),
    "mean_r": round(float(np.mean(rvals)), 3),
    "median_r": round(float(np.median(rvals)), 3),
    "max_r": round(float(np.max(rvals)), 3),
    "min_r": round(float(np.min(rvals)), 3),
    "critical_r_5pct": round(r_crit, 3),
    "sig_pairs": sig_pairs,
    "sig_pair_pct": round(100 * sig_pairs / n_pairs, 1),
}
say(f"Pearson r across {n_pairs} division pairs (annual series, n=115 each):")
say(f"  mean r = {correlation['mean_r']}, median = {correlation['median_r']}, "
    f"range [{correlation['min_r']}, {correlation['max_r']}]")
say(f"  pairs significant at 5% (|r| > {r_crit:.3f}): {sig_pairs} of {n_pairs} "
    f"({correlation['sig_pair_pct']}%)")
say("  -> divisions share weather; 36 tests are not 36 independent samples")
RESULTS["correlation"] = correlation

# ── Figure 7: correlation heatmap ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7.6, 6.8))
im = ax.imshow(corr.values, cmap="RdYlGn", vmin=-1, vmax=1, interpolation="nearest")
ax.set_xticks(range(len(divisions)))
ax.set_yticks(range(len(divisions)))
ax.set_xticklabels(divisions, rotation=90, fontsize=5.6)
ax.set_yticklabels(divisions, fontsize=5.6)
ax.set_title(f"Pearson correlation of annual rainfall, 36 subdivisions\n"
             f"(mean r = {correlation['mean_r']}; {correlation['sig_pair_pct']}% of pairs significant at 5%)",
             fontsize=10.5)
cb = fig.colorbar(im, ax=ax, shrink=0.82)
cb.set_label("Pearson r", fontsize=9)
ax.grid(False)
path = R3 / "fig7_correlation_heatmap.png"
fig.savefig(path, dpi=150, bbox_inches="tight")
plt.close(fig)
say("[figure] fig7_correlation_heatmap.png")

# ══════════════════════════════════════════════════════════════════════════════
# H. TWO-ERA COMPARISON (1950-1980 vs 1981-2015, dashboard defaults)
# ══════════════════════════════════════════════════════════════════════════════
hdr("H. TWO-ERA COMPARISON (national)")
a = nat[(nat.index >= 1950) & (nat.index <= 1980)]
b = nat[(nat.index >= 1981) & (nat.index <= 2015)]
tt = stats.ttest_ind(b, a, equal_var=False)
mw = stats.mannwhitneyu(b, a, alternative="two-sided")
lev_ab = stats.levene(a, b, center="median")
eras = {
    "era_a": "1950-1980", "era_a_mean": round(float(a.mean()), 1), "era_a_n": int(len(a)),
    "era_b": "1981-2015", "era_b_mean": round(float(b.mean()), 1), "era_b_n": int(len(b)),
    "diff_mm": round(float(b.mean() - a.mean()), 1),
    "diff_pct": round(float(100 * (b.mean() - a.mean()) / a.mean()), 2),
    "welch_t": round(float(tt.statistic), 3), "welch_p": round(float(tt.pvalue), 4),
    "mannwhitney_p": round(float(mw.pvalue), 4),
    "levene_p": round(float(lev_ab.pvalue), 4),
}
say(f"Era A ({eras['era_a']}): {eras['era_a_mean']} mm/yr (n={eras['era_a_n']})")
say(f"Era B ({eras['era_b']}): {eras['era_b_mean']} mm/yr (n={eras['era_b_n']})")
say(f"Difference: {eras['diff_mm']:+.1f} mm ({eras['diff_pct']:+.2f}%)")
say(f"Welch t-test: t={eras['welch_t']}, p={eras['welch_p']} | Mann-Whitney p={eras['mannwhitney_p']}")
RESULTS["two_era"] = eras

# ══════════════════════════════════════════════════════════════════════════════
# EXPORT TABLES + JSON + RAW LOG
# ══════════════════════════════════════════════════════════════════════════════
hdr("EXPORTS")
div_out = div_df.copy()
div_out["bh_q"] = tr["bh_q"]
div_out["ols_slope"] = tr["ols_slope"]
div_out["sig_bh"] = tr["sig_bh"]
div_out.round(2).to_csv(R3 / "division_statistics.csv")
say("[table] review_3/division_statistics.csv")

with open(R3 / "analysis_results.json", "w") as f:
    json.dump(RESULTS, f, indent=2)
say("[json]   review_3/analysis_results.json")

(RES / "_final_analysis_raw.txt").write_text("\n".join(LINES) + "\n", encoding="utf-8")
say("[log]    research/_final_analysis_raw.txt")
say("")
say("Review 3 analysis complete.")
