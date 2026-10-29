#!/usr/bin/env python3
"""
Generate VARSA_Final_Review.pptx — Final Capstone Review & Project Defense.
Crafted for easy, intuitive explanation to non-technical evaluators and professors,
while retaining 100% statistical rigor under the hood.

Includes:
- Reduced white heading font size (17-18pt) with generous vertical breathing room
  so it never visually merges or crowds into the amber category tag above it.
- Generous paragraph spacing (7pt space_after on category tag + 4pt space_before on heading).
- Layman-friendly explanations and intuitive analogies on every slide.
- Fixed image layout for Slide 15 (fig9_observed_departures.png side-by-side layout).
- Clean unified headers with zero collision or overlapping text.
- Clear takeaway callouts on every finding.

Run:
    python scripts/make_final_review_ppt.py
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
OBS = json.loads((R3 / "observed_results.json").read_text()) if (R3 / "observed_results.json").exists() else {}

# ── Palette (Professional Navy & Warm Amber) ──────────────────────────────────
BG_DARK = RGBColor(0x0B, 0x14, 0x28)
AMBER = RGBColor(0xE0, 0xA5, 0x26)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0xC9, 0xD6, 0xEA)
ACCENT = RGBColor(0x38, 0xBD, 0xF8)
GREEN = RGBColor(0x22, 0xC5, 0x5E)
RED = RGBColor(0xF8, 0x71, 0x71)
CARD_BG = RGBColor(0x0F, 0x20, 0x40)
CARD_BG_LIGHT = RGBColor(0x15, 0x2A, 0x52)
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


def _header(slide, section_text, heading_text, subtitle_text=None, size=17.5):
    """
    Unified header block with reduced heading font and generous vertical spacing:
    - Amber category tag (8pt bold) with 7pt bottom space
    - Clean white heading (17-18pt bold) with 4pt top space -> 11pt total margin!
    - Subtitle (9pt italic) with 3pt top space
    Guaranteed clean separation with zero crowding or merging across all slides.
    """
    txb = slide.shapes.add_textbox(MARGIN_L, emu(0.68), W - 2 * MARGIN_L, emu(2.3))
    tf = txb.text_frame
    tf.word_wrap = True
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.margin_left = 0
    tf.margin_right = 0

    if section_text:
        p1 = tf.paragraphs[0]
        p1.space_after = Pt(7)  # Generous gap after amber category tag
        run1 = p1.add_run()
        run1.text = section_text.strip().upper()
        run1.font.size = Pt(8.0)
        run1.font.bold = True
        run1.font.color.rgb = AMBER
        try:
            run1.font.name = "Outfit"
        except Exception:
            pass

        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)  # Extra spacing before heading to completely prevent visual merging
    else:
        p2 = tf.paragraphs[0]

    run2 = p2.add_run()
    run2.text = heading_text.strip()
    run2.font.size = Pt(size)  # Reduced from 21-24pt to 17.5pt for clean, elegant proportions
    run2.font.bold = True
    run2.font.color.rgb = WHITE
    try:
        run2.font.name = "Outfit"
    except Exception:
        pass

    if subtitle_text:
        p3 = tf.add_paragraph()
        p3.space_before = Pt(3)
        run3 = p3.add_run()
        run3.text = subtitle_text.strip()
        run3.font.size = Pt(9.0)
        run3.font.italic = True
        run3.font.color.rgb = MUTED
        try:
            run3.font.name = "Outfit"
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


def _footer(slide, page_num, total_pages=20):
    _add_rect(slide, 0, H - emu(0.8), W, emu(0.8), CARD_BG)
    _add_textbox(slide, MARGIN_L, H - emu(0.72), emu(16), emu(0.6),
                 "VARSA  ·  Final Project Review & Defense  ·  Probability & Statistics (BAMAT207)", 7.5, color=MUTED)
    _add_textbox(slide, W - emu(3.5), H - emu(0.72), emu(3.0), emu(0.6),
                 f"{page_num} / {total_pages}", 7.5, color=MUTED, align=PP_ALIGN.RIGHT)


def _slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_bg(slide, BG_DARK)
    return slide


def _stat_card(slide, x, y, w, h, value, label, sub, color=WHITE, value_size=18):
    _add_rect(slide, x, y, w, h, CARD_BG)
    _add_textbox(slide, x + emu(0.35), y + emu(0.22), w - emu(0.5), emu(1.2),
                 value, value_size, bold=True, color=color)
    _add_textbox(slide, x + emu(0.35), y + emu(1.45), w - emu(0.5), emu(0.55),
                 label, 8.5, bold=True, color=AMBER)
    _add_textbox(slide, x + emu(0.35), y + emu(2.05), w - emu(0.5), emu(h / 360000 - 2.1),
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


def _landscape_figure_slide(prs, page, section, heading, fig_name, cards,
                            subtitle=None, img_width=19.5, card_y=13.8, card_h=3.6, note=None):
    """Layout for wide landscape figures: image centered, stat cards below."""
    slide = _slide(prs)
    _header(slide, section, heading, subtitle_text=subtitle, size=17.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    _add_figure(slide, fig_name, 3.3, img_width)

    n = len(cards)
    gap = emu(0.35)
    card_w = (W - 2 * MARGIN_L - (n - 1) * gap) // n
    for i, c in enumerate(cards):
        val, lbl, sub = c[0], c[1], c[2]
        col = c[3] if len(c) > 3 else WHITE
        vsize = c[4] if len(c) > 4 else 18
        x = MARGIN_L + i * (card_w + gap)
        _stat_card(slide, x, emu(card_y), card_w, emu(card_h),
                   val, lbl, sub, color=col, value_size=vsize)
    if note:
        _add_textbox(slide, MARGIN_L, emu(SLIDE_H_CM - 1.45), W - 2 * MARGIN_L, emu(0.6),
                     note, 9.0, italic=True, color=MUTED)
    _footer(slide, page)
    return slide


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1: COVER
# ══════════════════════════════════════════════════════════════════════════════
def slide_cover(prs):
    slide = _slide(prs)
    _add_rect(slide, MARGIN_L, emu(1.3), emu(14.5), emu(0.65), CARD_BG)
    _add_textbox(slide, MARGIN_L + emu(0.3), emu(1.4), emu(14.0), emu(0.5),
                 "PROBABILITY & STATISTICS  ·  FINAL CAPSTONE PROJECT DEFENSE",
                 8.5, bold=True, color=AMBER)

    _add_textbox(slide, MARGIN_L, emu(2.7), emu(31.0), emu(2.0),
                 "VARSA: Understanding India's Rainfall",
                 34, bold=True, color=WHITE)
    _add_textbox(slide, MARGIN_L, emu(4.8), emu(31.0), emu(1.4),
                 "A 126-Year Statistical Journey (1901–2026): Myths, Realities & Interactive Atlas",
                 15, color=MUTED)

    _add_rule(slide, MARGIN_L, emu(6.8), W - 2 * MARGIN_L, AMBER)

    # 4 Quick Talking Points for the Professor
    metrics = [
        ("126 Years", "Complete History", "From British records (1901) to live monsoon 2026", ACCENT),
        ("36 Regions", "All of India", "Every meteorological subdivision analyzed individually", GREEN),
        ("0 Myths", "Truth in Data", "Common misconceptions tested with mathematical rigor", AMBER),
        ("Live & 3D", "Interactive Tools", "Web dashboard + 3D atlas anyone can explore", WHITE),
    ]
    card_w = (W - 2 * MARGIN_L - 3 * emu(0.4)) // 4
    for i, (v, l, s, c) in enumerate(metrics):
        x = MARGIN_L + i * (card_w + emu(0.4))
        _stat_card(slide, x, emu(7.6), card_w, emu(4.2), v, l, s, color=c, value_size=20)

    # Team & Faculty Box
    _add_rect(slide, MARGIN_L, emu(12.7), W - 2 * MARGIN_L, emu(4.2), CARD_BG)
    _add_textbox(slide, MARGIN_L + emu(0.6), emu(13.0), emu(14.0), emu(0.6),
                 "PROJECT TEAM", 9, bold=True, color=AMBER)
    _add_textbox(slide, MARGIN_L + emu(0.6), emu(13.7), emu(16.0), emu(2.6),
                 "• Pratik  (25BCE0337)\n• Adarsh  (25BCE0401)\n• Arunya  (25BCE0344)",
                 11, bold=True, color=WHITE)

    _add_textbox(slide, MARGIN_L + emu(16.5), emu(13.0), emu(14.0), emu(0.6),
                 "COURSE & FACULTY GUIDANCE", 9, bold=True, color=AMBER)
    _add_textbox(slide, MARGIN_L + emu(16.5), emu(13.7), emu(14.0), emu(2.6),
                 "Dr. Juhi Baroi\nProbability and Statistics (BAMAT207)\nSchool of Computer Science & Engineering",
                 11, color=MUTED)

    _footer(slide, 1)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2: EXECUTIVE SUMMARY (PLAIN ENGLISH)
# ══════════════════════════════════════════════════════════════════════════════
def slide_summary(prs):
    slide = _slide(prs)
    _header(slide, "EXECUTIVE SUMMARY", "The Big Questions & What We Discovered",
            subtitle_text="In simple words: what we set out to do, what we proved, and what we built.",
            size=18.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    cards = [
        ("1. Is India's Monsoon Decreasing?",
         "Common belief says India is rapidly drying up. But across 125 continuous years of official data, "
         "the national trend is virtually zero (-18 mm/century, p=0.50). Rainfall fluctuates in cycles, but the total volume remains steady.",
         ACCENT),
        ("2. Why 'National Averages' Are Misleading",
         "India is not one climate. 86% of rainfall differences come down to geography alone. "
         "Ladakh gets 148 mm while Konkan gets 3,500 mm. You cannot manage India's water with one nationwide number.",
         GREEN),
        ("3. Recovering the 'Missing Decade'",
         "Most public datasets abruptly end in 2015. We downloaded and parsed official IMD annual climate summaries (2015–2026), "
         "recovering 10 modern years and validating every single cell against printed departures.",
         AMBER),
        ("4. Interactive Tools for Everyone",
         "Rather than hiding results in a static document, we built a point-and-click Streamlit dashboard and a "
         "zero-lag 3D Prism Atlas on Vercel so any teacher, researcher, or student can visually inspect 126 years of rainfall.",
         WHITE),
    ]

    card_w = (W - 2 * MARGIN_L - emu(0.6)) // 2
    for i, (title, desc, col) in enumerate(cards):
        row = i // 2
        col_idx = i % 2
        x = MARGIN_L + col_idx * (card_w + emu(0.6))
        y = emu(3.6) + row * emu(5.2)

        _add_rect(slide, x, y, card_w, emu(4.7), CARD_BG)
        _add_rect(slide, x, y, emu(0.2), emu(4.7), col)
        _add_textbox(slide, x + emu(0.6), y + emu(0.4), card_w - emu(1.0), emu(0.8),
                     title, 13, bold=True, color=col)
        _add_textbox(slide, x + emu(0.6), y + emu(1.3), card_w - emu(1.2), emu(3.0),
                     desc, 10.2, color=MUTED, wrap=True)

    _add_textbox(slide, MARGIN_L, emu(14.8), W - 2 * MARGIN_L, emu(1.8),
                 "★ Takeaway: VARSA turns complex probability principles into clear, undeniable facts backed by 126 years of evidence.",
                 11, bold=True, color=AMBER)
    _footer(slide, 2)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3: EVOLUTION ACROSS REVIEWS
# ══════════════════════════════════════════════════════════════════════════════
def slide_evolution(prs):
    slide = _slide(prs)
    _header(slide, "01  ·  PROJECT TRAJECTORY", "Our Journey Across the Three Reviews",
            subtitle_text="How a simple classroom project evolved into an end-to-end meteorological system.",
            size=18.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    phases = [
        ("REVIEW 1", "Curiosity & Questions",
         ["Asked 6 foundational questions",
          "Audited raw public government data",
          "Noticed huge differences between states",
          "Realized naive testing leads to false alarms"],
         MUTED),
        ("REVIEW 2", "Hitting Roadblocks & Adapting",
         ["Found public data ended in 2015",
          "Proved ordinary textbook tests fail on India",
          "Learned that states have unequal variances",
          "Created our first rough dashboard prototype"],
         AMBER),
        ("REVIEW 3", "Mathematical Discovery",
         ["Ran full hypothesis tests on 115 years",
          "Busted the secular trend myth with 7 figures",
          "Scraped & parsed the missing 2015-2025 records",
          "Proved long-term stability holds on real data"],
         ACCENT),
        ("FINAL REVIEW", "Unification & Production",
         ["Integrated 1901-2026 into every screen",
          "Passed all 9 automated data safety checks",
          "Deployed live to the cloud (Streamlit & Vercel)",
          "Created a simple, robust final defense"],
         GREEN),
    ]

    card_w = (W - 2 * MARGIN_L - 3 * emu(0.4)) // 4
    for i, (rev, title, bullets, col) in enumerate(phases):
        x = MARGIN_L + i * (card_w + emu(0.4))
        y = emu(3.6)

        _add_rect(slide, x, y, card_w, emu(11.5), CARD_BG)
        _add_rect(slide, x, y, card_w, emu(0.2), col)

        _add_textbox(slide, x + emu(0.4), y + emu(0.4), card_w - emu(0.8), emu(0.6),
                     rev, 13, bold=True, color=col)
        _add_textbox(slide, x + emu(0.4), y + emu(1.1), card_w - emu(0.8), emu(1.0),
                     title, 10, bold=True, color=WHITE)
        _add_rule(slide, x + emu(0.4), y + emu(2.2), card_w - emu(0.8), DIVIDER)

        for b_idx, b in enumerate(bullets):
            by = y + emu(2.5) + b_idx * emu(2.1)
            _add_textbox(slide, x + emu(0.4), by, card_w - emu(0.8), emu(1.9),
                         f"▸ {b}", 9.2, color=MUTED, wrap=True)

    _footer(slide, 3)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4: MAJOR ACCOMPLISHMENTS SINCE REVIEW 3
# ══════════════════════════════════════════════════════════════════════════════
def slide_accomplishments(prs):
    slide = _slide(prs)
    _header(slide, "02  ·  RECENT PROGRESS", "What We Built and Polished for the Final Review",
            subtitle_text="The big upgrades that brought everything together into a polished capstone.",
            size=18.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    items = [
        ("Modern Data in Every Single View",
         "Earlier, our recent 2015-2025 data sat in separate test scripts. Now, when you pick any state or slide the year timeline in our app, you seamlessly explore 1901 right through 2026 with clear color-coded badges.",
         GREEN),
        ("Automated 'Zero-Hallucination' Test Suite",
         "We wrote an automated test script with 9 safety checks (T1–T9). It re-verifies every single math calculation and departure percentage to prove that zero records are fabricated or mislabeled.",
         ACCENT),
        ("Live Web Deployments (Zero Setup Required)",
         "Our teacher or classmates can open our project on any phone, tablet, or laptop right now. The analytical app runs on Streamlit Cloud, and our interactive 3D map runs on Vercel with zero installation.",
         AMBER),
        ("Responsible Data Handling (No Silent Errors)",
         "When official IMD 2020 tables had broken text scanning in their PDF report, we did not guess or fake numbers. We built an automatic gate that rejected the broken year and flagged it transparently.",
         RED),
    ]

    card_w = (W - 2 * MARGIN_L - emu(0.5)) // 2
    for i, (title, body, col) in enumerate(items):
        row = i // 2
        c_idx = i % 2
        x = MARGIN_L + c_idx * (card_w + emu(0.5))
        y = emu(3.6) + row * emu(5.3)

        _add_rect(slide, x, y, card_w, emu(4.8), CARD_BG)
        _add_rect(slide, x, y, emu(0.2), emu(4.8), col)
        _add_textbox(slide, x + emu(0.5), y + emu(0.35), card_w - emu(0.9), emu(0.8),
                     title, 12, bold=True, color=WHITE)
        _add_textbox(slide, x + emu(0.5), y + emu(1.3), card_w - emu(1.0), emu(3.2),
                     body, 9.8, color=MUTED, wrap=True)

    _footer(slide, 4)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5: DATA ARCHITECTURE (EASY TO EXPLAIN)
# ══════════════════════════════════════════════════════════════════════════════
def slide_data_architecture(prs):
    slide = _slide(prs)
    _header(slide, "03  ·  DATA LAYERS", "How Our 126 Years of Data Is Organized",
            subtitle_text="Combining colonial records, modern government publications, and live monsoon updates.",
            size=18.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    layers = [
        ("Layer 1: The Historical Record",
         "1901–2015 (115 Years)",
         "A century of meteorological records",
         "• 20,700 data points across 36 subdivisions\n"
         "• Provides the baseline 'normal' rainfall for each state\n"
         "• Allows us to study multi-decade climate cycles\n"
         "• Cleaned, standardized, and 100% complete",
         ACCENT),
        ("Layer 2: The Modern Decade",
         "2015–2025 (10 Validated Years)",
         "Recovered from IMD Climate Reports",
         "• Extracted from official Annual Climate Summaries\n"
         "• 1,800 validated data points across 3 distinct PDF formats\n"
         "• Every cell double-checked against printed IMD departures\n"
         "• Gives us an up-to-date picture of recent weather",
         GREEN),
        ("Layer 3: Live All-India Monsoon",
         "1901–2026 (Live Current Season)",
         "National series updated to present day",
         "• Official CMPG long-term national rainfall series\n"
         "• Includes the live 2026 monsoon (759.4 mm, -12.6%)\n"
         "• Kept strictly provisional so incomplete years don't distort\n"
         "• Connects past history directly to today's news",
         AMBER),
    ]

    card_w = (W - 2 * MARGIN_L - 2 * emu(0.4)) // 3
    for i, (title, span, path, details, col) in enumerate(layers):
        x = MARGIN_L + i * (card_w + emu(0.4))
        y = emu(3.6)

        _add_rect(slide, x, y, card_w, emu(11.5), CARD_BG)
        _add_rect(slide, x, y, card_w, emu(0.2), col)

        _add_textbox(slide, x + emu(0.4), y + emu(0.4), card_w - emu(0.8), emu(0.6),
                     title, 12, bold=True, color=WHITE)
        _add_textbox(slide, x + emu(0.4), y + emu(1.0), card_w - emu(0.8), emu(0.5),
                     span, 10, bold=True, color=col)
        _add_textbox(slide, x + emu(0.4), y + emu(1.5), card_w - emu(0.8), emu(0.5),
                     path, 8, italic=True, color=MUTED)
        _add_rule(slide, x + emu(0.4), y + emu(2.2), card_w - emu(0.8), DIVIDER)

        _add_textbox(slide, x + emu(0.4), y + emu(2.5), card_w - emu(0.8), emu(8.5),
                     details, 9.5, color=MUTED, wrap=True)

    _footer(slide, 5)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6: QUALITY ASSURANCE (SIMPLE WORDS)
# ══════════════════════════════════════════════════════════════════════════════
def slide_qa_suite(prs):
    slide = _slide(prs)
    _header(slide, "04  ·  TRUST & QUALITY", "How We Ensured Every Number Is 100% Genuine",
            subtitle_text="We wrote an automated test script that runs 9 safety checks before any graph is drawn.",
            size=18.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    tests = [
        ("1. All 36 Regions Accounted For", "Verified that every single official region from Kashmir to Kerala is present without omission.", GREEN),
        ("2. Double-Checked the Math", "Checked that (Actual Rain / Normal Rain - 1) matches IMD's official departure percentage on all 1,800 cells.", GREEN),
        ("3. Clear Labeling on Every Row", "Every single row tells the user whether it came from the historical archive or the newly parsed modern decade.", GREEN),
        ("4. Winter Definitions Handled Fairly", "IMD redefined Winter in modern tables (Jan-Feb vs Dec-Feb). We flag this so seasons aren't mixed improperly.", GREEN),
        ("5. 125-Year Timeline Kept Intact", "Verified continuous annual data from 1901 to 2025 without a single missing year in the national record.", GREEN),
        ("6. Incomplete Years Never Mixed In", "Because 2026 is still underway, its monsoon rain is kept separate and not counted as a full year total.", GREEN),
        ("7. 3D Web Map Numbers Matched", "Guaranteed that the numbers rendered on the 3D globe match our statistical analysis exactly.", GREEN),
        ("8. National Trends Confirmed", "Verified that historical charts and modern trend lines connect smoothly without sudden artificial jumps.", GREEN),
        ("9. Zero Fabricated Rows", "Checked that total row counts match the exact number of published government tables. No fake data.", GREEN),
    ]

    card_w = (W - 2 * MARGIN_L - 2 * emu(0.4)) // 3
    for i, (name, desc, col) in enumerate(tests):
        row = i // 3
        c_idx = i % 3
        x = MARGIN_L + c_idx * (card_w + emu(0.4))
        y = emu(3.6) + row * emu(3.6)

        _add_rect(slide, x, y, card_w, emu(3.2), CARD_BG)
        _add_rect(slide, x, y, emu(0.18), emu(3.2), col)

        _add_textbox(slide, x + emu(0.4), y + emu(0.25), card_w - emu(0.7), emu(0.6),
                     f"✓ {name}", 10.5, bold=True, color=WHITE)
        _add_textbox(slide, x + emu(0.4), y + emu(0.95), card_w - emu(0.7), emu(2.0),
                     desc, 9.0, color=MUTED, wrap=True)

    _add_textbox(slide, MARGIN_L, emu(15.2), W - 2 * MARGIN_L, emu(0.6),
                 "Talking Point: 'We don't ask you to trust our word — any evaluator can run our test script in 2 seconds to verify every claim.'",
                 10, bold=True, color=AMBER)
    _footer(slide, 6)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7: KEY FINDINGS MAP (LAYMAN SUMMARY)
# ══════════════════════════════════════════════════════════════════════════════
def slide_findings_map(prs):
    slide = _slide(prs)
    _header(slide, "05  ·  THE SIX DISCOVERIES", "Six Common Beliefs vs What the Data Proves",
            subtitle_text="The core conclusions of our project, presented in simple, plain English.",
            size=18.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    claims = [
        ("1", "The 4-Month Floodgate", "Belief: Rain is spread through the year. Fact: 74% falls in just 120 days of monsoon across every corner of India.", ACCENT),
        ("2", "Two Completely Different Indias", "Belief: India has a single average rainfall. Fact: Geography causes a 24× difference from desert (148 mm) to coast (3,500 mm).", GREEN),
        ("3", "The Trap of the 'Normal Curve'", "Belief: Textbook bell curves fit all rainfall. Fact: India has extreme rain-shadows; forcing a bell curve gives wrong probabilities.", AMBER),
        ("4", "Is India Drying Up? Myth Busted", "Belief: Climate change is making total rain disappear. Fact: 125 years show zero secular drying trend (-18 mm/century, p=0.50).", RED),
        ("5", "Drought Is Always Local", "Belief: A bad monsoon ruins the entire country. Fact: Severe drought never hits all of India at once; it strikes specific dry regions.", ACCENT),
        ("6", "Storm Clouds Don't Respect Borders", "Belief: Neighboring states have separate weather. Fact: 65% of regions share monsoon patterns; weather is a shared system.", GREEN),
    ]

    for i, (num, claim, detail, col) in enumerate(claims):
        y = emu(3.5) + i * emu(1.8)
        _add_rect(slide, MARGIN_L, y, W - 2 * MARGIN_L, emu(1.5), CARD_BG)
        _add_rect(slide, MARGIN_L, y, emu(0.18), emu(1.5), col)

        _add_textbox(slide, MARGIN_L + emu(0.5), y + emu(0.3), emu(1.2), emu(0.9),
                     num, 16, bold=True, color=col)
        _add_textbox(slide, MARGIN_L + emu(1.8), y + emu(0.15), emu(20.0), emu(0.7),
                     claim, 12, bold=True, color=WHITE)
        _add_textbox(slide, MARGIN_L + emu(1.8), y + emu(0.8), emu(28.5), emu(0.6),
                     detail, 9.2, color=MUTED)

    _add_textbox(slide, MARGIN_L, emu(15.0), W - 2 * MARGIN_L, emu(0.6),
                 "Let's look at each of these six discoveries with its actual graph from our research.",
                 10, italic=True, color=MUTED)
    _footer(slide, 7)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDES 8–12: FINDINGS 1 TO 5 (LANDSCAPE FIGURES)
# ══════════════════════════════════════════════════════════════════════════════
def build_finding_slides(prs):
    # Finding 1 (fig1)
    _landscape_figure_slide(prs, 8, "05  ·  FINDING 1: SEASONALITY",
                           "The 4-Month Floodgate: 74% of All Rain Falls in Just 120 Days",
                           "fig1_seasonality.png",
                           [("73.7%", "Monsoon Share", "882 mm out of 1,197 mm total arrives Jun–Sep", WHITE),
                            ("68–80%", "Every Region", "Even dry states receive over two-thirds in these 4 months", ACCENT),
                            ("51% Variance", "Season Explains It", "Season alone dictates half the rainfall variation in India", GREEN)],
                           subtitle="Layman translation: India does not have 'rainy days spread out' — it has one giant monsoon window.",
                           note="Talking Point: 'No matter which state you live in, India survives on a 120-day window. Water storage must capture 4 months of rain to last 12.'")

    # Finding 2 (fig2)
    _landscape_figure_slide(prs, 9, "05  ·  FINDING 2: REGIONAL DIVERSITY",
                           "Two Different Indias: A 24× Difference Between Desert and Coast",
                           "fig2_regional_variability.png",
                           [("24× Range", "Rainfall Gap", "Ladakh gets 148 mm while Konkan & Goa gets 3,511 mm", WHITE),
                            ("CV: 14% vs 70%", "Reliability Gap", "Kerala is steady year-to-year; Ladakh is totally erratic", ACCENT, 16),
                            ("86% Variance", "Geography Is King", "Location explains 86% of rainfall differences across India", GREEN),
                            ("Unequal Spread", "Welch ANOVA Test", "Standard textbook tests fail because states have unequal variance", AMBER, 16)],
                           subtitle="Layman translation: An average of 1,200 mm means nothing when one state gets a desert and another gets a deluge.",
                           img_width=18.5, card_y=13.8, card_h=3.6,
                           note="Talking Point: 'Saying India averages 1,200 mm is like saying a person with their head in an oven and feet in an ice bucket is comfortable.'")

    # Finding 3 (fig4)
    _landscape_figure_slide(prs, 10, "05  ·  FINDING 3: DISTRIBUTION FITTING",
                           "The Bell Curve Trap: Why a Single 'Normal' Curve Misleads",
                           "fig4_distribution_fits.png",
                           [("Bell Curve Fails", "Normal Rejected", "A simple symmetric bell curve fails the data decisively (p ≈ 10⁻⁵⁵)", RED, 16),
                            ("Lognormal Wins", "Best Heavy-Tail Fit", "Lognormal & Gamma curves accurately capture rare heavy-rain years", GREEN, 16),
                            ("States Are Normal", "Within Each Division", "Inside a single state, annual totals follow a normal curve", AMBER, 16)],
                           subtitle="Layman translation: India has too many dry regions and extreme wet spots to force into a single symmetric curve.",
                           note="Talking Point: 'When pooling all of India, heavy monsoon surges stretch the curve to the right. We must use Lognormal models for national risk.'")

    # Finding 4 (fig5)
    _landscape_figure_slide(prs, 11, "05  ·  FINDING 4: TRENDS BUSTED",
                           "Is India Drying Up? 125 Years of Data Busts the Secular Trend Myth",
                           "fig5_trends.png",
                           [("3 → 0 Trends", "The 'Lucky Dice' Filter", "3 apparent regional trends vanish under multiple-testing correction", RED, 16),
                            ("-18 mm / Century", "Essentially Zero", "Over 125 years, the national trend line is statistically flat (p = 0.50)", WHITE, 16),
                            ("36 / 36 Agreement", "Double Verification", "Both linear regression and rank-based tests reach the same verdict", ACCENT, 16),
                            ("No Decadal Shift", "Era Comparison", "Comparing 1950–1980 vs 1981–2015 shows virtually identical averages", MUTED, 16)],
                           subtitle="Layman translation: Random chance can make a few states look like they are drying up, but strict math proves long-term stability.",
                           note="Talking Point: 'If you roll 36 dice, someone gets a six. When tested with proper false-alarm filters, India is NOT undergoing secular drying.'")

    # Finding 5 (fig6)
    _landscape_figure_slide(prs, 12, "05  ·  FINDING 5: DROUGHT RISK",
                           "Drought Is Always Local: Severe Deficit Never Covers the Whole Country",
                           "fig6_drought.png",
                           [("15.8% Normal", "W. Rajasthan Worst", "In a 1-in-20-year drought, desert rain collapses to a tiny 50 mm", RED, 16),
                            ("77.8% Normal", "Kerala Worst", "In Kerala, even a 1-in-20-year bad year stays at 78% of normal", GREEN, 16),
                            ("Cyclic Epochs", "Clustered Droughts", "Deficits bunch into historic eras: 1918–29, 1965–72, 1982–87, 2002–09", AMBER, 16),
                            ("Zero Pan-India", "National Safety", "There has never been a year where the entire country dropped below 75%", WHITE, 16)],
                           subtitle="Layman translation: When Rajasthan suffers a harsh drought, southern and eastern India help balance the national grain basket.",
                           note="Talking Point: 'Drought is intense, but geographically contained. India's regional diversity acts as a natural national insurance policy.'")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13: FINDING 6 (SQUARE IMAGE SIDE-BY-SIDE)
# ══════════════════════════════════════════════════════════════════════════════
def slide_finding_6(prs):
    slide = _slide(prs)
    _header(slide, "05  ·  FINDING 6: SHARED SKIES",
            "Rain Clouds Don't Respect State Borders: Weather Is Shared",
            subtitle_text="Layman translation: States do not experience independent weather. Rain depressions travel across multiple states.",
            size=17.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    # Image on Left (Width 13.5 cm, aspect 1.13)
    _add_figure(slide, "fig7_correlation_heatmap.png", 3.3, 13.5, left_cm=1.6)

    # 3 Plain English Cards on Right
    cards = [
        ("Positive Correlation", "Shared Rain Systems", "Neighboring states rise and fall together because monsoon depressions sweep across them.", WHITE),
        ("65% Connected", "Not Independent States", "65% of region pairs show strong correlation — testing 36 states is NOT 36 independent trials.", AMBER),
        ("Why This Matters", "Avoiding Bad Statistics", "Because states share weather, naive statistical formulas overstate certainty. We accounted for this.", RED),
    ]
    for i, (v, l, s, c) in enumerate(cards):
        _stat_card(slide, emu(16.8), emu(3.6 + i * 3.8), emu(15.4), emu(3.4), v, l, s, c)

    _add_textbox(slide, emu(16.8), emu(15.6), emu(15.4), emu(1.8),
                 "Talking Point: 'When a low-pressure depression forms over the Bay of Bengal, it soaks Odisha, MP, and Gujarat together.'",
                 9.5, bold=True, color=AMBER, wrap=True)
    _footer(slide, 13)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14: EXTENDED RECORD (1901–2026)
# ══════════════════════════════════════════════════════════════════════════════
def slide_observed_verification(prs):
    _landscape_figure_slide(prs, 14, "06  ·  126 YEARS OF EVIDENCE",
                           "125 Years of Real Data (1901–2026) Confirms the Long-Term Verdict",
                           "fig8_extended_national_series.png",
                           [("-18 mm / Century", "125-Year Trend", "From 1901 to 2025, slope is flat (p = 0.50) — verified on real observations", WHITE, 16),
                            ("+0.7% Normal", "Modern Decade", "2016–2025 averaged 1,186 mm vs 1,180 mm historically — zero decade shift", GREEN, 16),
                            ("-12.6% Deficit", "Live 2026 Monsoon", "759 mm Jun–Sep — an ongoing live deficit captured in our system", RED, 16),
                            ("126 Continuous", "Bridging Eras", "Colonial era, Green Revolution, and modern climate era unified in one system", AMBER, 16)],
                           subtitle="Layman translation: We don't have to guess what happened after 2015. Real measurements prove rainfall totals are stable.",
                           note="Talking Point: 'Even with modern climate anxiety, total national monsoon volume has not drifted away from its 100-year average.'")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15: RECENT EXTREMES — SIDE-BY-SIDE LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
def slide_modern_extremes(prs):
    slide = _slide(prs)
    _header(slide, "06  ·  RECENT WILD WEATHER",
            "The True Face of Climate Change: Wild Regional Swings (2015–2025)",
            subtitle_text="Layman translation: While national rain stays steady, regional extremes are getting sharper (floods on one side, dry spells on the other).",
            size=17.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    # Render on the left at width 13.8 cm -> height is 11.10 cm. Fits cleanly from 3.3 cm to 14.4 cm!
    _add_figure(slide, "fig9_observed_departures.png", 3.3, 13.8, left_cm=1.6)

    # 3 High-Impact Cards on the Right
    right_x = emu(16.5)
    card_w = emu(15.8)

    cards = [
        ("+75% Deluge", "Saurashtra & Kutch (2024)",
         "In 2024, western Gujarat was hit by unprecedented monsoon cloudbursts, recording 75% above normal rain.",
         ACCENT),
        ("-34% Deficit", "Kerala Dry Spells (2016 & 2023)",
         "Even Kerala — India's most dependable state — suffered severe consecutive droughts reaching 34% below normal.",
         RED),
        ("Opposite Extremes", "Same Year, Opposite Fate",
         "In almost every recent year, while one state faced flash floods, another faced parched fields. The national total balances out.",
         AMBER),
    ]

    for i, (v, l, s, c) in enumerate(cards):
        y = emu(3.3 + i * 3.6)
        _stat_card(slide, right_x, y, card_w, emu(3.3), v, l, s, color=c, value_size=17)

    # Bottom Callout Box for Evaluator
    _add_rect(slide, right_x, emu(14.5), card_w, emu(2.2), CARD_BG_LIGHT)
    _add_textbox(slide, right_x + emu(0.4), emu(14.7), card_w - emu(0.8), emu(1.8),
                 "Teacher Summary: 'Climate volatility does not show up as a gradual national drying. It shows up as sudden local whiplash between floods and deficits.'",
                 9.5, bold=True, color=GREEN, wrap=True)

    _footer(slide, 15)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 16: STREAMLIT DASHBOARD (INTUITIVE & LIVE)
# ══════════════════════════════════════════════════════════════════════════════
def slide_dashboard(prs):
    slide = _slide(prs)
    _header(slide, "07  ·  INTERACTIVE PLATFORM", "A Point-and-Click Dashboard Anyone Can Use",
            subtitle_text="No programming required: explore all 36 states, time sliders, and risk reports in seconds.",
            size=18.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    features = [
        ("Time Travel Slider (1901–2026)",
         "Move a slider back and forth to inspect any decade in history. Visual tags clearly distinguish historical baseline from modern observed data.",
         ACCENT),
        ("36 Dedicated State Dossiers",
         "Click on any state (e.g., Punjab, Kerala, Bihar) to instantly get its historical bar charts, 10-year wet/dry trends, and drought risks.",
         GREEN),
        ("Color-Coded Drought Warning Matrix",
         "Classifies every state into Green (Safe/Reliable), Yellow (Moderate Risk), or Red (High Drought Risk) based on real recurrence data.",
         AMBER),
        ("Zero-Setup Cloud Access",
         "Hosted live on Streamlit Cloud so teachers and students can open it instantly from any phone or laptop browser without installing Python.",
         WHITE),
    ]

    card_w = (W - 2 * MARGIN_L - emu(0.6)) // 2
    for i, (title, body, col) in enumerate(features):
        row = i // 2
        c_idx = i % 2
        x = MARGIN_L + c_idx * (card_w + emu(0.6))
        y = emu(3.6) + row * emu(5.2)

        _add_rect(slide, x, y, card_w, emu(4.7), CARD_BG)
        _add_rect(slide, x, y, emu(0.2), emu(4.7), col)
        _add_textbox(slide, x + emu(0.6), y + emu(0.4), card_w - emu(1.0), emu(0.8),
                     title, 13, bold=True, color=WHITE)
        _add_textbox(slide, x + emu(0.6), y + emu(1.4), card_w - emu(1.2), emu(3.0),
                     body, 10.2, color=MUTED, wrap=True)

    _add_textbox(slide, MARGIN_L, emu(14.8), W - 2 * MARGIN_L, emu(1.5),
                 "🌐 Live Web Link: https://adarshkumarsingh5732-cpu-my-streamlit-dashboard-app-h5z5y7.streamlit.app/  (or localhost:8501)",
                 11, bold=True, color=ACCENT)
    _footer(slide, 16)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 17: VERCEL 3D PRISM ATLAS (VISUALLY IMPRESSIVE)
# ══════════════════════════════════════════════════════════════════════════════
def slide_vercel_atlas(prs):
    slide = _slide(prs)
    _header(slide, "07  ·  3D VISUAL ATLAS", "3D Rainfall Map: Watching 125 Years Like a Movie",
            subtitle_text="Built with WebGL 3D graphics: prism height shows rainfall, color shows departures from normal.",
            size=18.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    aspects = [
        ("Height = Water Volume",
         "States with heavy rainfall shoot up like tall 3D skyscrapers, while desert regions stay flat. Instantly shows the geographic disparity at a glance.",
         ACCENT),
        ("Color = Good vs Bad Year",
         "Blue and green mean excess rain; yellow, orange, and red mean deficit. A single glance tells you which parts of India suffered in any given year.",
         GREEN),
        ("Smooth 125-Year Playback",
         "Press 'Play' and watch 125 years of Indian monsoon history animate smoothly at 60 frames per second directly in the browser.",
         AMBER),
        ("Instant Static Deployment on Vercel",
         "Deploys directly from GitHub to Vercel's global CDN. Loads in milliseconds without needing a heavy cloud backend.",
         WHITE),
    ]

    card_w = (W - 2 * MARGIN_L - emu(0.6)) // 2
    for i, (title, body, col) in enumerate(aspects):
        row = i // 2
        c_idx = i % 2
        x = MARGIN_L + c_idx * (card_w + emu(0.6))
        y = emu(3.6) + row * emu(5.2)

        _add_rect(slide, x, y, card_w, emu(4.7), CARD_BG)
        _add_rect(slide, x, y, emu(0.2), emu(4.7), col)
        _add_textbox(slide, x + emu(0.6), y + emu(0.4), card_w - emu(1.0), emu(0.8),
                     title, 13, bold=True, color=WHITE)
        _add_textbox(slide, x + emu(0.6), y + emu(1.4), card_w - emu(1.2), emu(3.0),
                     body, 10.2, color=MUTED, wrap=True)

    _add_textbox(slide, MARGIN_L, emu(14.8), W - 2 * MARGIN_L, emu(1.5),
                 "🚀 Static Web URL: https://varsa.vercel.app  (Zero-lag 3D WebGL rendering in any modern browser)",
                 11, bold=True, color=GREEN)
    _footer(slide, 17)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 18: METHODOLOGY & DISCIPLINE (EASY ANALOGIES)
# ══════════════════════════════════════════════════════════════════════════════
def slide_methodology(prs):
    slide = _slide(prs)
    _header(slide, "08  ·  SCIENTIFIC DISCIPLINE", "Four Statistical Traps We Carefully Avoided",
            subtitle_text="Why our conclusions are trustworthy and won't mislead agricultural planners.",
            size=18.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    lessons = [
        ("1. The 'Equal Variance' Trap",
         "Trap: Assuming all states have similar fluctuations. Reality: Kerala varies by 14% while desert states swing by 70%. Solution: Used Welch's ANOVA, not naive textbook ANOVA.",
         RED),
        ("2. The 'Multiple Dice' Trap (p-Hacking)",
         "Trap: If you test 36 regions, random luck makes 2 or 3 look like they are drying up. Solution: Applied Benjamini–Hochberg False Discovery Rate to eliminate fake signals.",
         AMBER),
        ("3. The 'One Bell Curve' Trap",
         "Trap: Forcing heavy monsoon storms into a symmetric bell curve. Solution: Proved Lognormal models are required for pooled data, while individual states remain Gaussian.",
         GREEN),
        ("4. The 'Guessing Missing Data' Trap",
         "Trap: Filling broken official tables with made-up numbers. Solution: When 2020 IMD tables were scanned with errors, we gated it out and reported the gap honestly.",
         ACCENT),
    ]

    card_w = (W - 2 * MARGIN_L - emu(0.6)) // 2
    for i, (title, body, col) in enumerate(lessons):
        row = i // 2
        c_idx = i % 2
        x = MARGIN_L + c_idx * (card_w + emu(0.6))
        y = emu(3.6) + row * emu(5.2)

        _add_rect(slide, x, y, card_w, emu(4.7), CARD_BG)
        _add_rect(slide, x, y, emu(0.2), emu(4.7), col)
        _add_textbox(slide, x + emu(0.6), y + emu(0.4), card_w - emu(1.0), emu(0.8),
                     title, 13, bold=True, color=WHITE)
        _add_textbox(slide, x + emu(0.6), y + emu(1.4), card_w - emu(1.2), emu(3.0),
                     body, 10.2, color=MUTED, wrap=True)

    _footer(slide, 18)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 19: FIVE CORE TRUTHS (LAYMAN SYNTHESIS)
# ══════════════════════════════════════════════════════════════════════════════
def slide_five_truths(prs):
    slide = _slide(prs)
    _header(slide, "SYNTHESIS", "Five Simple Truths Every Teacher & Citizen Should Know",
            subtitle_text="The essential takeaways to remember about India's climate after 126 years of data.",
            size=18.0)
    _add_rule(slide, MARGIN_L, emu(3.0), W - 2 * MARGIN_L)

    items = [
        ("1", "India's Lifeblood Is 120 Days", "74% of rainfall occurs between June and September. Water policy must be built around saving 4 months of rain for 12 months of use.", ACCENT),
        ("2", "Geography Dictates Everything", "Location explains 86% of rainfall. Desert vs rainforest: national averages hide regional reality.", GREEN),
        ("3", "Total Rainfall Is NOT Disappearing", "Across 125 years, the secular trend is virtually zero (-18 mm/century). Long-term rainfall volume is stable.", AMBER),
        ("4", "Climate Risk Means Whiplash, Not Drying", "The real danger is extreme volatility: back-to-back droughts in Kerala followed by historic cloudburst floods in Gujarat.", RED),
        ("5", "Drought Is Local, Never Pan-India", "India has never experienced nationwide failure. Strong states always balance weak states, safeguarding food security.", ACCENT),
    ]

    for i, (num, head, body, col) in enumerate(items):
        y = emu(3.5) + i * emu(2.2)
        _add_rect(slide, MARGIN_L, y, emu(1.8), emu(1.8), CARD_BG)
        _add_textbox(slide, MARGIN_L + emu(0.15), y + emu(0.35), emu(1.5), emu(1.1),
                     num, 18, bold=True, color=col, align=PP_ALIGN.CENTER)
        _add_textbox(slide, MARGIN_L + emu(2.3), y + emu(0.1), emu(28.0), emu(0.75),
                     head, 13, bold=True, color=WHITE)
        _add_textbox(slide, MARGIN_L + emu(2.3), y + emu(0.9), emu(28.0), emu(0.85),
                     body, 10.5, color=MUTED)

    _footer(slide, 19)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 20: CLOSING & LIVE DEMO
# ══════════════════════════════════════════════════════════════════════════════
def slide_closing(prs):
    slide = _slide(prs)

    _add_textbox(slide, MARGIN_L, emu(3.0), emu(31), emu(2.2),
                 "VARSA turns 126 years of complex weather records into clear, undeniable truths —",
                 25, bold=True, color=WHITE)
    _add_textbox(slide, MARGIN_L, emu(5.4), emu(31), emu(1.4),
                 "with every calculation, graph, and interactive map reproducible in one click.",
                 25, bold=True, color=AMBER)

    _add_rule(slide, MARGIN_L, emu(7.6), W - 2 * MARGIN_L)

    _add_textbox(slide, MARGIN_L, emu(8.4), emu(31), emu(1.0),
                 "Thank You! We Welcome Any Questions & Would Love to Show You the Live Demo",
                 19, bold=True, color=WHITE)

    _add_textbox(slide, MARGIN_L, emu(10.0), emu(31), emu(0.7),
                 "Pratik (25BCE0337)  ·  Adarsh (25BCE0401)  ·  Arunya (25BCE0344)",
                 12, bold=True, color=ACCENT)
    _add_textbox(slide, MARGIN_L, emu(10.8), emu(31), emu(0.7),
                 "Faculty Mentor: Dr. Juhi Baroi  ·  Probability and Statistics (BAMAT207)",
                 11.5, color=MUTED)

    # Deliverables card
    _add_rect(slide, MARGIN_L, emu(12.0), W - 2 * MARGIN_L, emu(4.2), CARD_BG)
    _add_textbox(slide, MARGIN_L + emu(0.5), emu(12.3), emu(12.0), emu(0.6),
                 "LIVE PROJECT DELIVERABLES FOR EVALUATION", 9, bold=True, color=AMBER)
    delivs = (
        "• Live Interactive Dashboard: adarshkumarsingh5732-cpu-my-streamlit-dashboard-app-h5z5y7.streamlit.app\n"
        "• Static 3D Prism Atlas (Vercel): site/ (Deck.gl 125-year WebGL playback)\n"
        "• Open Source Code: github.com/ArunyaSrivastava/VARSA & github.com/adarshkumarsingh5732-cpu/VARSA\n"
        "• Automated Quality Assurance: scripts/test_date_coverage.py (100% passing test harness)\n"
        "• Complete Capstone Documentation: review_3/final_report.md"
    )
    _add_textbox(slide, MARGIN_L + emu(0.5), emu(13.0), W - 2 * MARGIN_L - emu(1.0), emu(2.8),
                 delivs, 10.0, color=WHITE)

    _footer(slide, 20)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN BUILDER
# ══════════════════════════════════════════════════════════════════════════════
def build():
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H

    print("Building Layman-Friendly VARSA Final Review Presentation with reduced headings...")
    slide_cover(prs)                 # 1
    slide_summary(prs)               # 2
    slide_evolution(prs)             # 3
    slide_accomplishments(prs)       # 4
    slide_data_architecture(prs)     # 5
    slide_qa_suite(prs)              # 6
    slide_findings_map(prs)          # 7
    build_finding_slides(prs)        # 8–12
    slide_finding_6(prs)             # 13
    slide_observed_verification(prs) # 14
    slide_modern_extremes(prs)       # 15
    slide_dashboard(prs)             # 16
    slide_vercel_atlas(prs)          # 17
    slide_methodology(prs)           # 18
    slide_five_truths(prs)           # 19
    slide_closing(prs)               # 20

    out = BASE / "VARSA_Final_Review.pptx"
    prs.save(str(out))
    print(f"Successfully generated {out} ({len(prs.slides)} slides).")


if __name__ == "__main__":
    build()
