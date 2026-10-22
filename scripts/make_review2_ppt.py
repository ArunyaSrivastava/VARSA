#!/usr/bin/env python3
"""
Generate VARSA_Review_2.pptx — progress update for faculty review.
Matches the dark-blue / amber design language of VARSA_Review_1_v7.pptx.
"""

from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pathlib import Path

# ── Palette (exact colours from v7) ─────────────────────────────────────────
BG_DARK   = RGBColor(0x0B, 0x14, 0x28)
AMBER     = RGBColor(0xE0, 0xA5, 0x26)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
MUTED     = RGBColor(0xC9, 0xD6, 0xEA)
ACCENT    = RGBColor(0x38, 0xBD, 0xF8)
GREEN     = RGBColor(0x22, 0xC5, 0x5E)
CARD_BG   = RGBColor(0x0F, 0x20, 0x40)
DIVIDER   = RGBColor(0x1E, 0x35, 0x58)

W = 12192000
H =  6858000
MARGIN_L = 548640


def emu(cm): return int(cm * 360000)


def _set_bg(slide, rgb):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = rgb


def _add_textbox(slide, left, top, width, height, text, size_pt,
                  bold=False, color=WHITE, align=PP_ALIGN.LEFT,
                  italic=False, wrap=True):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    try:
        run.font.name = "Outfit"
    except Exception:
        pass
    return txb


def _add_rect(slide, left, top, width, height, fill_rgb):
    shape = slide.shapes.add_shape(1, left, top, width, height)
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    return shape


def _add_rule(slide, left, top, width, color=None):
    color = color or DIVIDER
    connector = slide.shapes.add_shape(1, left, top, width, emu(0.05))
    connector.line.fill.background()
    connector.fill.solid()
    connector.fill.fore_color.rgb = color
    return connector


def _footer(slide, page_num):
    _add_rect(slide, 0, H - emu(0.8), W, emu(0.8), CARD_BG)
    _add_textbox(slide, MARGIN_L, H - emu(0.72), emu(14), emu(0.6),
                  "VARSA  ·  Probability & Statistics  ·  BAMAT207",
                  7.5, color=MUTED)
    _add_textbox(slide, W - emu(2.5), H - emu(0.72), emu(2.4), emu(0.6),
                  str(page_num), 7.5, color=MUTED, align=PP_ALIGN.RIGHT)


def _section_label(slide, text, top_offset=None):
    t = top_offset if top_offset is not None else MARGIN_L
    _add_textbox(slide, MARGIN_L, t, W - 2 * MARGIN_L, emu(0.6),
                  text, 8.5, bold=True, color=AMBER)


def _heading(slide, text, top_offset=None, size=24):
    t = top_offset if top_offset is not None else MARGIN_L + emu(0.65)
    _add_textbox(slide, MARGIN_L, t, W - 2 * MARGIN_L, emu(1.5),
                  text, size, bold=True, color=WHITE)


def _bullet(slide, text, left, top, width=None, size=10.5, color=None, bold=False):
    color = color or MUTED
    w = width or (W - left - MARGIN_L)
    _add_textbox(slide, left, top, w, emu(0.55),
                  "▸  " + text, size, color=color, bold=bold)


# ──────────────────────────────────────────────────────────────────────────────
# SLIDES
# ──────────────────────────────────────────────────────────────────────────────

def slide_cover(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)

    _add_textbox(slide, MARGIN_L, emu(2.3), emu(18), emu(0.65),
                  "PROBABILITY & STATISTICS  ·  REVIEW 2", 9, bold=True, color=AMBER)
    _add_textbox(slide, MARGIN_L, emu(3.0), emu(18), emu(3.2),
                  "VARSA", 92, bold=True, color=WHITE)
    _add_textbox(slide, MARGIN_L, emu(6.2), emu(18), emu(1.0),
                  "Variability, Anomalies and Regional Statistics of Indian Rainfall",
                  16.5, color=WHITE)
    _add_textbox(slide, MARGIN_L, emu(9.3), emu(18), emu(0.65),
                  "INTERACTIVE DASHBOARD  ·  DATA LIMITATIONS  ·  NEXT STEPS",
                  9, bold=True, color=AMBER)
    _add_textbox(slide, MARGIN_L, emu(10.0), emu(18), emu(0.65),
                  "Website built on IMR dataset  |  1901–2015  |  36 Met-subdivisions",
                  9.5, color=MUTED)

    _add_rect(slide, MARGIN_L, emu(11.5), W - 2 * MARGIN_L, emu(5.2), CARD_BG)
    _add_textbox(slide, emu(2.4), emu(12.2), emu(8.8), emu(0.8),
                  "COURSE", 7.7, bold=True, color=AMBER)
    _add_textbox(slide, emu(2.4), emu(12.9), emu(13.2), emu(1.0),
                  "Probability and Statistics (BAMAT207)", 12, bold=True, color=WHITE)
    _add_textbox(slide, emu(2.4), emu(14.1), emu(8.8), emu(0.8),
                  "FACULTY GUIDE", 7.7, bold=True, color=AMBER)
    _add_textbox(slide, emu(2.4), emu(14.8), emu(13.2), emu(1.0),
                  "Dr. Juhi Baroi", 12, bold=True, color=WHITE)

    _add_textbox(slide, emu(17.5), emu(12.2), emu(8.8), emu(0.8),
                  "TEAM", 7.7, bold=True, color=AMBER)
    for i, (name, roll) in enumerate([("Pratik", "25BCE0337"),
                                        ("Adarsh", "25BCE0401"),
                                        ("Arunya", "25BCE0344")]):
        y = emu(12.9) + i * emu(0.96)
        _add_textbox(slide, emu(17.5), y, emu(6.6), emu(0.85),
                      name, 11.5, bold=True, color=WHITE)
        _add_textbox(slide, emu(24.1), y, emu(7.6), emu(0.85),
                      roll, 10.5, color=MUTED)

    _add_textbox(slide, MARGIN_L, emu(17.4), emu(15.2), emu(0.75),
                  "October 2026", 7.7, color=MUTED)


def slide_agenda(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "OVERVIEW", top_offset=MARGIN_L)
    _heading(slide, "What we cover today", top_offset=emu(1.7), size=26)
    _add_rule(slide, MARGIN_L, emu(3.6), W - 2 * MARGIN_L)

    items = [
        ("01", "Recap — what Review 1 established",        MUTED),
        ("02", "The VARSA Website — features & live demo",  ACCENT),
        ("03", "Data deep-dive — IMR dataset limitations",  AMBER),
        ("04", "Current findings already reflected online", MUTED),
        ("05", "What's next — better data, wider scope",    GREEN),
    ]
    col_w = emu(10)
    for idx, (num, label, col) in enumerate(items):
        y = emu(4.2) + idx * emu(1.6)
        _add_rect(slide, MARGIN_L, y, emu(1.6), emu(1.1), CARD_BG)
        _add_textbox(slide, MARGIN_L + emu(0.15), y + emu(0.12), emu(1.3), emu(0.9),
                      num, 18, bold=True, color=col, align=PP_ALIGN.CENTER)
        _add_textbox(slide, MARGIN_L + emu(2.0), y + emu(0.22), W - MARGIN_L - emu(2.5), emu(0.75),
                      label, 13, bold=True, color=WHITE)
    _footer(slide, 2)


def slide_recap(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "01  ·  RECAP", top_offset=MARGIN_L)
    _heading(slide, "What Review 1 established", top_offset=emu(1.7), size=24)
    _add_rule(slide, MARGIN_L, emu(3.55), W - 2 * MARGIN_L)

    stats = [
        ("75.2%",   "monsoon contribution",   "Jun-Sep share of annual rain",    WHITE),
        ("87%",     "variance by region",      "eta-squared from Welch ANOVA",    ACCENT),
        ("9 of 36", "real trends",             "survive BH correction at 5% FDR", GREEN),
        ("47.6%",   "1-in-20 yr deficit",      "West Rajasthan worst division",   AMBER),
    ]
    col_x = [MARGIN_L, MARGIN_L + emu(8.0), MARGIN_L + emu(16.0), MARGIN_L + emu(24.0)]
    for (val, lbl, sub, col), x in zip(stats, col_x):
        _add_rect(slide, x, emu(4.0), emu(7.4), emu(3.8), CARD_BG)
        _add_textbox(slide, x + emu(0.4), emu(4.3), emu(7.0), emu(1.4),
                      val, 26, bold=True, color=col)
        _add_textbox(slide, x + emu(0.4), emu(5.65), emu(7.0), emu(0.65),
                      lbl, 9, bold=True, color=AMBER)
        _add_textbox(slide, x + emu(0.4), emu(6.3), emu(7.0), emu(0.6),
                      sub, 8, color=MUTED)

    _add_textbox(slide, MARGIN_L, emu(8.5), W - 2 * MARGIN_L, emu(0.65),
                  "These results now power every chart and table inside the VARSA website.", 9.5, color=MUTED)
    _footer(slide, 3)


def slide_website_overview(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "02  ·  THE VARSA WEBSITE", top_offset=MARGIN_L)
    _heading(slide, "An interactive dashboard for Indian rainfall analytics",
              top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    features = [
        ("Map  |  WebGL",            "60-FPS hardware-accelerated choropleth of all 36 subdivisions"),
        ("Globe  |  3D Interactive", "Tilt-able globe; rainfall intensity as colour overlay"),
        ("Dossier  |  Stats Panel",  "Division-level descriptive stats: CV, skewness, kurtosis"),
        ("Trend Analysis",           "OLS and Mann-Kendall with BH-corrected significance flags"),
        ("Distribution Fits",        "Gamma and Lognormal fits vs observed; KS distances reported"),
        ("Theme Toggle",             "Dark / light modes; responsive layout for any screen size"),
    ]
    lft_w = emu(15.4)
    for i, (title, desc) in enumerate(features):
        y = emu(4.0) + i * emu(1.55)
        _add_rect(slide, MARGIN_L, y, lft_w, emu(1.3), CARD_BG)
        _add_textbox(slide, MARGIN_L + emu(0.3), y + emu(0.1), lft_w - emu(0.3), emu(0.65),
                      title, 10.5, bold=True, color=ACCENT)
        _add_textbox(slide, MARGIN_L + emu(0.3), y + emu(0.68), lft_w - emu(0.3), emu(0.55),
                      desc, 8.5, color=MUTED)

    rgt_x = MARGIN_L + lft_w + emu(0.7)
    rgt_w = W - rgt_x - MARGIN_L
    _add_rect(slide, rgt_x, emu(4.0), rgt_w, emu(9.3), CARD_BG)
    _add_textbox(slide, rgt_x + emu(0.3), emu(4.3), rgt_w - emu(0.3), emu(0.65),
                  "BUILT WITH", 7.5, bold=True, color=AMBER)
    stack = ["Python 3.11 + Streamlit", "Plotly / WebGL rendering",
             "Pandas / NumPy / SciPy", "GeoJSON subdivision boundaries",
             "Google Fonts (Outfit, Plus Jakarta Sans)"]
    for j, s in enumerate(stack):
        _add_textbox(slide, rgt_x + emu(0.3), emu(5.1) + j * emu(1.2), rgt_w - emu(0.3), emu(0.7),
                      "▸  " + s, 9, color=MUTED)
    _footer(slide, 4)


def slide_website_features(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "02  ·  THE VARSA WEBSITE", top_offset=MARGIN_L)
    _heading(slide, "Three views — three ways to see the data",
              top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    panels = [
        ("ATLAS MAP",
         "Colour-coded choropleth by annual or seasonal rainfall. "
         "Click any subdivision for a 115-year history. "
         "Powered by WebGL — no page reload.",
         ACCENT),
        ("DOSSIER PANEL",
         "Per-subdivision statistical passport: mean, median, CV, skew, kurtosis, "
         "1-in-20-year return threshold, best-fit distribution, trend direction.",
         GREEN),
        ("ATLAS GLOBE",
         "3-D interactive globe; same colour scale, tiltable with mouse drag. "
         "Makes the spatial gradient from NE coast to Rajasthan visually striking.",
         AMBER),
    ]
    col_w = (W - 2 * MARGIN_L - emu(1.0)) // 3
    for k, (title, body, col) in enumerate(panels):
        x = MARGIN_L + k * (col_w + emu(0.5))
        _add_rect(slide, x, emu(4.0), col_w, emu(8.8), CARD_BG)
        _add_rect(slide, x, emu(4.0), col_w, emu(0.22), col)
        _add_textbox(slide, x + emu(0.3), emu(4.4), col_w - emu(0.4), emu(0.75),
                      title, 10, bold=True, color=col)
        _add_textbox(slide, x + emu(0.3), emu(5.3), col_w - emu(0.4), emu(5.0),
                      body, 9, color=MUTED, wrap=True)
    _footer(slide, 5)


def slide_data_limitations(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "03  ·  DATA LIMITATIONS", top_offset=MARGIN_L)
    _heading(slide, "The IMR dataset: what it gives us and what it doesn't",
              top_offset=emu(1.7), size=21)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    # Left — what we have
    _add_rect(slide, MARGIN_L, emu(4.0), emu(14.5), emu(9.3), CARD_BG)
    _add_rect(slide, MARGIN_L, emu(4.0), emu(14.5), emu(0.22), GREEN)
    _add_textbox(slide, MARGIN_L + emu(0.3), emu(4.4), emu(14.0), emu(0.65),
                  "WHAT WE HAVE", 9, bold=True, color=GREEN)
    haves = [
        "Monthly subdivision totals across 36 IMD met-divisions",
        "Full record 1901-2015  (115 years, 49 680 data points)",
        "Enough depth for ANOVA, trend tests, distribution fits",
        "Clean, public, reproducible — no API key required",
    ]
    for i, t in enumerate(haves):
        _bullet(slide, t, MARGIN_L + emu(0.3), emu(5.2) + i * emu(1.05), width=emu(14.0))

    # Right — limitations
    _add_rect(slide, MARGIN_L + emu(15.2), emu(4.0), emu(15.4), emu(9.3), CARD_BG)
    _add_rect(slide, MARGIN_L + emu(15.2), emu(4.0), emu(15.4), emu(0.22), AMBER)
    _add_textbox(slide, MARGIN_L + emu(15.5), emu(4.4), emu(15.0), emu(0.65),
                  "CURRENT LIMITATIONS", 9, bold=True, color=AMBER)
    limits = [
        "Data ends in 2015 — a decade of recent climate is missing",
        "Arrives in chunked annual files, not a single clean dataset",
        "Monthly granularity — no daily or sub-daily extremes",
        "Subdivision level only — no district or grid resolution",
        "No near-real-time stream; all figures are historical",
    ]
    for i, t in enumerate(limits):
        _bullet(slide, t, MARGIN_L + emu(15.5), emu(5.2) + i * emu(1.05), width=emu(15.0))
    _footer(slide, 6)


def slide_data_gap(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "03  ·  DATA LIMITATIONS", top_offset=MARGIN_L)
    _heading(slide, "A decade of rainfall is missing from the picture",
              top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    tl_top = emu(4.8)
    tl_h   = emu(0.7)
    tl_w   = W - 2 * MARGIN_L
    covered_w = int(tl_w * 0.92)

    _add_rect(slide, MARGIN_L, tl_top, covered_w, tl_h, GREEN)
    _add_rect(slide, MARGIN_L + covered_w, tl_top, tl_w - covered_w, tl_h, AMBER)

    _add_textbox(slide, MARGIN_L, tl_top - emu(0.8), emu(4), emu(0.65),
                  "Dataset covers 115 years (1901-2015)", 9, bold=True, color=GREEN)
    _add_textbox(slide, MARGIN_L + covered_w + emu(0.3), tl_top - emu(0.8), emu(8), emu(0.65),
                  "~10-year gap (2016-2026)", 9, bold=True, color=AMBER)

    _add_textbox(slide, MARGIN_L, tl_top + emu(0.9), emu(5), emu(0.6), "1901", 9, color=GREEN)
    _add_textbox(slide, MARGIN_L + covered_w - emu(1.5), tl_top + emu(0.9), emu(3), emu(0.6),
                  "2015", 9, color=GREEN)
    _add_textbox(slide, MARGIN_L + covered_w + emu(0.3), tl_top + emu(0.9), emu(4), emu(0.6),
                  "2026", 9, color=AMBER)

    bullets_data = [
        "2016-2026 includes anomalous monsoon years (2019 excess, 2023 deficit patterns)",
        "Climate-sensitive trends will be underestimated without the most-recent decade",
        "Drought-return-period estimates depend on the full distributional tail",
        "Policy models increasingly require post-2015 baselines",
    ]
    _add_textbox(slide, MARGIN_L, emu(7.2), W - 2 * MARGIN_L, emu(0.65),
                  "Why the gap matters", 11, bold=True, color=AMBER)
    for i, pt in enumerate(bullets_data):
        _bullet(slide, pt, MARGIN_L + emu(0.5), emu(8.0) + i * emu(1.1))
    _footer(slide, 7)


def slide_data_acquisition(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "03  ·  DATA LIMITATIONS", top_offset=MARGIN_L)
    _heading(slide, "IMR data comes in chunks — not as one clean dataset",
              top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    _add_textbox(slide, MARGIN_L, emu(4.0), W - 2 * MARGIN_L, emu(0.75),
                  "Unlike a Kaggle one-click download, IMD publishes data in separate "
                  "annual/decadal files requiring manual assembly and cleaning.",
                  10, color=MUTED, wrap=True)

    challenges = [
        ("Fragmented files",
         "Spread across individual yearly or decadal PDFs/XLS — "
         "each must be parsed and stitched into a single CSV."),
        ("Format inconsistency",
         "Column naming and subdivision codes changed across release periods "
         "(pre-1950 vs post-1970 publications differ significantly)."),
        ("No public API",
         "No programmatic endpoint for updates. All ingestion requires "
         "manual web scraping or IMD portal navigation."),
        ("Post-2015 access",
         "Files for 2016 onward are paywalled or need institutional IMD "
         "access, making automated retrieval difficult."),
    ]
    for i, (icon_title, desc) in enumerate(challenges):
        col = i % 2
        row = i // 2
        x = MARGIN_L + col * emu(16.5)
        y = emu(5.2) + row * emu(3.5)
        _add_rect(slide, x, y, emu(16.0), emu(3.1), CARD_BG)
        _add_textbox(slide, x + emu(0.3), y + emu(0.3), emu(15.5), emu(0.7),
                      icon_title, 10.5, bold=True, color=ACCENT)
        _add_textbox(slide, x + emu(0.3), y + emu(1.05), emu(15.5), emu(1.8),
                      desc, 9, color=MUTED, wrap=True)
    _footer(slide, 8)


def slide_findings(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "04  ·  CURRENT FINDINGS", top_offset=MARGIN_L)
    _heading(slide, "What the website already shows", top_offset=emu(1.7), size=24)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    findings = [
        ("Monsoon dominance",
         "75.2% of annual rain falls Jun-Sep. The map makes this "
         "instantly visible across all 36 subdivisions."),
        ("Sharp regional divide",
         "Assam & NE India: >2000 mm/yr. West Rajasthan: <200 mm/yr. "
         "The Globe view shows the gradient at a glance."),
        ("Skewed distributions",
         "Monsoon totals are right-skewed (pooled skew 1.51). "
         "Gamma / Lognormal fits plotted in Dossier; Normal shown as poor fit."),
        ("Corrected trend count",
         "9 of 36 subdivisions show significant trends after BH correction "
         "— clearly highlighted in the trend panel."),
        ("Drought thresholds",
         "1-in-20-year deficit per division: West Rajasthan 47.6%, "
         "Kerala 77.8% of long-run normal. Mapped in the dossier."),
        ("CV and reliability",
         "Coefficient of Variation 12% (Assam) to 41% (Saurashtra-Kutch). "
         "Visible in the stats panel."),
    ]
    col_w = (W - 2 * MARGIN_L - emu(0.8)) // 2
    for i, (title, body) in enumerate(findings):
        col = i % 2
        row = i // 2
        x = MARGIN_L + col * (col_w + emu(0.8))
        y = emu(4.0) + row * emu(2.6)
        _add_rect(slide, x, y, col_w, emu(2.4), CARD_BG)
        _add_textbox(slide, x + emu(0.3), y + emu(0.2), col_w - emu(0.4), emu(0.65),
                      title, 9.5, bold=True, color=ACCENT)
        _add_textbox(slide, x + emu(0.3), y + emu(0.85), col_w - emu(0.4), emu(1.4),
                      body, 8.5, color=MUTED, wrap=True)
    _footer(slide, 9)


def slide_next_data(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "05  ·  WHAT'S NEXT", top_offset=MARGIN_L)
    _heading(slide, "Priority: acquire updated post-2015 rainfall data",
              top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    sources = [
        ("IMD Official Portal",
          "imdpune.gov.in — apply for institutional data request. Monthly subdivision "
          "data available for registered users. Estimated approval lag: 2-4 weeks.",
          GREEN, "Preferred"),
        ("ERA5 Reanalysis  (ECMWF)",
          "Copernicus CDS: 0.25 degree grid, hourly, 1940-2025. Python cdsapi available. "
          "Aggregation to IMD subdivisions via boundary shapefile needed.",
          ACCENT, "High quality"),
        ("CHIRPS / PERSIANN",
          "UC Santa Barbara rainfall estimate from satellite; daily, 0.05 degree grid, "
          "1981-present. Open access. Less accurate over orographic terrain.",
          AMBER, "Backup"),
        ("Kaggle / Zenodo community datasets",
          "Community-curated datasets sometimes extend to 2022-2023. "
          "Verify against IMD bulletins before use — may contain processing errors.",
          MUTED, "Verify first"),
    ]
    for i, (title, body, col, badge) in enumerate(sources):
        y = emu(4.1) + i * emu(2.6)
        bw = W - 2 * MARGIN_L - emu(0.5)
        _add_rect(slide, MARGIN_L, y, bw, emu(2.3), CARD_BG)
        _add_rect(slide, MARGIN_L, y, emu(0.25), emu(2.3), col)
        _add_rect(slide, W - MARGIN_L - emu(5.5), y + emu(0.3), emu(5.0), emu(0.65), col)
        _add_textbox(slide, W - MARGIN_L - emu(5.4), y + emu(0.33), emu(4.8), emu(0.55),
                      badge, 7.5, bold=True, color=BG_DARK, align=PP_ALIGN.CENTER)
        _add_textbox(slide, MARGIN_L + emu(0.6), y + emu(0.2), bw - emu(6.0), emu(0.7),
                      title, 10.5, bold=True, color=col)
        _add_textbox(slide, MARGIN_L + emu(0.6), y + emu(0.9), bw - emu(6.0), emu(1.2),
                      body, 8.5, color=MUTED, wrap=True)
    _footer(slide, 10)


def slide_next_analysis(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "05  ·  WHAT'S NEXT", top_offset=MARGIN_L)
    _heading(slide, "Once new data lands — planned analyses",
              top_offset=emu(1.7), size=24)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    analyses = [
        ("1", "Extend trend analysis to 2025",
         "Re-run OLS and Mann-Kendall on 1901-2025 series. See if BH-corrected count "
         "shifts from current 9-of-36. Climate signal clearer with 10 more years.",
         ACCENT),
        ("2", "Update distribution fits and return periods",
         "Refit Gamma / Lognormal with extended tails. Recalculate 1-in-20-year "
         "return thresholds per division — key metric for drought planning.",
         GREEN),
        ("3", "District-level resolution",
         "If ERA5 or CHIRPS used, aggregate to ~700 IMD districts for finer "
         "spatial risk mapping. Heat-map view added to the website.",
         AMBER),
        ("4", "ENSO / IOD correlation layer",
         "Overlay Nino 3.4 index against subdivision anomalies. Quantify "
         "teleconnection strength via Pearson r and lagged cross-correlation.",
         WHITE),
        ("5", "Automated refresh pipeline",
         "Cron-pull → clean → recompute stats → update GeoJSON → hot-reload "
         "Streamlit app. Target: monthly cadence once data source is stable.",
         ACCENT),
    ]
    for i, (num, title, body, col) in enumerate(analyses):
        y = emu(4.0) + i * emu(2.1)
        _add_rect(slide, MARGIN_L, y, emu(1.8), emu(1.8), CARD_BG)
        _add_textbox(slide, MARGIN_L + emu(0.2), y + emu(0.35), emu(1.4), emu(1.0),
                      num, 20, bold=True, color=col, align=PP_ALIGN.CENTER)
        _add_rect(slide, MARGIN_L + emu(2.1), y, W - 2 * MARGIN_L - emu(2.1), emu(1.8), CARD_BG)
        _add_textbox(slide, MARGIN_L + emu(2.5), y + emu(0.15), W - 2 * MARGIN_L - emu(3.0), emu(0.65),
                      title, 10.5, bold=True, color=col)
        _add_textbox(slide, MARGIN_L + emu(2.5), y + emu(0.8), W - 2 * MARGIN_L - emu(3.0), emu(0.85),
                      body, 8.5, color=MUTED, wrap=True)
    _footer(slide, 11)


def slide_summary(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    _section_label(slide, "SUMMARY", top_offset=MARGIN_L)
    _heading(slide, "What we built  ·  what we know  ·  what comes next",
              top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    points = [
        ("VARSA Website is live",
         "Streamlit dashboard; WebGL map, 3D globe, dossier panel — powered by "
         "the 1901-2015 IMR dataset and the stats from Review 1.",
         GREEN),
        ("Six key findings visualised",
         "Monsoon dominance, regional variance, skewed distributions, corrected "
         "trend count, drought thresholds, and CV map — all on screen.",
         ACCENT),
        ("Data ceiling at 2015",
         "The IMR dataset ends 10 years ago. Post-2015 climate signal, including "
         "more-recent monsoon extremes, is not yet captured.",
         AMBER),
        ("Next: extend the dataset",
         "IMD portal request, ERA5 reanalysis, or CHIRPS satellite product. "
         "District resolution and ENSO correlation planned once data lands.",
         WHITE),
    ]
    for i, (title, body, col) in enumerate(points):
        y = emu(4.0) + i * emu(2.5)
        _add_rect(slide, MARGIN_L, y, emu(0.3), emu(2.0), col)
        _add_textbox(slide, MARGIN_L + emu(0.7), y + emu(0.1), W - 2 * MARGIN_L - emu(1.0), emu(0.7),
                      title, 11, bold=True, color=col)
        _add_textbox(slide, MARGIN_L + emu(0.7), y + emu(0.85), W - 2 * MARGIN_L - emu(1.0), emu(1.0),
                      body, 9, color=MUTED, wrap=True)
    _footer(slide, 12)


def slide_closing(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)

    _add_textbox(slide, MARGIN_L, emu(5.0), W - 2 * MARGIN_L, emu(2.5),
                  "VARSA turns historical rainfall records into statistically defensible findings —\n"
                  "and the website makes every finding explorable in real time.",
                  16, bold=True, color=WHITE, align=PP_ALIGN.CENTER, wrap=True)
    _add_textbox(slide, MARGIN_L, emu(8.2), W - 2 * MARGIN_L, emu(0.9),
                  "Questions welcome", 13, color=MUTED, align=PP_ALIGN.CENTER)
    _add_rule(slide, emu(10), emu(9.6), emu(14), color=DIVIDER)
    _add_textbox(slide, MARGIN_L, emu(10.3), W - 2 * MARGIN_L, emu(0.7),
                  "Pratik (25BCE0337)  ·  Adarsh (25BCE0401)  ·  Arunya (25BCE0344)",
                  9, color=MUTED, align=PP_ALIGN.CENTER)
    _add_textbox(slide, MARGIN_L, emu(11.0), W - 2 * MARGIN_L, emu(0.65),
                  "Dr. Juhi Baroi  ·  Probability and Statistics (BAMAT207)",
                  8.5, color=MUTED, align=PP_ALIGN.CENTER)
    _add_textbox(slide, MARGIN_L, emu(11.9), W - 2 * MARGIN_L, emu(0.6),
                  "Website: localhost:8501  |  Data: IMD 1901-2015  |  October 2026",
                  7.5, color=RGBColor(0x44, 0x5F, 0x7A), align=PP_ALIGN.CENTER)


# ──────────────────────────────────────────────────────────────────────────────
# ASSEMBLE
# ──────────────────────────────────────────────────────────────────────────────

def build():
    prs = Presentation()
    prs.slide_width  = Emu(W)
    prs.slide_height = Emu(H)

    slide_cover(prs)
    slide_agenda(prs)
    slide_recap(prs)
    slide_website_overview(prs)
    slide_website_features(prs)
    slide_data_limitations(prs)
    slide_data_gap(prs)
    slide_data_acquisition(prs)
    slide_findings(prs)
    slide_next_data(prs)
    slide_next_analysis(prs)
    slide_summary(prs)
    slide_closing(prs)

    out = Path("/Users/arunyasrivastava/rainfall/VARSA_Review_2.pptx")
    prs.save(str(out))
    size_kb = out.stat().st_size // 1024
    print(f"Saved {out}  ({size_kb} KB,  {len(prs.slides)} slides)")


if __name__ == "__main__":
    build()
