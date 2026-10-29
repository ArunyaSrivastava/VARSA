# DESIGN.md — VARSA "The Survey Sheet"

The visual world of the static explorer (`site/`), recorded from the build.
Direction: Survey of India two-colour lithographed topographic sheets
(seed:52f2ecd5b0cac593, mode: operate). Product truth: `PRODUCT.md`.
Surface contract: `.impeccable/surface-brief-site.md`.

## Tokens

### Colour — two-colour lithography + data inks
| Token | Value | Role |
|---|---|---|
| `--paper` | `#FAF9F5` | page ground: stark, cool plate paper |
| `--paper-2` | `#F1EFE7` | plate interiors |
| `--ink` | `#1C1917` | all linework and primary text |
| `--ink-2` | `#4A443C` | secondary text (tinted from the ink, never grey) |
| `--salmon` | `#C0532E` | the publication colour: fills, strokes, accents |
| `--salmon-ink` | `#9C3D1B` | salmon for *text* on paper (AA-safe) |
| `--survey` | `#2E5E6E` | cartographic blue (pipeline-year bars) |
| `--hairline` / `--hairline-soft` | `rgba(28,25,23,.34/.14)` | rules and the graticule rail |
| `--dep-*` | `#1d4ed8 #22c55e #eab308 #f97316 #dc2626 #8B857A` | departure semantics — data only, never decoration |

### Type (all self-hosted, `site/assets/fonts/`)
| Face | Use |
|---|---|
| Bricolage Grotesque 600–800 | display: wordmark, h1/h2, ledger values |
| Public Sans 400/600/700 | body, controls, tables |
| Spline Sans Mono 400/600 | every figure, stamp, scale-note, year readout (tabular numerals) |

Scale: h1 clamp(30–44px)/-0.025em · h2 clamp(20–27px) · body 15px ·
secondary 13.5px · captions 12.5px · functional floor 11px. Body measure ≤74ch
(caps applied in px).

### Structure
- The **graticule rail** (three vertical hairlines) is the signature system:
  every section registers to it.
- Sections are separated by 1.5px ink rules — no cards, no nested boxes.
- Plates (data figures) are 1.5px-bordered sheets on `--paper-2` with an
  uppercase plate-head and a mono scale note.
- The cartouche (bordered title block) carries the live reading; its bottom
  row is the only place data sits inside the title.
- Controls are standard web widgets restyled to 2px radii, 1.5px ink borders.
- One authored motion: Plate I bars rise once on load (exponential ease-out,
  disabled under `prefers-reduced-motion`). Everything else is instant.

### Non-negotiables
- Departure colours only ever encode data.
- Provenance is visible: observed/pipeline/provisional/gated are named or
  stamped wherever figures render.
- No gradient text, no eyebrow kickers, no side-stripe borders, no emoji
  icons — drawn SVG strokes only.
