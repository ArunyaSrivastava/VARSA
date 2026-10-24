# Review 2 — Statistical Analysis

**Stage:** Review 2 (70% of work, 20 marks)

> Numbers marked **[R1]** were computed on the reference (raw IMD) layer and presented at
> Review 1; numbers marked **[P]** are from the reproducible pipeline layer
> (`scripts/final_analysis.py`). Both are reported so the two layers can be compared;
> Review 3 (§5.6 of the final report) reconciles them.

---

## 1. Methods & Rationale

| Research Question | Method Used | Why This Method | Assumption Check |
|---|---|---|---|
| RQ1 — how concentrated is the monsoon? | Seasonal means/shares; one-way ANOVA across seasons | quantifies concentration + variance share | large n per season; η² reported |
| RQ2 — do divisions differ? | Per-division CV; Levene test → Welch ANOVA; η² | 36 groups with unequal variances | Levene rejects equal variances on both layers → Welch, not ordinary ANOVA |
| RQ3 — which distribution fits? | MLE fits (Normal, Gamma, Lognormal) + KS distance; Shapiro–Wilk | nonparametric goodness-of-fit comparison | fits judged per-division and pooled — unit of analysis stated |
| RQ4 — which divisions trend? | OLS slope + p; Mann–Kendall τ; Sen's slope; BH-FDR over 36 tests | linear + rank-based trend with multiplicity control | OLS vs MK sign agreement 36/36 **[P]** |
| RQ5 — how deep is a 1-in-20-year deficit? | Deficit counts (<90%, <75% of normal); empirical 5th percentile | return level from the record, no parametric assumption | no extrapolation beyond the record |

---

## 2. Statistical Checks Performed

- **Distribution fits:** pooled monsoon totals right-skewed — skew 1.51 **[R1]** /
  1.39 **[P]**; Lognormal best, Gamma second, Normal clearly worst (KS below).
- **Normality:** Shapiro–Wilk on pooled monsoon totals W = 0.829, p ≈ 5.5×10⁻⁵⁵ **[P]** —
  normality rejected; within divisions, 33 of 36 annual series are best fit by the Normal **[P]**.
- **Variance equality:** Levene W = 53.4 **[R1]** / W = 27.8, p ≈ 1.2×10⁻¹⁶¹ **[P]** —
  equal variances rejected → Welch ANOVA everywhere.
- **Independence:** 78.6% **[R1]** / 64.9% **[P]** of division pairs correlate significantly —
  dependence carried as a limitation, not assumed away.
- **Multiple comparisons:** Benjamini–Hochberg at 5% FDR applied to every family of 36
  divisional trend tests.

---

## 3. Results Summary

| RQ / Hypothesis | Test Statistic | p-value | Effect Size | Decision |
|---|---|---|---|---|
| Season explains rainfall variance **[P]** | F = 5,785.6 | < 0.001 | η² = 0.512 | significant |
| Region explains rainfall variance **[P]** | Welch F(35, 1445) = 588.5 (classical F = 727.2) | < 0.001 | η² = 0.861 (**[R1]** 0.875) | significant |
| Pooled monsoon totals normal? **[P]** | Shapiro–Wilk W = 0.829 | ≈ 10⁻⁵⁵ | — | rejected: use Gamma/Lognormal |
| Gamma fits better than Normal **[P]** | KS D 0.094 vs 0.185 (Lognormal 0.069) | — | — | Lognormal best pooled |
| Divisional trends, uncorrected **[P]** | 3 of 36 raw p < 0.05 (**[R1]** 16 of 36) | — | — | see next row |
| Divisional trends after BH **[P]** | **0 of 36** at 5% FDR (**[R1]** 9 of 36); smallest q = 0.44 | — | — | no division significant |
| National trend **[P]** | −34.1 mm/century, 95% CI [−116.7, +48.5] | 0.415 | — | no trend detected |
| Two-era shift (1950–80 vs 1981–2015) **[P]** | Welch t = −0.325 | 0.746 | −0.96% | no shift |
| 1-in-20-year deficit **[P]** | empirical 5th percentile | — | W Rajasthan 15.8% of normal; Kerala 77.8% (**[R1]** 47.6% / 77.8%) | drought risk is local |

---

## 4. Feature / Variable Importance

- **Region is the dominant factor** for annual rainfall (η² = 0.86 **[P]**): the
  north-west arid arc (Ladakh, West Rajasthan, Marathwada) combines the lowest means
  with the highest CV — least rain *and* least reliable.
- The wet belt (Konkan & Goa, Arunachal Pradesh, Kerala, Assam & Meghalaya) is both wet
  and steady (CV ≤ 20%).
- Trend magnitude is small relative to inter-annual variability everywhere: no division's
  Sen's slope exceeds ~2 mm/yr **[P]**.

---

## 5. Reproducible Analysis Script

```bash
python scripts/final_analysis.py | tee research/_final_analysis_raw.txt
# machine-readable results: review_3/analysis_results.json
```

---

## 6. Interpretation

- **What the results mean:** the rainfall year is structurally monsoonal (~74% in four
  months, everywhere); where you are matters far more than which decade you pick;
  pooled modelling must use skewed distributions, but a single division's annual total
  is well-behaved; and after honest multiplicity correction there is **no defensible
  long-term trend** in the pipeline record — a caution against reading noise as climate.
- **Practical vs statistical significance:** seasonality and regional effects are both
  statistically overwhelming and practically decisive; the (null) trend results are
  statistically null and practically small — an honest combination.
- **Limitations:** pipeline layer is generated (IMD-calibrated) — tail behaviour and
  trend strength must be re-validated on the assembled raw record; record ends 2015;
  division series are cross-correlated.

---

## 7. Next Step (Review 3)

Move to `review_3/final_report.md` and compile the final report from this analysis.
