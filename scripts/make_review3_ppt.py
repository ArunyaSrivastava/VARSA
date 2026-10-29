#!/usr/bin/env python3
"""
Generate VARSA_Review_3.pptx — final report presentation.
Matches the dark-blue / amber design language of VARSA_Review_1_v7.pptx and
VARSA_Review_2.pptx, and embeds the figures produced by scripts/final_analysis.py.

Run AFTER final_analysis.py (figures must exist in review_3/):
    python scripts/make_review3_ppt.py
"""

import json
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt

BASE = Path(__file__).resolve().parent.parent
R3 = BASE / "review_3"
RESULTS = json.loads((R3 / "analysis_results.json").read_text())

# ── Palette (exact colours from Review 1 v7 / Review 2) ──────────────────────
BG_DARK = RGBColor(0x0B, 0x14, 0x28)
AMBER = RGBColor(0xE0, 0xA5, 0x26)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0xC9, 0xD6, 0xEA)
ACCENT = RGBColor(0x38, 0xBD, 0xF8)
GREEN = RGBColor(0x22, 0xC5, 0x5E)
RED = RGBColor(0xF8, 0x71, 0x71)
CARD_BG = RGBColor(0x0F, 0x20, 0x40)
DIVIDER = RGBColor(0x1E, 0x35, 0x58)

W = 12192000
H = 6858000
MARGIN_L = 548640
SLIDE_W_CM = W / 360000  # 33.87 cm
SLIDE_H_CM = H / 360000  # 19.05 cm


def emu(cm):
    return int(cm * 360000)


def _set_bg(slide, rgb):
    fill = slide.background.fill
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
                  "VARSA  ·  Probability & Statistics  ·  BAMAT207", 7.5, color=MUTED)
    _add_textbox(slide, W - emu(2.5), H - emu(0.72), emu(2.4), emu(0.6),
                  str(page_num), 7.5, color=MUTED, align=PP_ALIGN.RIGHT)


def _section_label(slide, text, top_offset=None):
    t = emu(0.8)
    _add_textbox(slide, MARGIN_L, t, W - 2 * MARGIN_L, emu(0.55),
                  text, 8.5, bold=True, color=AMBER)


def _heading(slide, text, top_offset=None, size=24):
    t = emu(1.45)
    _add_textbox(slide, MARGIN_L, t, W - 2 * MARGIN_L, emu(1.5),
                 text, size, bold=True, color=WHITE)


def _bullet(slide, text, left, top, width=None, size=10.5, color=None, bold=False):
    color = color or MUTED
    w = width or (W - left - MARGIN_L)
    _add_textbox(slide, left, top, w, emu(0.55),
                 "▸  " + text, size, color=color, bold=bold)


def _slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    return slide


def _stat_card(slide, x, y, w, h, value, label, sub, color=WHITE, value_size=19):
    _add_rect(slide, x, y, w, h, CARD_BG)
    _add_textbox(slide, x + emu(0.35), y + emu(0.25), w - emu(0.5), emu(1.3),
                 value, value_size, bold=True, color=color)
    _add_textbox(slide, x + emu(0.35), y + emu(1.55), w - emu(0.5), emu(0.6),
                 label, 8.5, bold=True, color=AMBER)
    _add_textbox(slide, x + emu(0.35), y + emu(2.15), w - emu(0.5), emu(h / 360000 - 2.2),
                 sub, 7.5, color=MUTED)


def _img_aspect(path):
    with Image.open(path) as im:
        return im.width / im.height


def _add_figure(slide, filename, top_cm, width_cm, left_cm=None):
    path = R3 / filename
    aspect = _img_aspect(path)
    h = width_cm / aspect
    left = emu(left_cm if left_cm is not None else (SLIDE_W_CM - width_cm) / 2)
    slide.shapes.add_picture(str(path), left, emu(top_cm), width=emu(width_cm))
    return h


# ══════════════════════════════════════════════════════════════════════════════
# SLIDES
# ══════════════════════════════════════════════════════════════════════════════

def slide_cover(prs):
    slide = _slide(prs)

    _add_textbox(slide, MARGIN_L, emu(2.3), emu(18), emu(0.65),
                 "PROBABILITY & STATISTICS  ·  REVIEW 3  ·  FINAL REPORT", 9, bold=True, color=AMBER)
    _add_textbox(slide, MARGIN_L, emu(3.0), emu(18), emu(3.2),
                 "VARSA", 92, bold=True, color=WHITE)
    _add_textbox(slide, MARGIN_L, emu(6.2), emu(18), emu(1.0),
                 "Variability, Anomalies and Regional Statistics of Indian Rainfall",
                 16.5, color=WHITE)
    _add_textbox(slide, MARGIN_L, emu(9.3), emu(18), emu(0.65),
                 "FINAL RESULTS  ·  ASSUMPTION CHECKS  ·  RECOMMENDATION",
                 9, bold=True, color=AMBER)
    _add_textbox(slide, MARGIN_L, emu(10.0), emu(18), emu(0.65),
                 "Full statistical pipeline on 36 subdivisions  |  1901–2015  |  every number reproducible",
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


def slide_overview(prs):
    slide = _slide(prs)
    _section_label(slide, "OVERVIEW", top_offset=MARGIN_L)
    _heading(slide, "What the final report covers", top_offset=emu(1.7), size=26)
    _add_rule(slide, MARGIN_L, emu(3.6), W - 2 * MARGIN_L)

    items = [
        ("01", "Questions & scope — what we asked of the data", MUTED),
        ("02", "Data & audit — two layers, one reproducible pipeline", ACCENT),
        ("03", "Methods — the right test for each question", MUTED),
        ("04", "Key findings — six figures, six defensible claims", AMBER),
        ("05", "Verdict, limitations & recommendation", GREEN),
    ]
    for idx, (num, label, col) in enumerate(items):
        y = emu(4.2) + idx * emu(1.9)
        _add_rect(slide, MARGIN_L, y, emu(1.9), emu(1.3), CARD_BG)
        _add_textbox(slide, MARGIN_L + emu(0.1), y + emu(0.28), emu(1.7), emu(0.75),
                     num, 17, bold=True, color=col, align=PP_ALIGN.CENTER, wrap=False)
        _add_textbox(slide, MARGIN_L + emu(2.4), y + emu(0.3), W - MARGIN_L - emu(2.9), emu(0.8),
                     label, 13, bold=True, color=WHITE)
    _footer(slide, 2)


def slide_questions(prs):
    slide = _slide(prs)
    _section_label(slide, "01  ·  QUESTIONS", top_offset=MARGIN_L)
    _heading(slide, "Five questions, carried from Review 1 to the finish", top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    rqs = [
        ("RQ1", "How concentrated is rainfall in the June–September monsoon?"),
        ("RQ2", "How much do amount and reliability (CV) differ between subdivisions?"),
        ("RQ3", "Which distribution — Normal, Gamma or Lognormal — fits rainfall totals?"),
        ("RQ4", "Which subdivisions trend over 115 years, after correcting 36 tests?"),
        ("RQ5", "How deep is a 1-in-20-year deficit, nationally and by division?"),
    ]
    for i, (tag, q) in enumerate(rqs):
        y = emu(4.0) + i * emu(1.7)
        _add_rect(slide, MARGIN_L, y, emu(2.0), emu(1.3), CARD_BG)
        _add_textbox(slide, MARGIN_L + emu(0.15), y + emu(0.3), emu(1.7), emu(0.8),
                     tag, 12, bold=True, color=ACCENT, align=PP_ALIGN.CENTER, wrap=False)
        _add_textbox(slide, MARGIN_L + emu(2.4), y + emu(0.28), emu(19.0), emu(0.85),
                     q, 11.5, color=WHITE, wrap=True)

    _add_textbox(slide, MARGIN_L, emu(13.1), emu(22.0), emu(2.0),
                 "Why it matters: rainfall arrives in a few intense months and is spread "
                 "unevenly across regions — farmers and water planners need local reliability, "
                 "and statistics states how confident each claim can be.",
                 9.5, italic=True, color=MUTED, wrap=True)

    card_x = MARGIN_L + emu(23.3)
    card_w = W - MARGIN_L - card_x
    _add_rect(slide, card_x, emu(4.0), card_w, emu(11.6), CARD_BG)
    _add_rect(slide, card_x, emu(4.0), card_w, emu(0.22), AMBER)
    _add_textbox(slide, card_x + emu(0.3), emu(4.4), card_w - emu(0.6), emu(0.65),
                 "REVIEW 1  →  REVIEW 3", 9, bold=True, color=AMBER)
    steps = [
        "Review 1: preliminary numbers from the raw IMD CSV",
        "Review 2: interactive dashboard + data limitations logged",
        "Review 3: full pipeline — every figure, test and p-value regenerates from one command",
        "Same qualitative conclusions on both data layers",
    ]
    for j, s in enumerate(steps):
        _add_textbox(slide, card_x + emu(0.3), emu(5.3) + j * emu(2.55), card_w - emu(0.6), emu(2.4),
                     "▸  " + s, 9, color=MUTED, wrap=True)
    _footer(slide, 3)


def slide_scope(prs):
    slide = _slide(prs)
    _section_label(slide, "01  ·  SCOPE", top_offset=MARGIN_L)
    _heading(slide, "Scope & boundaries — stated up front", top_offset=emu(1.7), size=24)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    _add_rect(slide, MARGIN_L, emu(4.0), emu(15.4), emu(11.0), CARD_BG)
    _add_rect(slide, MARGIN_L, emu(4.0), emu(15.4), emu(0.22), GREEN)
    _add_textbox(slide, MARGIN_L + emu(0.3), emu(4.4), emu(15.0), emu(0.65),
                 "IN SCOPE", 9, bold=True, color=GREEN)
    ins = [
        "36 IMD meteorological subdivisions, 1901–2015",
        "Seasonal and annual aggregated totals",
        "ANOVA family, distribution fitting, OLS + Mann–Kendall, correlation",
        "Multiplicity control (BH/FDR) and assumption checks",
        "Reproducible Python pipeline + Streamlit dashboard",
    ]
    for i, t in enumerate(ins):
        _bullet(slide, t, MARGIN_L + emu(0.3), emu(5.3) + i * emu(1.55), width=emu(14.8), size=10)

    _add_rect(slide, MARGIN_L + emu(16.1), emu(4.0), emu(16.2), emu(11.0), CARD_BG)
    _add_rect(slide, MARGIN_L + emu(16.1), emu(4.0), emu(16.2), emu(0.22), RED)
    _add_textbox(slide, MARGIN_L + emu(16.4), emu(4.4), emu(15.8), emu(0.65),
                 "OUT OF SCOPE", 9, bold=True, color=RED)
    outs = [
        "District- or grid-level analysis",
        "Daily / sub-daily rainfall extremes",
        "Causal attribution of trends (e.g. to climate change)",
        "Real-time data ingestion; forecasting",
        "Spatial-statistical models (kriging, spatial autoregression)",
    ]
    for i, t in enumerate(outs):
        _bullet(slide, t, MARGIN_L + emu(16.4), emu(5.3) + i * emu(1.55), width=emu(15.6), size=10)

    _add_textbox(slide, MARGIN_L, emu(15.6), W - 2 * MARGIN_L, emu(0.7),
                 "Association is not causation: every method here describes patterns, not drivers.",
                 10, italic=True, color=MUTED)
    _footer(slide, 4)


def slide_data(prs):
    slide = _slide(prs)
    _section_label(slide, "02  ·  DATA & AUDIT", top_offset=MARGIN_L)
    _heading(slide, "Two data layers — one reproducible pipeline", top_offset=emu(1.7), size=24)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    _add_rect(slide, MARGIN_L, emu(4.0), emu(15.4), emu(6.6), CARD_BG)
    _add_textbox(slide, MARGIN_L + emu(0.3), emu(4.35), emu(15.0), emu(0.65),
                 "REFERENCE LAYER — RAW IMD", 9, bold=True, color=ACCENT)
    _add_textbox(slide, MARGIN_L + emu(0.3), emu(5.15), emu(15.0), emu(5.2),
                 "4,116 × 19 published subdivision file (data.gov.in / Kaggle mirror, "
                 "CC BY-SA 4.0). Used for Review 1's preliminary numbers — 12 monthly, "
                 "4 seasonal and 1 annual column per subdivision-year.",
                 10, color=MUTED, wrap=True)

    _add_rect(slide, MARGIN_L + emu(16.1), emu(4.0), emu(16.2), emu(6.6), CARD_BG)
    _add_rect(slide, MARGIN_L + emu(16.1), emu(4.0), emu(16.2), emu(0.22), GREEN)
    _add_textbox(slide, MARGIN_L + emu(16.4), emu(4.35), emu(15.8), emu(0.65),
                 "PIPELINE LAYER — ANALYSED (SEEDED, IN-REPO)", 9, bold=True, color=GREEN)
    _add_textbox(slide, MARGIN_L + emu(16.4), emu(5.15), emu(15.8), emu(5.2),
                 "IMD-calibrated generated series (36 × 115 × 5 = 20,700 rows) built because "
                 "the official file arrives in chunked releases needing manual assembly. "
                 "Powers the dashboard and every number in this deck.",
                 10, color=MUTED, wrap=True)

    audit = RESULTS["audit"]
    cards = [
        ("20,700 × 4", "rows × columns", "36 divisions · 115 years · 5 series each", WHITE),
        ("0 / 0", "missing / duplicates", "complete grid, no division-year gaps", GREEN),
        ("230", "flagged values", "1.1% slightly negative DJF (2 divisions) — artefact, documented", AMBER),
        ("1,217 mm", "national normal", "mean of 36 divisions, 1901–2015 (SD 148 mm)", ACCENT),
    ]
    cw = (SLIDE_W_CM - 2 * (MARGIN_L / 360000) - 3 * 0.5) / 4
    for i, (v, l, s, c) in enumerate(cards):
        _stat_card(slide, emu(MARGIN_L / 360000 + i * (cw + 0.5)), emu(11.2), emu(cw), emu(4.6), v, l, s, c)
    _add_textbox(slide, MARGIN_L, emu(16.3), W - 2 * MARGIN_L, emu(0.7),
                 "One command regenerates data + tests + figures:  python scripts/final_analysis.py",
                 10, italic=True, color=MUTED)
    _footer(slide, 5)


def slide_methods(prs):
    slide = _slide(prs)
    _section_label(slide, "03  ·  METHODS", top_offset=MARGIN_L)
    _heading(slide, "The right test for each question", top_offset=emu(1.7), size=24)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    rows = [
        ("Seasonality", "Seasonal means & shares; one-way ANOVA", "Quantifies concentration and its variance share", ACCENT),
        ("Regional variability", "Levene test → Welch ANOVA (η²)", "36 groups with unequal variances — Welch, not ordinary ANOVA", GREEN),
        ("Distributions", "MLE fits + Kolmogorov–Smirnov; Shapiro–Wilk", "Nonparametric fit comparison across Normal / Gamma / Lognormal", AMBER),
        ("Trends", "OLS + Mann–Kendall + Sen's slope; BH-FDR", "Linear + rank-based trend, corrected for 36 simultaneous tests", ACCENT),
        ("Drought", "Deficit counts; empirical 5th percentile", "1-in-20-year level from the record, no parametric assumption", GREEN),
        ("Independence", "Pearson r across all 630 division pairs", "Measures shared weather between subdivisions", AMBER),
    ]
    for i, (topic, method, why, col) in enumerate(rows):
        y = emu(4.0) + i * emu(1.62)
        _add_rect(slide, MARGIN_L, y, W - 2 * MARGIN_L, emu(1.38), CARD_BG)
        _add_rect(slide, MARGIN_L, y, emu(0.18), emu(1.38), col)
        _add_textbox(slide, MARGIN_L + emu(0.45), y + emu(0.13), emu(5.4), emu(0.65),
                     topic, 10.5, bold=True, color=col)
        _add_textbox(slide, MARGIN_L + emu(6.1), y + emu(0.13), emu(11.3), emu(1.1),
                     method, 10, bold=True, color=WHITE, wrap=True)
        _add_textbox(slide, MARGIN_L + emu(17.7), y + emu(0.13), emu(13.1), emu(1.1),
                     why, 9.5, color=MUTED, wrap=True)
    _add_textbox(slide, MARGIN_L, emu(14.1), W - 2 * MARGIN_L, emu(0.7),
                 "Every family of 36 tests gets Benjamini–Hochberg correction — raw p-values are always shown next to adjusted ones.",
                 10, italic=True, color=MUTED)
    _footer(slide, 6)


def _figure_slide(prs, page, section, heading, img, cards, img_width=20.0, img_top=4.1,
                  card_y=None, card_h=3.9, note=None):
    slide = _slide(prs)
    _section_label(slide, section, top_offset=MARGIN_L)
    _heading(slide, heading, top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    h = _add_figure(slide, img, img_top, img_width)
    if card_y is None:
        card_y = img_top + h + 0.55
    n = len(cards)
    gap = 0.5
    cw = (SLIDE_W_CM - 2 * (MARGIN_L / 360000) - (n - 1) * gap) / n
    for i, card in enumerate(cards):
        v, l, s, c = card[0], card[1], card[2], card[3]
        vs = card[4] if len(card) > 4 else 19
        _stat_card(slide, emu(MARGIN_L / 360000 + i * (cw + gap)), emu(card_y), emu(cw), emu(card_h),
                   v, l, s, c, value_size=vs)
    if note:
        _add_textbox(slide, MARGIN_L, emu(SLIDE_H_CM - 1.5), W - 2 * MARGIN_L, emu(0.65),
                     note, 9.5, italic=True, color=MUTED)
    _footer(slide, page)
    return slide


def slide_findings_map(prs):
    slide = _slide(prs)
    _section_label(slide, "04  ·  KEY FINDINGS", top_offset=MARGIN_L)
    _heading(slide, "Six figures, six defensible claims", top_offset=emu(1.7), size=24)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    claims = [
        ("1", "The monsoon dominates the rainfall year — everywhere", "73.7% national share; 67.8–80.3% by division", ACCENT),
        ("2", "Regions differ enormously, in amount and reliability", "24× mean range; CV 13.6% → 70.3%; η² = 0.861", GREEN),
        ("3", "Pooled totals are right-skewed — Normal is the wrong default", "KS: Normal 0.185 vs Lognormal 0.069", AMBER),
        ("4", "No trend survives multiple-testing correction", "3 → 0 of 36 after BH; national CI spans zero", RED),
        ("5", "Drought risk is intensely local", "1-in-20-yr: 15.8% of normal (W Rajasthan) vs 77.8% (Kerala)", ACCENT),
        ("6", "Divisions share weather — independence is violated", "64.9% of 630 pairs correlate significantly", GREEN),
    ]
    for i, (num, claim, detail, col) in enumerate(claims):
        y = emu(4.0) + i * emu(1.62)
        _add_rect(slide, MARGIN_L, y, W - 2 * MARGIN_L, emu(1.38), CARD_BG)
        _add_rect(slide, MARGIN_L, y, emu(0.18), emu(1.38), col)
        _add_textbox(slide, MARGIN_L + emu(0.5), y + emu(0.28), emu(1.2), emu(0.8),
                     num, 15, bold=True, color=col)
        _add_textbox(slide, MARGIN_L + emu(1.9), y + emu(0.13), emu(19.5), emu(0.7),
                     claim, 11.5, bold=True, color=WHITE)
        _add_textbox(slide, MARGIN_L + emu(1.9), y + emu(0.78), emu(28.5), emu(0.55),
                     detail, 9, color=MUTED)
    _add_textbox(slide, MARGIN_L, emu(14.2), W - 2 * MARGIN_L, emu(0.7),
                 "Each claim is shown with its figure on the next six slides — numbers match review_3/final_report.md exactly.",
                 10, italic=True, color=MUTED)
    _footer(slide, 7)


def build():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H

    slide_cover(prs)                 # 1
    slide_overview(prs)              # 2
    slide_questions(prs)             # 3
    slide_scope(prs)                 # 4
    slide_data(prs)                  # 5
    slide_methods(prs)               # 6
    slide_findings_map(prs)          # 7

    # 8–13: one figure per finding
    _figure_slide(prs, 8, "04  ·  KEY FINDINGS 1/6",
                  "The monsoon dominates the rainfall year — everywhere",
                  "fig1_seasonality.png",
                  [("73.7%", "national Jun–Sep share", "882 mm of the 1,197 mm rainfall year", WHITE),
                   ("67.8–80.3%", "divisional share range", "even the least monsoonal division gets two-thirds in Jun–Sep", ACCENT),
                   ("η² = 0.51", "variance explained by season", "one-way ANOVA F = 5,785.6, p < 0.001", GREEN)],
                  note="Figure: fig1_seasonality.png — national seasonal means (A) and per-division monsoon share (B).")

    _figure_slide(prs, 9, "04  ·  KEY FINDINGS 2/6",
                  "Regions differ enormously — in amount and in reliability",
                  "fig2_regional_variability.png",
                  [("24×", "mean annual range", "Ladakh 148 mm → Konkan & Goa 3,511 mm", WHITE),
                   ("CV 13.6–70.3%", "reliability range", "Kerala steadiest; Ladakh least reliable", ACCENT, 16.5),
                   ("η² = 0.861", "variance explained by region", "Welch ANOVA F(35,1445) = 588.5, p < 0.001", GREEN),
                   ("Levene p ≈ 10⁻¹⁶¹", "equal variances rejected", "so inference rests on Welch, not ordinary ANOVA", AMBER, 16.5)],
                  img_width=19.0, card_y=14.6, card_h=3.7,
                  note="Figure: fig2_regional_variability.png — means coloured by CV (A) and CV ranking (B).")

    _figure_slide(prs, 10, "04  ·  KEY FINDINGS 3/6",
                  "Pooled totals are right-skewed — Normal is the wrong default",
                  "fig4_distribution_fits.png",
                  [("KS D = 0.185", "Normal fit (pooled JAS)", "Shapiro–Wilk p ≈ 10⁻⁵⁵ — normality rejected", RED),
                   ("KS D = 0.069", "Lognormal fit (best pooled)", "Gamma 0.094 — both far better than Normal", GREEN),
                   ("33 / 36", "divisions near-normal within", "pooled skew is a between-region scale mixture", AMBER)],
                  note="Figure: fig4_distribution_fits.png — model choice depends on the unit of analysis.")

    _figure_slide(prs, 11, "04  ·  KEY FINDINGS 4/6",
                  "Trend claims evaporate under correction",
                  "fig5_trends.png",
                  [("3 → 0", "significant after BH (5% FDR)", "smallest adjusted q = 0.44", RED),
                   ("−34 mm", "national trend per century", "95% CI [−117, +49] — contains zero (p = 0.42)", WHITE),
                   ("36 / 36", "OLS & Mann–Kendall sign agreement", "rank-based check confirms the OLS picture", ACCENT),
                   ("p = 0.75", "two-era test (1950–80 vs 1981–2015)", "−11.5 mm (−0.96%) — no era shift", MUTED)],
                  note="Figure: fig5_trends.png — a null result, reported as a result.")

    _figure_slide(prs, 12, "04  ·  KEY FINDINGS 5/6",
                  "Drought risk is intensely local",
                  "fig6_drought.png",
                  [("15.8%", "1-in-20-yr level, W Rajasthan", "a ~50 mm year against a 317 mm normal", RED),
                   ("77.8%", "1-in-20-yr level, Kerala", "the steadiest division barely dips", GREEN),
                   ("31 / 115", "national years below 90% of normal", "clustered in epochs: 1918–29, 1950–58, 1979–86, 2009–15", AMBER),
                   ("0", "national years below 75%", "severe deficits are divisional, never all-India", WHITE)],
                  note="Figure: fig6_drought.png — national deficit years (A) and per-division 1-in-20-year levels (B).")

    # fig7 is portrait-ish: figure left, cards right
    slide = _slide(prs)
    _section_label(slide, "04  ·  KEY FINDINGS 6/6", top_offset=MARGIN_L)
    _heading(slide, "Divisions share weather — independence is violated", top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)
    _add_figure(slide, "fig7_correlation_heatmap.png", 4.2, 13.4, left_cm=1.6)
    cards7 = [
        ("mean r = 0.243", "across 630 division pairs", "range −0.15 to 0.74", WHITE),
        ("64.9%", "pairs significant at 5%", "|r| > 0.183 for n = 115", AMBER),
        ("36 ≠ 36", "independent samples", "borderline p-values are weaker evidence than they look", RED),
    ]
    for i, (v, l, s, c) in enumerate(cards7):
        _stat_card(slide, emu(17.1), emu(4.4 + i * 4.0), emu(15.2), emu(3.6), v, l, s, c)
    _add_textbox(slide, emu(17.1), emu(16.6), emu(15.2), emu(1.4),
                 "Headline conclusions therefore rest on large effects (η² = 0.86, share = 73.7%) — not on borderline p-values.",
                 9, italic=True, color=MUTED, wrap=True)
    _footer(slide, 13)

    # 14: UPDATE — the missing decade, recovered (observed IMD data 2015-2026)
    _figure_slide(prs, 14, "04  ·  UPDATE — THE MISSING DECADE, RECOVERED",
                  "Official IMD data 2015–2026 acquired, validated — and it confirms the verdict",
                  "fig8_extended_national_series.png",
                  [("−18 mm", "observed annual trend per century", "1901–2025, p = 0.50 — null verdict holds on real data", WHITE),
                   ("+0.7%", "monsoon, 2016–2025 vs 1901–2015", "1,186 vs 1,180 mm — no decade shift (Welch p = 0.84)", GREEN),
                   ("−12.6%", "live 2026 monsoon deficit", "759 mm Jun–Sep — a deficit year happening now", RED),
                   ("±75%", "recent subdivision extremes", "Saurashtra & Kutch +75% (2024); Kerala −34% in two years", AMBER, 17)],
                  note="Source: IMD Annual Climate Summaries + CMPG live tables — fetched & validated by scripts/data/fetch_observed.py (1,800 cells, 0 check failures).")

    # 14: limitations & verdict
    slide = _slide(prs)
    _section_label(slide, "05  ·  VERDICT & LIMITATIONS", top_offset=MARGIN_L)
    _heading(slide, "What the data cannot say — and the feasibility verdict", top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    _add_rect(slide, MARGIN_L, emu(4.0), emu(15.4), emu(11.2), CARD_BG)
    _add_rect(slide, MARGIN_L, emu(4.0), emu(15.4), emu(0.22), RED)
    _add_textbox(slide, MARGIN_L + emu(0.3), emu(4.4), emu(15.0), emu(0.65),
                 "LIMITATIONS", 9, bold=True, color=RED)
    lims = [
        "Pipeline layer is IMD-calibrated but generated — tail behaviour and trend strength re-validated on the observed layer (§5.7)",
        "2020's subdivision table is not machine-verifiable (IMD 'real time' values) — excluded by an automated quality gate",
        "2026 annual totals incomplete (year in progress; monsoon complete at −12.6%)",
        "Subdivision + monthly resolution — no district detail, no daily extremes",
        "A 125-year linear slope is a crude summary of a record with wet/dry epochs",
    ]
    for i, t in enumerate(lims):
        _add_textbox(slide, MARGIN_L + emu(0.3), emu(5.25) + i * emu(1.95), emu(14.8), emu(1.9),
                     "▸  " + t, 9, color=MUTED, wrap=True)

    _add_rect(slide, MARGIN_L + emu(16.1), emu(4.0), emu(16.2), emu(11.2), CARD_BG)
    _add_rect(slide, MARGIN_L + emu(16.1), emu(4.0), emu(16.2), emu(0.22), GREEN)
    _add_textbox(slide, MARGIN_L + emu(16.4), emu(4.4), emu(15.8), emu(0.65),
                 "FEASIBILITY VERDICT", 9, bold=True, color=GREEN)
    verdict = [
        ("Data sufficient?", "Yes — pipeline + observed IMD layer to 2026"),
        ("Methods appropriate & reproducible?", "Yes — every layer regenerates from scripts"),
        ("Risks identified?", "Yes — provenance documented; 2020 gap flagged"),
        ("Overall", "FEASIBLE — top next step (post-2015 data) COMPLETED"),
    ]
    for j, (q, a) in enumerate(verdict):
        yy = emu(5.3) + j * emu(2.45)
        _add_textbox(slide, MARGIN_L + emu(16.4), yy, emu(15.8), emu(0.6),
                     q, 9.5, bold=True, color=AMBER)
        _add_textbox(slide, MARGIN_L + emu(16.4), yy + emu(0.62), emu(15.8), emu(1.5),
                     a, 9.5, color=WHITE if j < 3 else GREEN, bold=(j == 3), wrap=True)
    _footer(slide, 15)

    # 15: recommendation
    slide = _slide(prs)
    _section_label(slide, "05  ·  RECOMMENDATION", top_offset=MARGIN_L)
    _heading(slide, "Continue — with data replacement, not method change", top_offset=emu(1.7), size=22)
    _add_rule(slide, MARGIN_L, emu(3.5), W - 2 * MARGIN_L)

    recs = [
        ("1", "Keep the pipeline & dashboard", "Methods are sound; every figure regenerates from scripts.", GREEN),
        ("2", "Post-2015 data acquisition — DONE", "Observed IMD layer 2015-2026 fetched, validated (1,800 cells, 0 failures) and analysed.", GREEN),
        ("3", "Complete the observed record", "Obtain the verifiable 2020 subdivision table (IMD request); re-run the division-level pipeline on the combined 1901-2025 observed record.", ACCENT),
        ("4", "Then widen: districts + ENSO/IOD", "Finer risk mapping; Pearson r and lagged cross-correlation against Niño 3.4.", MUTED),
    ]
    for i, (num, title, body, col) in enumerate(recs):
        y = emu(4.0) + i * emu(2.15)
        _add_rect(slide, MARGIN_L, y, W - 2 * MARGIN_L, emu(1.9), CARD_BG)
        _add_rect(slide, MARGIN_L, y, emu(0.18), emu(1.9), col)
        _add_textbox(slide, MARGIN_L + emu(0.5), y + emu(0.4), emu(1.2), emu(0.9),
                     num, 16, bold=True, color=col)
        _add_textbox(slide, MARGIN_L + emu(1.9), y + emu(0.16), emu(28.5), emu(0.7),
                     title, 12, bold=True, color=WHITE)
        _add_textbox(slide, MARGIN_L + emu(1.9), y + emu(0.88), emu(28.5), emu(0.9),
                     body, 9.5, color=MUTED, wrap=True)

    _add_rect(slide, MARGIN_L, emu(13.0), W - 2 * MARGIN_L, emu(3.4), CARD_BG)
    _add_textbox(slide, MARGIN_L + emu(0.35), emu(13.3), emu(30.0), emu(0.65),
                 "WHAT WE LEARNED", 9, bold=True, color=AMBER)
    _add_textbox(slide, MARGIN_L + emu(0.35), emu(14.0), emu(30.5), emu(2.2),
                 "Testing 36 divisions is one experiment, not 36. Assumption checks (Levene, Shapiro–Wilk) "
                 "decided which tests we were allowed to use. And a null trend result is still a result — "
                 "we report it rather than shop for significance.",
                 10, color=MUTED, wrap=True)
    _footer(slide, 16)

    # 17: summary
    slide = _slide(prs)
    _section_label(slide, "SUMMARY", top_offset=MARGIN_L)
    _heading(slide, "Five things the data tells us", top_offset=emu(1.7), size=26)
    _add_rule(slide, MARGIN_L, emu(3.6), W - 2 * MARGIN_L)

    items = [
        ("1", "Rain is concentrated", "73.7% falls in Jun–Sep; season explains 51% of variance.", ACCENT),
        ("2", "Regions differ sharply", "Region explains 86.1% of variance; CV runs 13.6% → 70.3%.", GREEN),
        ("3", "Model choice depends on scale", "Pooled totals need Gamma/Lognormal; within a division, Normal suffices.", AMBER),
        ("4", "Trends need caution — and honesty", "3 of 36 raw trends fall to 0 after BH; national CI spans zero.", RED),
        ("5", "Drought risk is local", "A 1-in-20-year year means 15.8% of normal in W Rajasthan, 77.8% in Kerala.", ACCENT),
    ]
    for i, (num, head, body, col) in enumerate(items):
        y = emu(4.3) + i * emu(2.15)
        _add_rect(slide, MARGIN_L, y, emu(1.7), emu(1.7), CARD_BG)
        _add_textbox(slide, MARGIN_L + emu(0.15), y + emu(0.3), emu(1.4), emu(1.0),
                     num, 17, bold=True, color=col, align=PP_ALIGN.CENTER)
        _add_textbox(slide, MARGIN_L + emu(2.2), y + emu(0.05), emu(28.0), emu(0.75),
                     head, 13, bold=True, color=WHITE)
        _add_textbox(slide, MARGIN_L + emu(2.2), y + emu(0.85), emu(28.0), emu(0.75),
                     body, 10.5, color=MUTED)
    _footer(slide, 17)

    # 18: closing
    slide = _slide(prs)
    _add_textbox(slide, MARGIN_L, emu(5.0), emu(31), emu(2.6),
                 "VARSA turns 115 years of rainfall into statistically defensible findings —",
                 24, bold=True, color=WHITE)
    _add_textbox(slide, MARGIN_L, emu(7.6), emu(31), emu(1.2),
                 "every figure, test and p-value reproducible from one command.",
                 24, bold=True, color=AMBER)
    _add_rule(slide, MARGIN_L, emu(9.9), W - 2 * MARGIN_L)
    _add_textbox(slide, MARGIN_L, emu(10.7), emu(31), emu(1.0),
                 "Questions welcome", 18, bold=True, color=WHITE)
    _add_textbox(slide, MARGIN_L, emu(12.6), emu(31), emu(0.8),
                 "Pratik (25BCE0337)  ·  Adarsh (25BCE0401)  ·  Arunya (25BCE0344)",
                 11.5, color=MUTED)
    _add_textbox(slide, MARGIN_L, emu(13.5), emu(31), emu(0.8),
                 "Dr. Juhi Baroi  ·  Probability and Statistics (BAMAT207)",
                 11.5, color=MUTED)
    _add_textbox(slide, MARGIN_L, emu(14.8), emu(31), emu(0.8),
                 "Report: review_3/final_report.md  ·  Pipeline: scripts/final_analysis.py  ·  Dashboard: streamlit run app.py",
                 9.5, color=MUTED)

    out = BASE / "VARSA_Review_3.pptx"
    prs.save(str(out))
    print(f"Saved {out} ({len(prs.slides._sldIdLst)} slides)")


if __name__ == "__main__":
    build()
