# Review 2 — Feasibility Report

**Stage:** Review 2 (70% of work, 20 marks)

---

## 1. Feasibility Verdict

| Criterion | Status |
|---|---|
| Data available & sufficient? | Yes — complete pipeline grid + reference IMD layer |
| Methods appropriate & reproducible? | Yes — one command, assumption-checked |
| Time to deliver? | Yes |
| Risks identified? | data provenance (generated pipeline layer); 2015 ceiling; cross-division dependence |
| Overall verdict | **Feasible — continue with one adjustment (data replacement)** |

---

## 2. What the Analysis Shows

- The data supports the research questions confidently wherever effects are structural:
  monsoon concentration (~74% everywhere), regional dominance (η² = 0.86), skewed pooled
  distributions, and strongly local drought exposure.
- The trend question is answerable but the answer (on the pipeline layer) is *no
  detectable trend after BH correction* — a valid, reportable result, not a failure.
- Concerns carried forward: the pipeline layer is IMD-calibrated but generated, so
  tail-dependent quantities (return levels, exact trend counts) need re-validation on
  the assembled raw record; the record ends in 2015.

---

## 3. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Generated pipeline layer diverges from raw IMD in tails/trends | Medium | High | two-layer comparison in every report; replace layer with assembled IMD / ERA5 / CHIRPS and re-run the same pipeline |
| Data ends 2015 — recent extremes missing | High | Medium | acquire post-2015 IMD or ERA5 (2025); re-test trends on the longer record |
| Cross-division dependence inflates apparent evidence | High | Medium | report dependence (64.9% of pairs); rely on large effects, not borderline p-values |
| Fragmented official releases block a clean raw dataset | High | Medium | institutional IMD request (2–4 weeks) or reanalysis products as fallback |
| Method mismatch (equal-variance ANOVA on unequal variances) | Low | High | already mitigated: Levene → Welch ANOVA |

---

## 4. What Works / What Doesn't

| Works | Doesn't Work |
|---|---|
| Topic is rich and every syllabus method applies naturally | No daily/sub-daily extremes (aggregated data) |
| Pipeline is fully reproducible; dashboard makes findings explorable | Trend claims do not survive correction (on the pipeline layer) |
| Large, robust effects (seasonality, region, drought locality) | Post-2015 decade absent; district resolution out of reach with subdivision data |

---

## 5. Recommendation

- **Continue as planned — conditional on data replacement.** The methods and pipeline are
  sound; the single highest-value adjustment is swapping the pipeline layer for the
  assembled raw IMD record (or ERA5/CHIRPS) and re-running `scripts/final_analysis.py`
  unchanged.
- Review 3 should therefore focus on: (1) the final compiled report with figures;
  (2) the two-layer consistency check; (3) a data-acquisition plan (IMD portal request,
  ERA5, CHIRPS) with verification steps.

---

## 6. Next Step (Review 3)

Move to `review_3/final_report.md` and compile the final report from the scope, audit,
analysis, and this feasibility report.
