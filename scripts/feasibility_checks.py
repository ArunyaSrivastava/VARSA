#!/usr/bin/env python3
"""
feasibility_checks.py — Statistical feasibility checks for prob_project.

Performs the statistical methods appropriate to the research question, prints
results to stdout (tee'd to research/_feasibility_raw.txt for Review 2).

Methods included (pick what applies to your project):
- Descriptive statistics
- Distribution fit (Shapiro-Wilk normality)
- t-test / Mann-Whitney (two groups)
- One-way ANOVA (>= 3 groups)
- Correlation (Pearson / Spearman)
- Chi-square test of independence

Usage:
    python scripts/feasibility_checks.py
    python scripts/feasibility_checks.py --test anova
"""

import argparse
import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = "data/raw"


def load_data(name: str) -> pd.DataFrame:
    """Load a dataset. Replace with your actual data loading."""
    # Example: load from CSV
    path = f"{DATA_DIR}/{name}.csv"
    return pd.read_csv(path)


def describe(df: pd.DataFrame) -> None:
    print("=== Descriptive Stats ===")
    print(df.describe(include="all").to_string())
    print()


def normality_test(series: pd.Series, name: str) -> None:
    """Shapiro-Wilk normality test."""
    valid = series.dropna()
    if len(valid) < 3:
        print(f"=== {name}: skipped (too few valid values) ===")
        return
    stat, p = stats.shapiro(valid)
    print(f"=== {name} (Shapiro-Wilk) ===")
    print(f"  stat={stat:.4f}, p={p:.4f} -> {'likely normal' if p > 0.05 else 'not normal'}")
    print()


def t_test(group1: pd.Series, group2: pd.Series, name: str) -> None:
    """Independent t-test (or Mann-Whitney if not normal)."""
    print(f"=== {name} (t-test) ===")
    if stats.shapiro(group1.dropna()).pvalue > 0.05 and stats.shapiro(group2.dropna()).pvalue > 0.05:
        t, p = stats.ttest_ind(group1, group2, equal_var=False)
        print(f"  t={t:.4f}, p={p:.4f} -> {'significant' if p < 0.05 else 'not significant'}")
    else:
        u, p = stats.mannwhitneyu(group1, group2, alternative="two-sided")
        print(f"  U={u:.4f}, p={p:.4f} -> {'significant' if p < 0.05 else 'not significant'} (Mann-Whitney)")


def anova(*groups: pd.Series, name: str) -> None:
    """One-way ANOVA."""
    valid_groups = [g.dropna() for g in groups if len(g.dropna()) > 0]
    if len(valid_groups) < 2:
        print(f"=== {name}: skipped (need >= 2 groups) ===")
        return
    F, p = stats.f_oneway(*valid_groups)
    print(f"=== {name} (one-way ANOVA) ===")
    print(f"  F={F:.4f}, p={p:.4f} -> {'significant' if p < 0.05 else 'not significant'}")


def correlation(x: pd.Series, y: pd.Series, name: str) -> None:
    """Pearson and Spearman correlation."""
    dx = x.dropna()
    dy = y.loc[dx.index].dropna()
    if len(dx) < 3:
        print(f"=== {name}: skipped (too few valid values) ===")
        return
    r_pearson, p_pearson = stats.pearsonr(dx, dy)
    r_spearman, p_spearman = stats.spearmanr(dx, dy)
    print(f"=== {name} (correlation) ===")
    print(f"  Pearson:  r={r_pearson:.4f}, p={p_pearson:.4f}")
    print(f"  Spearman: r={r_spearman:.4f}, p={p_spearman:.4f}")


def chi_square(df: pd.DataFrame, col1: str, col2: str, name: str) -> None:
    """Chi-square test of independence between two categorical columns."""
    contingency = pd.crosstab(df[col1], df[col2])
    if contingency.shape[0] < 2 or contingency.shape[1] < 2:
        print(f"=== {name}: skipped (need 2x2+ table) ===")
        return
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    print(f"=== {name} (chi-square) ===")
    print(f"  chi2={chi2:.4f}, dof={dof}, p={p:.4f} -> {'significant' if p < 0.05 else 'not significant'}")


def main():
    parser = argparse.ArgumentParser(description="Statistical feasibility checks.")
    parser.add_argument("--test", choices=["anova", "t", "corr", "chisq", "all"], default="all",
                        help="Which test to run (default: all)")
    args = parser.parse_args()

    # --- Load your data here ---
    # Replace with your actual data loading
    # df = load_data("spotify")
    # desc(df)

    if args.test in ("t", "all"):
        # Example: t-test between two groups
        pass

    if args.test in ("anova", "all"):
        # Example: ANOVA across 3+ groups
        pass

    if args.test in ("corr", "all"):
        # Example: correlation between two numeric columns
        pass

    if args.test in ("chisq", "all"):
        # Example: chi-square between two categorical columns
        pass

    print("=== Feasibility checks complete ===")


if __name__ == "__main__":
    main()
