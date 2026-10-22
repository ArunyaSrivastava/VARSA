# Review 2 — Dataset / System Audit

**Stage:** Review 2 (70% of work, 20 marks)

---

## 1. Audit Scope

Run the full audit over every data source used. Document:

- Schema: columns, types, units
- Quality: duplicates, missingness, outliers
- Summary statistics: counts, min/max/mean/median/SD
- Anomalies: unexpected values, impossible entries, imbalances

---

## 2. Data Sources Audited

| Source | Rows | Columns | Duplicate rows | Missing cells | Key findings |
|---|---|---|---|---|---|
| (e.g. Spotify dataset) | (114k) | (20) | (24k, 21.3%) | (by column) | (summary) |
| (e.g. TidyTuesday Spotify) | (32.8k) | (23) | (4.5k, 13.6%) | (by column) | (summary) |
| | | | | | |

Add rows for each source.

---

## 3. Duplicate / Independence Check

- Report duplicate count and % for each source
- State whether independence is violated and what is done about it (e.g. dedupe, note as limitation)
- (See GitHub-repo example: 21.3% / 13.6% duplicates — independence violated, handled in analysis)

---

## 4. Missingness Analysis

- Per-column missing counts and %
- If > 20% missing, document decision (drop, impute, treat as separate category)
- Any systematic missingness (e.g. missing values correlate with time or artist)?

---

## 5. Summary Statistics

| Column | Non-null | Missing | Mean | Median | Std | Min | Max |
|---|---|---|---|---|---|---|---|
| (target) | | | | | | | |
| (feature) | | | | | | | |

Add rows for key columns.

---

## 6. Reproducible Audit Script

All audit steps must be runnable:

```bash
python scripts/audit_datasets.py | tee research/_audit_raw.txt
```

(Fill in the actual command from your project.)

---

## 7. Key Findings

- What did the audit reveal that could affect the analysis?
- Any limits on the conclusions you can draw?
- Any sources that must be excluded or handled carefully?

---

## 8. Next Step (Review 2 Part 2)

Move to `statistical_analysis.md` and `feasibility_report.md`.
