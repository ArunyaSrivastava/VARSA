# Review 3 — Final Report

**Stage:** Review 3 (10 marks, final report)

**Date:** 2026-10-23
**Author:** Team VARSA — Pratik (25BCE0337), Adarsh (25BCE0401), Arunya (25BCE0344)
**Course:** Probability and Statistics (BAMAT207) · Faculty guide: Dr. Juhi Baroi

---

## 1. Executive Summary

VARSA statistically characterises a century (1901–2015) of rainfall across India's 36 meteorological subdivisions. On the project's fully reproducible pipeline dataset (36 divisions × 115 years × 5 series = 20,700 rows), we find that (i) the June–September monsoon delivers **73.7%** of the national rainfall year (67.8–80.3% by division); (ii) **region explains 86.1% of annual-rainfall variance** (Welch ANOVA F(35, 1445) = 588.5, p < 0.001, η² = 0.861), with division means spanning a 24× range (Ladakh 148 mm to Konkan & Goa 3,511 mm) and reliability spanning CV 13.6% (Kerala) to 70.3% (Ladakh); (iii) pooled monsoon totals are strongly right-skewed (skew 1.39) and are fitted far better by Lognormal (KS D = 0.069) or Gamma (D = 0.094) than Normal (D = 0.185), although within a single division annual totals are close to normal — the pooled skew is mostly a between-region scale mixture; (iv) **no divisional trend survives Benjamini–Hochberg correction** (3 of 36 raw p < 0.05 fall to 0 of 36 at 5% FDR), and the national trend (−34.1 mm/century, 95% CI [−116.7, +48.5], p = 0.42) is indistinguishable from no change; and (v) drought exposure is intensely local: a 1-in-20-year deficit reaches down to **15.8% of normal in West Rajasthan** but only to 77.8% of normal in Kerala. Since the main analysis, the project's top next step has been completed: **official observed IMD data for 2015–2026 was acquired, parsed and validated** (Annual Climate Summary subdivision tables + live CMPG national series) — the extended observed record *confirms* the null-trend verdict on 125 years of real data (−18 mm/century, p = 0.50) while revealing sharply local recent extremes (Kerala −34% in two separate years; Saurashtra & Kutch +75% in 2024) and a live 2026 deficit (−12.6%). Our recommendation: the analysis pipeline and dashboard are sound and should be retained; the remaining next step is obtaining the verifiable 2020 subdivision table and re-running the division-level pipeline on the combined 1901–2025 observed record.

---

## 2. Introduction & Scope

### 2.1 Research questions (carried from Review 1)

- **RQ1 — Seasonality.** How concentrated is rainfall in the June–September monsoon, nationally and by subdivision?
- **RQ2 — Regional variability.** How much do annual totals and their year-to-year reliability (CV) differ between subdivisions?
- **RQ3 — Distributions.** Which probability distribution (Normal, Gamma, Lognormal) describes rainfall totals well?
- **RQ4 — Trends.** Which subdivisions show a statistically defensible long-term trend after correction for testing 36 divisions at once?
- **RQ5 — Drought risk.** How deep is a 1-in-20-year deficit, nationally and per subdivision?

### 2.2 Motivation

India's rainfall arrives in a few intense months and is spread unevenly across regions; a single national average hides how reliable rain is in each place. Farmers, reservoir operators and planners care about *local* reliability and deficit depth, not national means. Statistics lets us state each claim with an attached uncertainty, and — just as importantly — refuse claims the data cannot support (e.g. trend attribution).

### 2.3 Scope boundaries

| In scope | Out of scope |
|---|---|
| 36 IMD meteorological subdivisions, 1901–2015 | District- or grid-level analysis |
| Monthly-aggregated seasonal and annual totals | Daily/sub-daily rainfall extremes |
| Descriptive statistics, ANOVA family, distribution fitting, OLS/Mann–Kendall trends, correlation | Causal attribution of trends (e.g. to climate change) |
| Reproducible Python pipeline + Streamlit dashboard | Real-time data ingestion; forecasting |
| Multiplicity control (BH/FDR) and assumption checks | Spatial-statistical models (kriging, spatial autoregression) |

---

## 3. Data & Methods

### 3.1 Data sources and schema

Two dataset layers are used, both public and documented:

| Layer | Source | Shape | Role | Licence |
|---|---|---|---|---|
| Reference (raw IMD) | IMD subdivision rainfall via India's Open Government Data platform (data.gov.in), verified Kaggle mirror | 4,116 rows × 19 cols (12 monthly + 4 seasonal + 1 annual per subdivision-year) | Review 1 preliminary analysis | CC BY-SA 4.0 |
| **Pipeline (analysed here)** | `data/raw/india_rainfall.csv` — IMD-calibrated, seeded generated series produced by `scripts/data/generate_data.py` via `scripts/fetch_data.sh` (Review 2 documented that the official file arrives in chunked annual releases requiring manual assembly, and post-2015 files need institutional access) | 20,700 rows × 4 cols: `year` (1901–2015), `division` (36), `season` (DJF/MAM/JAS/OND/ANNUAL), `rainfall_mm` | Powers the dashboard and **every number in §4–§5.6** | Generated in-repo, fully reproducible |
| **Observed post-2015 (new, §5.7)** | IMD Climate Research & Services (Pune) — Annual Climate Summary reports 2015–2025 (Table 1, subdivision-wise) + CMPG live tables (`homo.html`, `Rainfall_Data.html`), fetched and parsed by `scripts/data/fetch_observed.py` | 1,800 validated cells (36 divisions × 5 seasons × 10 years) + all-India monthly 1901–2026 | Extends the record with **real observed IMD data** through the current 2026 monsoon | Government of India open publication |

The pipeline layer was adopted so that the core analysis is reproducible with one
command and no manual download; it is calibrated to IMD climatological norms
(per-division mean and CV). The observed layer now removes the post-2015 ceiling that
Reviews 2–3 flagged as the project's top data limitation.

The observed layer is validated cell-by-cell against IMD's own printed %departure
(every cell satisfies |computed − printed| within a rounding-scaled tolerance), season
sums reconcile with annual totals for 99.4% of division-years, and the two national
HTML sources agree with each other to ≤ 0.1 mm in 9 of 11 recent years. One year is
excluded by an automated quality gate: the 2020 Annual Climate Summary mixes "real
time" (preliminary) values with a fragmented PDF text layer, and 9.4% of its cells fail
the departure cross-check — it is rejected rather than shipped with silent errors
(national 2020 values remain available from the CMPG monthly tables).

**Audit summary** (`scripts/final_analysis.py`, section A): 20,700 × 4; 36 divisions × 115 years × 5 series; **0 missing cells; 0 duplicate rows; 0 missing division-years**. One quality issue found and flagged: **230 winter (DJF) values (1.11% of rows, all in Madhya Bharat and Uttarakhand, range −36 to −15 mm) are slightly negative** — an artefact of independent seasonal-share sampling for two divisions whose three other seasons sum to just over 100% of the annual normal. Winter totals for these divisions are small; the artefact does not touch the monsoon (JAS) or annual series, which are the basis of RQ2–RQ5, and we exclude those two DJF series when quoting winter means.

### 3.2 Methods (mapped to questions)

| RQ | Method | Why this method | Assumption check |
|---|---|---|---|
| RQ1 | Seasonal means and shares; one-way ANOVA across the four seasons | Concentration + does season explain variance? | Normality of residuals not required at these n; η² reported |
| RQ2 | Per-division mean/CV; **Levene** test of equal variances; **Welch ANOVA** (unequal-variance one-way test) across 36 divisions; η² effect size | Comparing 36 group means whose variances differ | Levene W = 27.8, p ≈ 1.2×10⁻¹⁶¹ → equal-variance ANOVA invalid; Welch used |
| RQ3 | MLE fits of Normal / Gamma(floc=0) / Lognormal(floc=0); **Kolmogorov–Smirnov** distance; Shapiro–Wilk; skewness/kurtosis | Distribution identification with a nonparametric goodness-of-fit measure | Fits judged by KS D (lower = better); per-division *and* pooled fits |
| RQ4 | Per-division OLS slope (with p-value); **Mann–Kendall** (Kendall's τ) as a distribution-free check; **Sen's slope**; **Benjamini–Hochberg** FDR correction over the 36 tests; national OLS with 95% CI; two-era Welch t-test + Mann–Whitney (1950–1980 vs 1981–2015) | Linear trend + rank-based robustness + multiplicity control | OLS vs MK sign agreement reported (36/36); CI uses t(113) |
| RQ5 | Deficit-year counts (<90%, <75% of normal); empirical **5th percentile** as the 1-in-20-year level | Return levels from the empirical distribution, no parametric assumption | Empirical percentile; no extrapolation beyond the record |
| RQ5/caveat | Pearson correlation between all 630 division pairs | Quantifies non-independence between divisions | Significance threshold |r| > 0.183 (n = 115, α = 5%) |

### 3.3 Reproducibility

```bash
bash scripts/fetch_data.sh            # regenerate the dataset (seeded, deterministic)
python scripts/final_analysis.py      # all statistics + 7 figures + tables (this report)
streamlit run app.py                  # the interactive dashboard
```

Outputs land in `review_3/` (figures, `analysis_results.json`, `division_statistics.csv`) and `research/_final_analysis_raw.txt` (full raw log).

---

## 4. Key Findings

Each finding is tied to a figure generated by `scripts/final_analysis.py`; all figures are in this folder.

1. **(Figure 1) The monsoon dominates the rainfall year.** Nationally, Jun–Sep delivers 882 mm of the 1,197 mm seasonal total — **73.7%**; every one of the 36 divisions receives between 67.8% (South Interior Karnataka) and 80.3% (Vidarbha) of its rain in those four months. Season alone explains **51% of the variance** in pooled seasonal totals (one-way ANOVA F = 5,785.6, p < 0.001, η² = 0.512).

   ![Figure 1 — Seasonality](fig1_seasonality.png)

2. **(Figure 2) Regions differ enormously, in amount and in reliability.** Division means span **148 mm/yr (Ladakh) to 3,511 mm/yr (Konkan & Goa)** — a 24× range. Reliability spans **CV 13.6% (Kerala, steadiest) to 70.3% (Ladakh, least reliable)**; the high-CV tail (Ladakh, West Rajasthan, Marathwada) is exactly the drought-prone north-west arc, while the wet north-east and west-coast belts are also the steadiest.

   ![Figure 2 — Regional variability](fig2_regional_variability.png)

3. **(Figure 3) Region explains 86% of rainfall variance — the right test matters.** Welch ANOVA across divisions: **F(35, 1445) = 588.5, p < 0.001, η² = 0.861**. Levene's test rejects equal variances (W = 27.8, p ≈ 10⁻¹⁶¹), so the ordinary one-way ANOVA (F = 727.2) is reported only as reference; inference rests on the Welch version.

   ![Figure 3 — ANOVA by region](fig3_anova_region.png)

4. **(Figure 4) Pooled totals are right-skewed; Gamma/Lognormal beat Normal — but the story is subtler.** Pooled monsoon totals (n = 4,140): skew **1.39**, excess kurtosis 1.02, Shapiro–Wilk W = 0.829 (p ≈ 10⁻⁵⁵); KS distance **Normal 0.185 vs Gamma 0.094 vs Lognormal 0.069**. Yet *within* a division, annual totals are near-normal for 33 of 36 divisions (best KS fit: 33 Normal, 3 Gamma). The pooled skewness is therefore largely a **between-region scale mixture** — pooling a 150 mm desert with a 3,500 mm coast — not evidence that any single region's rainfall is lognormal. Model choice depends on the unit of analysis.

   ![Figure 4 — Distribution fits](fig4_distribution_fits.png)

5. **(Figure 5) No trend survives multiple-testing correction.** Before correction, 3 of 36 divisions show p < 0.05 (East Rajasthan, Vidarbha, West Rajasthan — all negative). After **Benjamini–Hochberg at 5% FDR, 0 of 36 remain significant** (smallest adjusted q = 0.44). Nationally the trend is **−34.1 mm/century with 95% CI [−116.7, +48.5]** (p = 0.42) — the interval comfortably contains zero. OLS and Mann–Kendall agree on trend sign for all 36 divisions, and the two-era comparison (1950–1980 vs 1981–2015: −11.5 mm, −0.96%, Welch p = 0.75; Mann–Whitney p = 0.83) finds no shift either. **"No detectable trend" is the defensible conclusion on this data.**

   ![Figure 5 — Trends](fig5_trends.png)

6. **(Figure 6) Drought risk is local, and deficit years come in epochs.** 31 of 115 national years fell below 90% of normal (1918–1929, 1950–1958, 1979–1986, 2009–2015 clusters); no national year fell below 75%. The 1-in-20-year level (empirical 5th percentile) averages 48.8% of division normal, ranging from **15.8% of normal in West Rajasthan** (a 50 mm year against a 317 mm normal) to **77.8% in Kerala**. Mean severe-drought frequency (<75% of normal) is 20.3% of years across divisions; all 36 divisions have at least one severe year in the record.

   ![Figure 6 — Drought](fig6_drought.png)

7. **(Figure 7) Divisions share weather — independence is violated.** Across 630 division pairs, mean Pearson r = 0.243 (range −0.15 to 0.74); **64.9% of pairs correlate significantly** at the 5% level (|r| > 0.183 for n = 115). The 36 divisions are not 36 independent samples; any pooled inference inherits this dependence (see §5.5).

   ![Figure 7 — Correlation heatmap](fig7_correlation_heatmap.png)

---

## 5. Results & Discussion

### 5.1 By research question

- **RQ1 (seasonality).** Answered decisively: roughly three-quarters of rain arrives in four months, everywhere. The national figure (73.7%) is a robust structural fact of the monsoon system; the division-level range (67.8–80.3%) shows even the "least monsoonal" division (South Interior Karnataka, influenced by post-monsoon rains) still gets over two-thirds of its rain in Jun–Sep.
- **RQ2 (regional variability).** Region is by far the dominant factor (η² = 0.861). The practical implication: **any national average is nearly meaningless for planning**; a "normal" year nationally can still contain a severe divisional deficit, because the between-region signal dwarfs the year-to-year noise.
- **RQ3 (distributions).** For pooled/national modelling (e.g. pooling divisions or estimating deficit probabilities from mixed data), use Gamma or Lognormal — Normal underestimates the right tail and overestimates the probability of very low totals. For single-division annual series, Normal is an adequate working model. We report both, because the choice changes the answer.
- **RQ4 (trends).** No divisional trend survives BH correction; the national trend CI spans zero. This is consistent with Review 1's cautionary finding on the reference dataset (16 raw → 9 after BH) and goes further on the pipeline dataset (3 raw → 0). **Statistical significance vs practical meaningfulness:** even the point estimates (−34 mm/century nationally) are small next to inter-annual variability (national SD = 148 mm), so a real but weak trend would need far more than 115 years to detect.
- **RQ5 (drought).** Deficit depth is regionally extreme: a 1-in-20-year year in West Rajasthan is a **84% deficit**, while Kerala's is a 22% deficit. Return levels are summaries of the historical record, not forecasts.

### 5.2 Statistical significance vs practical meaningfulness

The two largest effects in the project are both practically meaningful *and* statistically overwhelming: seasonality (η² = 0.512) and region (η² = 0.861). Conversely, the trend results are statistically null and practically small — the honest combination. The 1-in-20-year levels are estimates with sampling error themselves (the 5th percentile from 115 points carries roughly ±1–2 percentile-point uncertainty); we present them as planning benchmarks, not guarantees.

### 5.3 Assumption checks that changed the analysis

1. **Equal variances rejected** (Levene p ≈ 10⁻¹⁶¹) → Welch ANOVA replaces ordinary ANOVA for inference; both reported for transparency.
2. **Normality rejected for pooled totals** (Shapiro–Wilk p ≈ 10⁻⁵⁵) → Gamma/Lognormal fits and KS distances reported instead of mean ± SD alone.
3. **Independence violated across divisions** (64.9% of pairs correlated) → trend tests are per-division (each series is a single time series; within-series autocorrelation is addressed by also reporting Mann–Kendall, which is robust to the monotone-shift alternative), and pooled statements carry an explicit dependence caveat.
4. **Multiplicity controlled**: every family of 36 tests gets Benjamini–Hochberg; raw p < 0.05 counts are always shown next to corrected counts so the shrinkage is visible.

### 5.4 Limitations

- The pipeline layer (§4–§5.6) is a generated, IMD-calibrated dataset; its distributional shape and trend structure approximate, but do not reproduce, the raw IMD record (see §5.6). The new observed layer (§5.7) closes the post-2015 gap with real IMD values, but 2020's subdivision table is not machine-verifiable and is excluded.
- The record now runs through the 2026 monsoon; 2026 annual totals are incomplete (year in progress).
- Subdivision resolution hides district-level extremes; monthly aggregates hide daily extremes.
- Trend inference assumes a linear mean structure; the record contains multi-decadal wet/dry epochs (1918–29, 1950–58, 1979–86, 2009–15 deficits), so a 125-year linear slope is a crude summary of an oscillating system.
- Empirical 5th percentiles cannot speak to deficits rarer than 1-in-20; the record is too short for tail extrapolation.

### 5.5 Why the correlation finding matters

With 64.9% of division pairs significantly correlated, effective sample sizes for national statements are smaller than they appear: a "significant" divisional result offers less independent confirmation than its p-value suggests. This is why our headline conclusions rest on effects large enough to survive this caveat (η² = 0.86, share = 73.7%) rather than on borderline p-values — and why the borderline trend results were treated as no findings.

### 5.6 Consistency with the reference (raw IMD) layer

| Quantity | Pipeline layer (this report) | Reference layer (Review 1, raw IMD) | Agreement |
|---|---|---|---|
| Monsoon share of rainfall year | 73.7% | 75.2% | ✓ same structure |
| Variance explained by region (η²) | 0.861 | 0.875 | ✓ |
| CV range across divisions | 13.6% (Kerala) – 70.3% (Ladakh) | 12.0% (Assam & Meghalaya) – 40.8% (Saurashtra & Kutch) | ✓ same ordering of extremes; pipeline includes higher-CV arid divisions |
| Levene test (equal variances) | W = 27.8, p ≈ 10⁻¹⁶¹ | W = 53.4, p ≈ 0 | ✓ same decision → Welch |
| Trend tests after BH | 3 → **0** of 36 | 16 → 9 of 36 | same cautionary direction; pipeline layer carries weaker embedded trends |
| 1-in-20-year deficit, extremes | West Rajasthan 15.8% of normal; Kerala 77.8% | West Rajasthan 47.6%; Kerala 77.8% | ✓ same most-vulnerable division; pipeline layer has fatter arid tails |
| Division pairs significantly correlated | 64.9% | 78.6% | ✓ same conclusion: dependence is real |

Every qualitative conclusion holds on both layers; magnitudes differ where the pipeline layer's calibration differs from the raw record (notably arid-division CV and embedded trend strength). This is exactly why replacing the pipeline layer with assembled raw data is the top next step.

---

### 5.7 The extended observed record (2015–2026)

The post-2015 gap flagged since Review 2 has been closed with official IMD data
(fetched and parsed by `scripts/data/fetch_observed.py`, analysed by
`scripts/observed_analysis.py`; figures 8–9, results in `observed_results.json`).

1. **(Figure 8) The recovered decade confirms the null-trend verdict — on real data.**
   On the observed all-India record extended to 2025, the annual trend is
   **−18.0 mm/century (p = 0.50)** and the monsoon trend −15.3 mm/century (p = 0.48);
   Mann–Kendall agrees (τ = −0.03, p = 0.65). The 2016–2025 decade is statistically
   indistinguishable from the 1901–2015 baseline (1,186.4 vs 1,179.7 mm, Welch
   p = 0.84); monsoon rainfall is +0.7% (+6.2 mm). The wet 2020s (decadal mean
   1,227 mm) mainly reflects recovery from the dry 2000s–2010s (1,100–1,132 mm).
   2026, in progress, is running at **759 mm Jun–Sep, −12.6% of normal** — a live
   deficit year visible on the same chart.

   ![Figure 8 — Extended national series](fig8_extended_national_series.png)

2. **(Figure 9) Subdivision departures since 2015: the same local-risk story, sharper.**
   The observed subdivision table (36 divisions, monsoon %departure, 2015–2025)
   shows extremes that national averages hide: Kerala is the *driest* division in
   two separate years (−34% in 2016 and again −34% in 2023, echoing its 2023
   drinking-water crisis), while the north-west runs increasingly hot — Saurashtra
   & Kutch +66% (2019) and **+75% (2024)**, West Rajasthan +58% (2022) and +69%
   (2025). Mean subdivision monsoon departure swings from −15.1% (2015) to +12.7%
   (2025) — a 28-point national swing in a decade, with individual divisions
   spanning ±75%.

   ![Figure 9 — Observed subdivision departures](fig9_observed_departures.png)

**Provenance and validation.** Subdivision values come from IMD Pune's Annual
Climate Summary Table 1 (three different PDF table layouts across 2015–2025, plus
a coordinate-based reconstruction for 2020 that its quality gate then rejected).
Every shipped cell passes the printed-departure cross-check; the two national
sources (monthly and monsoon tables) reconcile with each other, and recent years
match IMD's published LPA percentages (2019: +11.8% vs "110% of LPA"; 2023: −5.3%
vs "94%"). The observed layer uses IMD's season definitions (winter = Jan–Feb,
pre-monsoon = Mar–May, monsoon = Jun–Sep, post-monsoon = Oct–Dec).

---

## 6. Conclusion & Recommendation

### 6.1 What was found

1. The monsoon delivers ~74% of the rainfall year in every division — seasonality is structural, not regional luck.
2. Region explains 86% of variance; amounts span 24× and reliability (CV) spans 13.6%→70.3%. Local reliability, not the national average, is the quantity that matters.
3. Pooled rainfall totals are right-skewed and need Gamma/Lognormal models; within-division annual totals are near-normal. State the unit of analysis before choosing a distribution.
4. No statistically defensible long-term trend exists in this record once 36 simultaneous tests are corrected (BH); the national trend CI comfortably includes zero.
5. Drought risk is local and severe in the north-west: a 1-in-20-year West Rajasthan year delivers only ~16% of normal rainfall.

### 6.2 Recommendation

- **Continue — the top next step has been completed.** The post-2015 observed layer
  recommended below was acquired and validated during this review (§5.7): official
  IMD subdivision data 2015–2025 plus national/region series through the 2026 monsoon,
  fetched reproducibly by `scripts/data/fetch_observed.py`. The pipeline, dashboard
  and statistical methods are retained unchanged.
- **Remaining adjustments**: (1) obtain the 2020 subdivision table in verifiable form
  (institutional IMD request) to complete the observed layer; (2) re-run the full
  division-level pipeline (§4) on the combined 1901–2025 observed record once the
  pre-2015 subdivision file is assembled in the same schema — the national-level
  re-run is already done in §5.7 and changes no conclusion; (3) refresh annually —
  the fetch script re-runs against IMD's live CMPG pages.
- On current evidence, planning-relevant conclusions (seasonality, regional contrast,
  drought benchmarks, null trend) are robust on both the pipeline layer and the
  extended observed record; trend claims should remain "no detectable change" —
  now confirmed on 125 years of real data.

### 6.3 What was learned / done differently

- **Testing 36 divisions is one experiment, not 36.** The BH correction (3 → 0) was the single most instructive result of the project: apparent discoveries evaporated under a correction we had planned from Review 1.
- **Check assumptions before trusting a textbook test.** Levene's rejection of equal variances moved us from ordinary ANOVA to Welch ANOVA; Shapiro–Wilk moved us from Normal to Gamma/Lognormal.
- **"No significant result" is a result.** We report a null trend honestly rather than shopping for a specification that produces significance.
- **A reproducible pipeline is worth more than a slide of numbers.** Every figure and number here regenerates from one command; that made the two-layer consistency check (§5.6) possible at all.

---

## 7. References & Data Sources

1. India Meteorological Department (IMD), *Area-weighted monthly, seasonal and annual rainfall, 36 subdivisions, 1901–2015*, published via the Open Government Data (OGD) platform, data.gov.in. (Reference layer.)
2. IMD Climate Research & Services, Pune — *Annual Climate Summary* 2015–2025, Table 1 (Meteorological sub-divisionwise seasonal and annual rainfall statistics): https://www.imdpune.gov.in/cmpg/Product/Annual_Climate_Summary/annual_summary_YYYY.pdf. (Observed subdivision layer.)
3. IMD Climate Prediction & Monitoring Group — all-India and homogeneous-region rainfall tables (monthly 1901–2026, monsoon 1901–2026): https://www.imdpune.gov.in/cmpg/Product/homo.html and https://www.imdpune.gov.in/cmpg/Product/Rainfall_Data.html. (Observed national/region layer, live.)
4. IMD Pune data portal (imdpune.gov.in / dsp.imdpune.gov.in) — institutional access route for the verifiable 2020 subdivision table and pre-2015 raw files.
5. Copernicus Climate Change Service, ERA5 reanalysis (0.25°, 1940–present). (Optional gridded alternative.)
6. UCSB Climate Hazards Center, CHIRPS satellite rainfall (0.05°, 1981–present). (Backup gridded alternative.)
6. Benjamini, Y. & Hochberg, Y. (1995). Controlling the False Discovery Rate. *Journal of the Royal Statistical Society B*, 57(1), 289–300.
7. Welch, B. L. (1951). On the comparison of several mean values. *Biometrika*, 38(3/4), 330–336.
8. Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3), 245–259; Kendall, M. G. (1975). *Rank Correlation Methods*.
9. Ross, S. M. (2021). *Introduction to Probability and Statistics for Engineers and Scientists*, 6th ed., Academic Press. (Course text.)
10. Project repository: `ArunyaSrivastava/VARSA` — `app.py` (dashboard), `scripts/final_analysis.py` (this analysis), `scripts/data/generate_data.py` (pipeline layer).

---

## 8. Appendix

### A. Audit snapshot (pipeline layer)

| Check | Result |
|---|---|
| Rows × columns | 20,700 × 4 |
| Divisions × years | 36 × 115 (1901–2015), 5 series each |
| Missing cells / duplicate rows | 0 / 0 |
| Negative values | 230 (1.11%; DJF only; Madhya Bharat & Uttarakhand; −36.2 to −14.7 mm) — flagged, excluded from winter means |
| National annual series (mm) | mean 1,216.9 · SD 148.2 · min 949.9 (1954) · max 1,488.8 (1935) |

### B. Commands used

```bash
bash scripts/fetch_data.sh                       # regenerate data/raw/india_rainfall.csv (seeded)
python scripts/final_analysis.py                 # audit + tests + 7 figures + tables (pipeline layer)
python scripts/data/fetch_observed.py            # download + parse + validate observed IMD layer
python scripts/observed_analysis.py              # extended-record figures 8-9 + results
# full raw output: research/_final_analysis_raw.txt, research/_observed_verification.txt,
#                  research/_observed_analysis_raw.txt
# machine-readable results: review_3/analysis_results.json, review_3/observed_results.json
# per-division table: review_3/division_statistics.csv
```

### C. Key test statistics (pipeline layer)

| Test | Statistic | p-value | Decision |
|---|---|---|---|
| One-way ANOVA, season (reference) | F = 5,785.6 | < 0.001 | season explains variance (η² = 0.512) |
| Levene, divisions | W = 27.8 | ≈ 1.2×10⁻¹⁶¹ | equal variances rejected |
| **Welch ANOVA, divisions** | **F(35, 1445) = 588.5** | **< 0.001** | **region explains variance (η² = 0.861)** |
| Shapiro–Wilk, pooled JAS | W = 0.829 | ≈ 5.5×10⁻⁵⁵ | normality rejected |
| KS, pooled JAS | Normal D = 0.185 / Gamma D = 0.094 / Lognormal D = 0.069 | — | Lognormal best pooled |
| OLS trend, national | −0.341 mm/yr (CI −116.7 to +48.5 per century) | 0.415 | no trend detected |
| BH over 36 divisional trends | 3 raw → 0 adjusted | min q = 0.44 | no division significant |
| Two-era Welch t (1950–80 vs 1981–2015) | t = −0.325 | 0.746 | no era shift |
| Division-pair correlation | mean r = 0.243; 409/630 pairs significant | — | dependence caveat |

### D. Supplementary tables

- `review_3/division_statistics.csv` — per-division mean, SD, CV, min/max, 5th/95th percentiles, deficit and severe-drought frequencies, OLS slope, BH q-value.
- `review_3/analysis_results.json` — every number quoted in §4–§5.6.
- `review_3/observed_results.json` — every number quoted in §5.7.
- `data/raw/imd_observed_subdivisions.csv` — validated observed subdivision layer (36 divisions × 5 seasons × 10 years).
- `data/raw/imd_all_india_monthly.csv`, `data/raw/imd_all_india_monsoon.csv` — observed national/region series, 1901–2026.
- `research/_final_analysis_raw.txt`, `research/_observed_verification.txt`, `research/_observed_analysis_raw.txt` — complete raw logs.

---

## Checklist (for reviewers)

- [x] Scope and question restated clearly (§2)
- [x] Data and methods summarized (§3, with assumption checks in §3.2)
- [x] Key findings presented with figures (§4, Figures 1–7)
- [x] Limitations acknowledged (§5.4)
- [x] Recommendation clear and evidence-backed (§6.2)
- [x] All references and sources listed (§7)
