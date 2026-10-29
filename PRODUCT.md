# PRODUCT.md — VARSA

## Product

**VARSA** — Variability, Anomalies and Regional Statistics of Indian Rainfall.
A statistical explorer for 125 years (1901–2026) of Indian monsoon rainfall across
India's 36 IMD meteorological subdivisions. Course project for Probability &
Statistics (BAMAT207), VIT; team: Pratik (25BCE0337), Adarsh (25BCE0401),
Arunya (25BCE0344); guide: Dr. Juhi Baroi.

## What makes it different

Every number is **provenance-tagged and validated**: a generated IMD-calibrated
pipeline layer (1901–2015) is unified with **observed IMD data** (Annual Climate
Summary subdivision tables 2015–2025, quality-gated; CMPG live national tables
through the 2026 monsoon). The 3D "Rainfall-Height Atlas" extrudes the
subcontinent into prisms — height = rainfall, colour = % departure. Headline
live fact: the **2026 monsoon is running 12.6% below normal** (759.4 mm Jun–Sep).

## Audience and scene

- **Primary:** the faculty review panel and statistics students, assessing
  whether the analysis is defensible; they read on laptops, often projected in a
  dim classroom.
- **Secondary:** anyone wanting an honest public view of Indian rainfall history
  (the static site is the public face; the Streamlit app is the full dossier).
- Job: see the monsoon's structure, regional contrast, drought depth and the
  (null) trend story at a glance, then drill into one subdivision's 125-year record.

## Confirmed facts and constraints

- Two artefacts must stay visually consistent: this static site (Vercel) and the
  Streamlit dashboard (same dark-navy data-identity family; the Streamlit app's
  theme is fixed by its existing codebase and out of scope for this surface).
- Data honesty is a brand commitment: observed vs generated vs provisional must
  stay distinguishable everywhere. 2020 is excluded by a validation gate; 2026
  subdivision values do not exist yet; the 2026 national monsoon is provisional.
- Accessibility: WCAG AA contrast on all body text (detector-enforced).
- Units: millimetres, % departure from normal. No forecasts; return periods are
  record summaries, not predictions.
- Brand commitments: the name "VARSA"; team attribution footer; the departure
  colour semantics (blue ≥+20%, green normal, amber −20–0%, orange −40–−20%,
  red ≤−40%, grey = no data) carry real data meaning and must survive re-styling.
- Stack (existing): static HTML + deck.gl + Plotly, no framework; deploy: Vercel.

## Open decisions

- None material. Design world replacement is owned by the direction round on
  each surface; product truth above is binding.
