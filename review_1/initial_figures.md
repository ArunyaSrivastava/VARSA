# Review 1 — Initial Figures Plan

**Stage:** Review 1 (30% of work, 10 marks)

---

## 1. Figure Inventory

| Figure | Description | Data Source | Status |
|---|---|---|---|
| Fig. 1 | Seasonal composition — monsoon share of the rainfall year, national and by division | pipeline layer | done (Review 3) |
| Fig. 2 | Mean annual rainfall by division, coloured by CV + CV ranking | pipeline layer | done (Review 3) |
| Fig. 3 | Annual rainfall distribution by division (boxplot, log scale) with Welch ANOVA / η² annotation | pipeline layer | done (Review 3) |
| Fig. 4 | Pooled monsoon totals with Normal / Gamma / Lognormal fits + per-division best-fit counts | pipeline layer | done (Review 3) |
| Fig. 5 | National trend with 95% CI + per-division OLS slopes flagged by BH significance | pipeline layer | done (Review 3) |
| Fig. 6 | National deficit-year bar chart + per-division 1-in-20-year levels (% of normal) | pipeline layer | done (Review 3) |
| Fig. 7 | 36 × 36 Pearson correlation heatmap of annual series | pipeline layer | done (Review 3) |

At Review 1 the figures existed as dashboard drafts; the polished, publication-ready
versions were finalised in Review 3 by `scripts/final_analysis.py` (PNG, 200 dpi).

---

## 2. Reproducible Script Mapping

| Figure | Script | Output |
|---|---|---|
| Fig. 1–7 | `scripts/final_analysis.py` | `review_3/fig1_seasonality.png` … `fig7_correlation_heatmap.png` |
| Dashboard equivalents | `app.py` (Streamlit, interactive) | browser |

Every figure regenerates from one command; no manual steps.

---

## 3. Styling & Conventions

- Consistent matplotlib style: light background, colour-blind-safe accents, grid #E2E8F0
- Labels, titles, units and legends always included; 200 dpi PNG
- Same colour semantics as the dashboard (green = monsoon/normal, amber = caution, red = deficit)
- PNG for report/dashboard; figures live directly in `review_3/`

---

## 4. Notes

- Review-1 drafts exposed two issues fixed for Review 3: threshold annotations overlapping
  bars (Fig. 6) and legend placement over the confidence band (Fig. 5) — both corrected.
- Figures that revealed data issues are flagged in the audit: negative winter values in
  two divisions (Fig. 1's winter means exclude them).
