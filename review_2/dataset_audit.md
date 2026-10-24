# Review 2 — Dataset / System Audit

**Stage:** Review 2 (70% of work, 20 marks)

---

## 1. Audit Scope

Full audit over both data sources used by the project: schema (columns, types, units),
quality (duplicates, missingness, outliers), summary statistics, and anomalies.
Re-run and extended by `scripts/final_analysis.py` (section A) in Review 3.

---

## 2. Data Sources Audited

| Source | Rows | Columns | Duplicate rows | Missing cells | Key findings |
|---|---|---|---|---|---|
| IMD subdivision rainfall (reference layer, data.gov.in / Kaggle mirror) | 4,116 | 19 | 0 | 26 rows without annual totals; scattered monthly gaps | Coverage uneven: Arunachal Pradesh starts 1916; some island series shorter; aggregated monthly data only |
| Pipeline layer `data/raw/india_rainfall.csv` | 20,700 | 4 | 0 | 0 | Complete 36 × 115 × 5 grid; 230 slightly negative DJF values (1.11%, Madhya Bharat & Uttarakhand, −36 to −15 mm) — sampling artefact in two divisions, flagged and excluded from winter means; monsoon/annual series unaffected |

---

## 3. Duplicate / Independence Check

- Duplicate rows: **0** in both sources.
- Independence: division-year rows are unique, but **divisions are cross-correlated**
  (64.9% of the 630 division pairs correlate significantly at 5% on the pipeline layer;
  78.6% on the reference layer). Handled as an explicit limitation — never as 36
  independent samples (see Review 3, §5.5).

---

## 4. Missingness Analysis

- Reference layer: 26 of 4,116 rows lack annual totals; a few monthly cells missing.
  No column exceeds 20% missing; no imputation performed (rows retained for the
  analyses whose columns are present).
- Pipeline layer: zero missing — the seeded generator produces a complete grid by
  construction.
- Systematic missingness: none detected in either layer (missingness does not correlate
  with time or region beyond the documented late-start series).

---

## 5. Summary Statistics

Pipeline layer, national annual series (mean of 36 divisions), mm:

| Series | Non-null | Mean | Median | Std | Min | Max |
|---|---|---|---|---|---|---|
| National annual mean | 115 | 1,216.9 | 1,220.3 | 148.2 | 949.9 (1954) | 1,488.8 (1935) |

Per-division table (mean, CV, percentiles, drought frequencies, trend stats for all 36
divisions): `review_3/division_statistics.csv`.

---

## 6. Reproducible Audit Script

```bash
python scripts/audit_datasets.py            # schema + quality scan (both sources)
python scripts/final_analysis.py            # full audit + tests (Review 3 pipeline)
# raw logs: research/_audit_raw.txt, research/_final_analysis_raw.txt
```

---

## 7. Key Findings

- The pipeline grid is complete and clean except the flagged negative winter values —
  a documented artefact, not silent corruption.
- The reference (raw IMD) layer has minor gaps and starts-late series; none block the
  planned analyses.
- Aggregation limits: subdivision + monthly resolution cannot address daily extremes or
  district-level risk — scope excludes them.
- The data ends in **2015**; post-2015 monsoon years (including the anomalous 2019–2023
  period) are absent — the single most important data limitation (see feasibility report).

---

## 8. Next Step (Review 2 Part 2)

Move to `statistical_analysis.md` and `feasibility_report.md`.
