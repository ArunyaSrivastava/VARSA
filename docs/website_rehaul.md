# VARSA Website Rehaul — Ideation & Blueprint

**Goal:** turn the existing Streamlit dashboard into a flashier, 3D-rich,
map-first experience — more 3D models, better India map visualizations, and a
cinematic feel — without breaking what already works or losing statistical honesty.

**Grounding:** this document references the current `app.py` structure (Section 1
map + style switcher, Section 2 dossier, Section 3 comparisons), the existing
assets (`india/source/india.fbx`, `india/textures/`, `data/geo/india_boundary.geojson`,
`DIV_COORDS`), and the **new observed data layer** (`imd_observed_subdivisions.csv`
2015–2025, `imd_all_india_monthly.csv` / `imd_all_india_monsoon.csv` 1901–2026) that
makes several of these ideas possible for the first time.

---

## 0. Design principles (the taste guardrails)

1. **Data is the hero.** Every flashy effect must encode a real number — rain
   intensity, departure, trend — never decoration for its own sake.
2. **One identity.** Keep the dark-navy `#0B1428` / amber `#E0A526` / electric-blue
   `#38BDF8` palette from the decks; the site and the Review 3 deck should feel
   like one product family.
3. **60 FPS or it doesn't ship.** The current WebGL map sets the bar; anything 3D
   must be GPU-driven (Deck.gl/pydeck/Plotly WebGL), never 2,000 SVG nodes.
4. **Progressive disclosure.** Wow on first paint; every click reveals a number
   you can cite in the report.
5. **Streamlit-first.** Everything below is buildable inside Streamlit + custom
   components; Section 7 says when it's right to graduate to a standalone app.

---

## 1. Honest baseline (what exists today)

| Component | Status | Weakness |
|---|---|---|
| WebGL MapLibre map | strong | Divisions shown as **dots**, not shapes; no time dimension |
| 3D Sculpted model (`india.fbx`) | good demo | Static — shows no rainfall data at all |
| 3D Globe (Plotly) | decent | Flat markers; no terrain, no atmosphere |
| Dossier panel | strong | Text/table heavy |
| All-states comparison | good | Static bars |
| Theme toggle, rain particles | nice | Particles are decorative, not data-driven |

**Biggest gaps:** no true subdivision *choropleth* (filled shapes), no time
scrubbing across 125 years, no 3D where the third axis *is* rainfall, and no
use of the new 2016–2026 observed layer anywhere in the UI.

---

## 2. The 3D centerpiece ideas

### A. 🌧️ Rainfall-Height India — "the subcontinent as a bar chart of itself"
**The single highest-impact upgrade.** Extrude each IMD subdivision to a 3D prism
whose **height = seasonal rainfall** and colour = % departure. Konkan & Goa towers
over the Rajasthan plain — the 24× regional contrast (finding 2) becomes physical.

- Tech: `pydeck` `PolygonLayer` with `get_elevation` + `get_fill_color`, GPU-lit
  (`extruded=True`, `coverage=0.9`), orbitable camera. Runs inside Streamlit via
  `st.pydeck_chart` at 60 FPS.
- Data hook: pivot `imd_observed_subdivisions.csv` + pipeline layer to
  (division → polygon, height, colour); needs a **subdivision boundary GeoJSON**
  (see §3-F).
- Interaction: season selector (WINTER/PRE-MONSOON/MONSOON/POST/ANNUAL) morphs
  the skyline; clicking a prism opens the existing dossier.
- Effort: ~1 day once GeoJSON exists. Demo-wattage: ★★★★★.

### B. ⏳ The 125-Year Time Machine
A year scrubber (1901 → **2026**) that animates the map through every monsoon:
1918 drought, 1933 flood, 1972, 2009, 2019 (+11.8%), the 2016–2025 observed
decade, and the live **2026 deficit (−12.6%)** as the final frame.

- Tech: precompute per-year colour/elevation scales into a JSON blob; animate
  with `st.slider` (server-side) or a tiny custom component (client-side,
  requestAnimationFrame). Plotly `animation_frame` works for the globe today.
- Data hook: pipeline layer 1901–2015 + observed 2016–2026 — finally one
  continuous 125-year series *because* of the new fetch.
- Extra: a "deficit epochs" ribbon under the slider (1918–29, 1950–58, 1979–86,
  2009–15, 2026) auto-scrolls the story.
- Effort: 1–2 days. Demo-wattage: ★★★★★ — this is the review-demo moment.

### C. 🌬️ Monsoon Onset Replay — wind-streamline particles
Animate the monsoon's arrival: particle streamlines sweeping from the Arabian
Sea branch (Kerala, ~1 June) and the Bay branch (NE India, ~5 June) across the
subcontinent, with the onset dates IMD publishes per year.

- Tech: custom HTML component (canvas/WebGL, ~150 lines) layered under the
  pydeck view; particles follow a hand-tuned wind field (two jet streams +
  orographic deflection by the Western Ghats). Not a physics model — a
  narrated animation, honestly labelled as such.
- Data hook: IMD onset/withdrawal dates per year (fetchable from IMD LRF pages);
  particle density per division ∝ that week's rainfall.
- Effort: 2–3 days. Demo-wattage: ★★★★★.

### D. 🗿 The fbx model, but data-driven
The existing 3D sculpted model is beautiful and shows nothing. Give it a job:

- **Rain skin:** recolour the model's surface per-vertex by rainfall departure
  (green→amber→red), updated with the season selector.
- **Cloud layer:** a semi-transparent volume above regions currently in their
  wet season, with animated drift.
- **Rainfall pins:** glowing 3D columns rising from each division centroid,
  height = 1-in-20-year deficit depth — turning the drought finding into a
  landscape of spikes over West Rajasthan.
- Tech: the current FBX render is via an embedded Sketchfab viewer; to make it
  data-driven, re-export the mesh to glTF and render with `three.js` in a custom
  Streamlit component (`st.components.v1.html`), passing a JSON of colours per
  region via `window.postMessage` or a templated HTML string.
- Effort: 3–4 days (glTF conversion + three.js component). Demo-wattage: ★★★★.

### E. 🌍 Atmosphere upgrade for the globe
Keep the Plotly globe but add: a soft atmosphere rim (glow shader via
`plotly`'s `surfacepattern`… in practice: a second transparent sphere), graticule
lines, night-side city lights, and the **2026 monsoon arc** — an animated great-circle
of moisture from the Indian Ocean. Division markers become pulsing spheres whose
radius = CV (bigger = less reliable), making "reliability" visible at a glance.
Effort: 1 day. Demo-wattage: ★★★.

---

## 3. Better India map visualizations (2D, but smarter)

### F. True subdivision choropleth (prerequisite for A)
The dots must become the actual 36 IMD subdivision polygons. Source: the IMD
subdivision shapefile (datameet community maps or the shapefile cited in IITM
RR-138); convert to GeoJSON, harmonise names with our canonical 36 (the alias
map already exists in `fetch_observed.py`). Then the existing MapLibre/pydeck
views get filled shapes with the wet→dry green ramp.
Effort: 0.5 day (after obtaining the shapefile). Unblocks A, B, G.

### G. Hex-state small multiples — "36 sparkline grid"
A wall of 36 mini line-charts (one per division, 1901–2026, trend line + BH
significance tick), laid out geographically. The grid IS the map. Hover any
cell → dossier; the grid doubles as a navigation menu.
Effort: 1 day. Demo-wattage: ★★★★ (and it's the fastest way to show "region
explains 86% of variance" visually).

### H. Deficit-epoch ribbon timeline
National annual series 1901–2026 as a slim ribbon under the hero: green/amber/red
bands per year, with the four deficit epochs + 2026 labelled. Clicking an epoch
jumps the Time Machine (B) to that window.
Effort: 0.5 day.

### I. Seasonal radial clock
A polar chart: 12 spokes (months), radius = rainfall, one ring per decade
(1900s…2020s). The monsoon bulge (73.7%) and its stability across 125 years is
instantly visible; the 2020s ring in amber shows the recent wet decade.
Effort: 0.5 day.

### J. Story mode: "Kerala's two droughts"
A scroll-driven mini-story using the observed layer: Kerala −34% in 2016,
−34% again in 2023, with reservoir photos (public), the 1-in-20-year level from
the report, and the honest caveat that return periods are not forecasts.
Streamlit's `st.dialog`/tabs can host this; or a horizontal card carousel.
Effort: 1 day. Demo-wattage: ★★★★ (emotional anchor for the panel).

---

## 4. Flashier UI layer

| Idea | What | Effort |
|---|---|---|
| K. Cinematic hero | Full-bleed animated hero: the time-machine map blurred behind the title, KPI numbers counting up (75.2% → 73.7% observed), monsoon-green shimmer sweep | 1 day |
| L. **Live 2026 banner** | "2026 monsoon in progress: 759 mm, −12.6% of normal" — a pulsing amber/red banner fed by `imd_all_india_monsoon.csv`; updates on every `fetch_observed.py` re-run | 0.5 day |
| M. Glass cards + micro-interactions | Frosted-glass stat cards (backdrop-filter), hover-lift, Lottie rain icon on the theme toggle; keep Outfit font | 0.5 day |
| N. Data-driven audio (opt-in) | Gentle rain loop whose intensity follows the selected year's departure; muted by default, small toggle. Streamlit `st.audio` + a pre-rendered intensity mix | 0.5 day |
| O. Command-palette search | `/` opens a palette: jump to any division, season, finding, or section | 1 day |

---

## 5. Data wiring (what feeds what)

```
data/raw/india_rainfall.csv              (pipeline, 1901-2015) ─┐
data/raw/imd_observed_subdivisions.csv   (observed, 2015-2025) ─┼─► unified series service
data/raw/imd_all_india_monthly.csv       (national, 1901-2026) ─┤   (one cached loader in app.py)
data/raw/imd_all_india_monsoon.csv       (monsoon, 1901-2026)  ─┘
                                                            │
        ┌───────────────┬───────────────┬───────────────┬───┴────────┬─────────────┐
        ▼               ▼               ▼               ▼            ▼             ▼
   A. 3D prisms    B. Time Machine  F. choropleth  G. spark grid  L. 2026 banner  J. Kerala story
```

One new module in `app.py` (or `scripts/data_service.py`): `load_unified()` returns
a tidy (year, division, season, mm, dep, layer) frame, caches with
`@st.cache_data`, and merges the three layers with explicit provenance tags so
every tooltip can say "observed IMD" vs "pipeline layer (generated)".

---

## 6. Tech decision matrix

| Approach | 3D quality | Streamlit fit | Risk | Verdict |
|---|---|---|---|---|
| **pydeck (Deck.gl)** | excellent (GPU, extrusions, lighting) | native `st.pydeck_chart` | low | **use for A/B/F** |
| Plotly 3D (surface/mesh/scatter3d) | good | native | low | keep for globe (E) |
| three.js custom component | best (fbx/glTF, shaders, particles) | via `components.v1.html` | medium | use for C/D when needed |
| kepler.gl | great but heavy | `streamlit-keplergl` | medium | skip (less control) |
| folium/leaflet | 2D only | existing dep | low | retire — superseded by MapLibre/pydeck |
| Standalone React + r3f | best-in-class | none (rewrite) | high | only if the project becomes a portfolio site (post-course) |

Performance rules of thumb: subdivision polygons are tiny (36 shapes) — anything
scales; the time-machine precomputes all 125 frames of colour/elevation as
arrays (~36×125×2 floats ≈ 36 KB), so animation is trivial.

---

## 7. Phased roadmap

> **Status: Phase 1 SHIPPED** — the subdivision GeoJSON exists
> (`data/geo/imd_subdivisions.geojson`, built by
> `scripts/data/build_subdivision_geo.py` from IMD's own district file),
> `app.py` has the **🏗️ 3D Rainfall-Height Atlas (1901–2026)** map style
> (pydeck extruded prisms, season + year controls, dossier picker), the
> unified data service `load_unified_subdivisions()`, the **live 2026
> monsoon banner**, and the departure-colour legend. Verified: zero
> exceptions across all map paths (Streamlit AppTest) and a real browser
> render check (Chrome + pixel analysis confirms data-coloured prisms).

**Phase 1 — "Map, but real" (2–3 days, immediately demoable)** ✅ DONE
F (subdivision choropleth) → A (3D rainfall-height prisms) → L (live 2026 banner).
H (epoch ribbon) remains a small follow-up.

**Phase 2 — "Time and story" (3–4 days)**
B (125-year time machine — animate the existing year slider client-side) →
G (spark-grid wall) → J (Kerala story) → I (radial clock).

**Phase 3 — "The wow pass" (3–5 days, optional)**
C (monsoon onset particles) → D (data-driven fbx) → E (atmosphere globe) →
K/M/N/O UI polish.

**Not doing (taste calls):** no spinning-by-default camera; no sound on load;
no dark-pattern contrast loss (WCAG AA on all text); no fake data anywhere —
every effect cites its layer and year.

---

## 8. First concrete commit (if you start tomorrow)

1. Obtain IMD subdivision boundaries → `data/geo/imd_subdivisions.geojson`
   (name-harmonised with `fetch_observed.py`'s canonical map).
2. Add `load_unified()` + `st.cache_data` to `app.py`.
3. Replace the WebGL dot map's marker layer with a pydeck `PolygonLayer`
   (`extruded=True`, elevation = selected season's mm, colour = % dep ramp).
4. Add the season selector + year slider already present in the sidebar, and the
   2026 banner at the top.
5. Screenshot before/after — the Phase-1 pitch is done.
