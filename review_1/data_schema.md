# Review 1 — Data Schema & Sources

**Stage:** Review 1 (30% of work, 10 marks)

---

## 1. Source(s) & Format

| Source | Format | Rows / Volume | Coverage | Notes |
|---|---|---|---|---|
| (e.g. Kaggle Spotify Tracks) | (CSV, JSON, .pkl) | (114k × 20) | (114 genres) | (download script available) |
| | | | | |

Add rows for each data source used.

---

## 2. Key Fields / Columns

Describe the important fields/attributes. Group them:

| Data type | Fields | Description |
|---|---|---|
| Identifiers | (e.g. track_id, artist_id) | Unique keys |
| Numeric | (e.g. popularity, duration_ms, energy) | Target or features |
| Categorical | (e.g. genre, explicit) | Groupings |
| Temporal | (e.g. release_date) | Time-series / cohort |

Add rows as needed.

---

## 3. Initial Quality Snapshot

| Check | Result |
|---|---|
| Rows / columns | (count) |
| Duplicate rows | (count / % ) |
| Missing values per column | (top 3 columns) |
| Data types | (ok / issues) |
| Target variable | (name + distribution description) |

> The full audit is done in Review 2 (`review_2/dataset_audit.md`). This is a high-level view for Review 1.

---

## 4. First Figures Planned

List 3–7 figures with a one-line description of what each shows:

1. **(Figure 1)** — [e.g. popularity distribution histogram]
2. **(Figure 2)** — [e.g. correlation heatmap of audio features]
3. **(Figure 3)** — [e.g. boxplot of popularity by genre]
4. **(Figure 4)** — [e.g. scatter: energy vs valence colored by popularity]
5. **(Figure 5)** — [e.g. boxplot of release-year distribution by popularity tertile]
6. **(Figure 6)** — [e.g. line chart: average popularity over years]
7. **(Figure 7)** — [e.g. duplicate-rate impact on analysis]

---

## 5. Data Acquisition Plan

- Where to download / fetch data:
- Is there a reproducible script? (`scripts/fetch_data.sh` or similar)
- Any license / registration requirements?

---

## 6. Notes / Assumptions

- Any caveats about the data (sampling bias, missing classes, etc.)?
- Assumptions about the target variable or feature definitions?

---

## 7. Next Step (Review 2)

Move to Review 2: run the full audit, apply statistical methods, and document results in `review_2/dataset_audit.md` and `review_2/statistical_analysis.md`.
