#!/usr/bin/env python3
"""
feasibility_checks.py — quick statistical feasibility checks for VARSA.

Prints a compact summary of the headline tests (audit snapshot, Levene → Welch ANOVA,
distribution fits, trend counts with BH correction, drought benchmarks). This is the
Review 2 entry point; the full pipeline with figures is scripts/final_analysis.py.

Usage:
    python scripts/feasibility_checks.py
    python scripts/feasibility_checks.py --test anova
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "raw" / "india_rainfall.csv"


def load() -> pd.DataFrame:
    return pd.read_csv(DATA)


def describe(df: pd.DataFrame) -> None:
    ann = df[df["season"] == "ANNUAL"]
    print("=== Dataset snapshot ===")
    print(f"  rows={len(df)}, divisions={ann['division'].nunique()}, "
          f"years={ann['year'].nunique()} ({ann['year'].min()}-{ann['year'].max()})")
    print(f"  missing={df.isna().sum().sum()}, duplicates={df.duplicated().sum()}")
    nat = ann.groupby("year")["rainfall_mm"].mean()
    print(f"  national annual: mean={nat.mean():.0f} mm, sd={nat.std():.0f}, "
          f"min={nat.min():.0f} ({nat.idxmin()}), max={nat.max():.0f} ({nat.idxmax()})")
    print()


def seasonality(df: pd.DataFrame) -> None:
    sea = df[df["season"] != "ANNUAL"]
    means = sea.groupby("season")["rainfall_mm"].mean()
    share = 100 * means / means.sum()
    print("=== Seasonality (RQ1) ===")
    for s in ["DJF", "MAM", "JAS", "OND"]:
        print(f"  {s}: {means[s]:7.1f} mm  ({share[s]:.1f}%)")
    print()


def anova(df: pd.DataFrame) -> None:
    ann = df[df["season"] == "ANNUAL"]
    groups = [ann[ann["division"] == d]["rainfall_mm"].values
              for d in ann["division"].unique()]
    lev_W, lev_p = stats.levene(*groups, center="median")
    F_cl, _ = stats.f_oneway(*groups)
    grand = ann["rainfall_mm"].mean()
    ss_t = ((ann["rainfall_mm"] - grand) ** 2).sum()
    ss_b = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    eta2 = ss_b / ss_t
    # Welch ANOVA (Welch 1951)
    k = len(groups)
    n_g = np.array([len(g) for g in groups])
    m_g = np.array([g.mean() for g in groups])
    v_g = np.array([g.var(ddof=1) for g in groups])
    w = n_g / v_g
    W = w.sum()
    m_w = (w * m_g).sum() / W
    A = (w * (m_g - m_w) ** 2).sum() / (k - 1)
    B = (2 * (k - 2) / (k ** 2 - 1)) * (((1 - w / W) ** 2 / (n_g - 1)).sum())
    F_w = A / (1 + B)
    df2 = 1 / ((3 / (k ** 2 - 1)) * (((1 - w / W) ** 2 / (n_g - 1)).sum()))
    p_w = stats.f.sf(F_w, k - 1, df2)
    print("=== Regional variability (RQ2) ===")
    print(f"  Levene (equal variances): W={lev_W:.1f}, p={lev_p:.2e} -> use Welch ANOVA")
    print(f"  classical ANOVA (ref):  F={F_cl:.1f}")
    print(f"  Welch ANOVA:            F({k-1:.0f},{df2:.0f})={F_w:.1f}, p={p_w:.2e}")
    print(f"  eta^2 = {eta2:.3f} (region explains {100*eta2:.0f}% of variance)")
    print()


def distributions(df: pd.DataFrame) -> None:
    jas = df[df["season"] == "JAS"]["rainfall_mm"].values
    mu, sd = stats.norm.fit(jas)
    ks_n = stats.kstest(jas, stats.norm(mu, sd).cdf).statistic
    a, loc, sc = stats.gamma.fit(jas, floc=0)
    ks_g = stats.kstest(jas, stats.gamma(a, loc, sc).cdf).statistic
    s_ln, loc_ln, sc_ln = stats.lognorm.fit(jas, floc=0)
    ks_l = stats.kstest(jas, stats.lognorm(s_ln, loc_ln, sc_ln).cdf).statistic
    sh = stats.shapiro(jas)
    print("=== Distribution fits (RQ3, pooled Jun-Sep totals) ===")
    print(f"  skew={stats.skew(jas):.2f}; Shapiro-Wilk W={sh.statistic:.3f}, p={sh.pvalue:.1e}")
    print(f"  KS distance: Normal={ks_n:.3f}, Gamma={ks_g:.3f}, Lognormal={ks_l:.3f}")
    print()


def trends(df: pd.DataFrame) -> None:
    ann = df[df["season"] == "ANNUAL"]
    slopes, pvals, taus = [], [], []
    for d, g in ann.groupby("division"):
        lr = stats.linregress(g["year"], g["rainfall_mm"])
        mk = stats.kendalltau(g["year"], g["rainfall_mm"])
        slopes.append(lr.slope)
        pvals.append(lr.pvalue)
        taus.append(mk.statistic)
    p = np.sort(np.asarray(pvals))
    n = len(p)
    q = np.minimum.accumulate((p * n / (np.arange(n) + 1))[::-1])[::-1]
    raw = int((np.asarray(pvals) < 0.05).sum())
    bh = int((q < 0.05).sum())
    agree = int(((np.asarray(slopes) > 0) == (np.asarray(taus) > 0)).sum())
    print("=== Trends (RQ4, 1901-2015) ===")
    print(f"  divisions with raw p < 0.05: {raw} of {n}")
    print(f"  divisions significant after BH (5% FDR): {bh} of {n}")
    print(f"  OLS / Mann-Kendall sign agreement: {agree} of {n}")
    print()


def drought(df: pd.DataFrame) -> None:
    ann = df[df["season"] == "ANNUAL"]
    nat = ann.groupby("year")["rainfall_mm"].mean()
    normal = nat.mean()
    below90 = int((nat < 0.90 * normal).sum())
    print("=== Drought (RQ5) ===")
    print(f"  national normal: {normal:.0f} mm; years below 90%: {below90} of {len(nat)}")
    rows = []
    for d, g in ann.groupby("division"):
        m = g["rainfall_mm"].mean()
        rows.append((d, 100 * np.percentile(g["rainfall_mm"], 5) / m))
    rows.sort(key=lambda r: r[1])
    print(f"  1-in-20-yr level, most vulnerable: {rows[0][0]} ({rows[0][1]:.1f}% of normal)")
    print(f"  1-in-20-yr level, most stable:     {rows[-1][0]} ({rows[-1][1]:.1f}% of normal)")
    print()


TESTS = {
    "describe": describe,
    "seasonality": seasonality,
    "anova": anova,
    "corr": None,
    "distributions": distributions,
    "trends": trends,
    "drought": drought,
}


def main():
    parser = argparse.ArgumentParser(description="Statistical feasibility checks.")
    parser.add_argument("--test", choices=list(TESTS) + ["all"], default="all",
                        help="Which check to run (default: all)")
    args = parser.parse_args()

    if not DATA.exists():
        print("No data found — run: bash scripts/fetch_data.sh")
        return
    df = load()
    keys = list(TESTS) if args.test == "all" else [args.test]
    for key in keys:
        fn = TESTS[key]
        if fn is not None:
            fn(df)
    print("=== Feasibility checks complete ===")


if __name__ == "__main__":
    main()
