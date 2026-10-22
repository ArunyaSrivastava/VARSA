# Review 2 — Statistical Analysis

**Stage:** Review 2 (70% of work, 20 marks)

---

## 1. Methods & Rationale

For each research question, state:

| Research Question | Method Used | Why This Method | Assumption Check |
|---|---|---|---|
| (e.g. "Does genre affect popularity?") | (e.g. one-way ANOVA) | (e.g. comparing ≥3 group means) | (e.g. normality, equal variances) |
| (e.g. "Do audio features correlate with popularity?") | (e.g. Pearson/Spearman correlation) | (e.g. linear association) | (e.g. monotonic, no outliers) |
| (e.g. "Is there a difference between explicit and clean tracks?") | (e.g. t-test / Mann–Whitney) | (e.g. two-group comparison) | (e.g. normality, equal variances) |

Add rows for each question + method.

---

## 2. Statistical Checks Performed

List the checks you ran and their outcomes:

- Distribution fits (e.g. normal, log-normal) — results
- Normality tests (Shapiro–Wilk or similar) — results
- Variance equality tests (Levene or similar) — results
- Homoscedasticity, independence, linearity checks (as applicable)
- Multiple-comparison corrections (e.g. Benjamini–Hochberg) — applied if many tests

---

## 3. Results Summary

| RQ / Hypothesis | Test Statistic | p-value | Effect Size | Decision |
|---|---|---|---|---|
| (e.g. genre affects popularity) | (F = 343.5) | (< 0.001) | (η² = 0.254) | (significant) |
| (e.g. audio features predict popularity) | (multiple regression R² = 0.022) | (< 0.001) | (R²) | (significant but small) |

Add rows for each result.

---

## 4. Feature / Variable Importance

- If doing regression: which features were most predictive?
- If doing ANOVA: which categories differ most?
- If doing classification: which features matter most?

---

## 5. Reproducible Analysis Script

```bash
python scripts/feasibility_checks.py | tee research/_feasibility_raw.txt
```

(Fill in the actual command from your project.)

---

## 6. Interpretation

- What do the results mean in plain terms?
- Is the effect practically meaningful, even if statistically significant?
- What are the limitations of the analysis (sample, collection method, etc.)?

---

## 7. Next Step (Review 3)

Move to `review_3/final_report.md` and compile the final report from this analysis.
