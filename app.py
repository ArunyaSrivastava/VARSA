#!/usr/bin/env python3
"""
VARSA Explorer — Indian Rainfall Analytics
Streamlit dashboard for 36 meteorological subdivisions, 1901-2026.

Run with: streamlit run app.py
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import json
import os
from scipy import stats as _stats
from pathlib import Path
import textwrap

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VARSA Explorer — Indian Rainfall Analytics",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme (warm beige / cream light by default, dark mode optional) ─────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False  # light beige/cream is the default
_DARK = bool(st.session_state.get("dark_mode", False))

if _DARK:
    T = dict(
        bg="linear-gradient(160deg, #070c16 0%, #0c1424 50%, #060f18 100%)",
        bg_solid="#080d1a",
        sidebar="linear-gradient(180deg, #0b1326 0%, #060a14 100%)",
        side_border="rgba(34, 197, 94, 0.35)",  # distinct neon green sidebar border
        text="#f1f5f9", muted="#94a3b8", faint="#64748b",
        card="rgba(15, 23, 42, 0.88)", card2="rgba(17, 27, 49, 0.94)",
        border="rgba(34, 197, 94, 0.42)", hover="rgba(56, 189, 248, 0.85)",
        hero="linear-gradient(135deg, rgba(34, 197, 94, 0.16) 0%, rgba(56, 189, 248, 0.12) 100%)",
        accent="#22c55e", accent_soft="rgba(34, 197, 94, 0.18)", accent_border="rgba(34, 197, 94, 0.55)",
        blue="#38bdf8", blue_soft="rgba(56, 189, 248, 0.18)", blue_border="rgba(56, 189, 248, 0.55)",
        purple="#a855f7", amber="#f59e0b", title="#f8fafc",
        value="#ffffff", grid="rgba(255,255,255,0.07)",
        hr="rgba(34, 197, 94, 0.25)", chip="rgba(255,255,255,0.08)",
        foot="#64748b", font="'Outfit', 'Inter', -apple-system, sans-serif",
        shadow="0 14px 40px -8px rgba(0, 0, 0, 0.75), 0 0 16px rgba(34, 197, 94, 0.14)",
        shadow_hover="0 24px 55px -10px rgba(0, 0, 0, 0.85), 0 0 28px rgba(56, 189, 248, 0.35)",
        outline_map="1.5px solid rgba(56, 189, 248, 0.65)",
        glow_map="0 0 25px rgba(56, 189, 248, 0.20)",
        outline_dossier="1.5px solid rgba(34, 197, 94, 0.65)",
        glow_dossier="0 0 25px rgba(34, 197, 94, 0.20)",
        outline_hero="1.5px solid rgba(168, 85, 247, 0.55)",
        glow_hero="0 0 25px rgba(168, 85, 247, 0.18)",
    )
else:
    T = dict(
        bg="linear-gradient(150deg, #fbf7ee 0%, #f6f0df 45%, #eee3ce 100%)",
        bg_solid="#f7f2e6",
        sidebar="linear-gradient(180deg, #f5ecd9 0%, #ece0c5 100%)",
        side_border="rgba(165, 135, 90, 0.32)",
        text="#000000", muted="#374151", faint="#4b5563",
        card="rgba(255, 253, 247, 0.94)", card2="rgba(255, 252, 243, 0.98)",
        border="rgba(175, 142, 95, 0.32)", hover="rgba(21, 128, 61, 0.65)",
        hero="linear-gradient(135deg, rgba(21, 128, 61, 0.10) 0%, rgba(180, 83, 9, 0.08) 100%)",
        accent="#15803d", accent_soft="rgba(21, 128, 61, 0.12)", accent_border="rgba(21, 128, 61, 0.38)",
        blue="#0369a1", blue_soft="rgba(3, 105, 161, 0.12)", blue_border="rgba(3, 105, 161, 0.35)",
        purple="#6b21a8", amber="#b45309", title="#000000",
        value="#000000", grid="rgba(130, 100, 60, 0.10)",
        hr="rgba(175, 142, 95, 0.28)", chip="rgba(238, 226, 206, 0.85)",
        foot="#4b5563", font="'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif",
        shadow="0 10px 30px -8px rgba(78, 62, 38, 0.10), 0 2px 8px rgba(78, 62, 38, 0.05)",
        shadow_hover="0 20px 45px -10px rgba(78, 62, 38, 0.18), 0 4px 14px rgba(21, 128, 61, 0.12)",
        outline_map="1px solid rgba(175, 142, 95, 0.35)",
        glow_map="none",
        outline_dossier="1.5px solid rgba(21, 128, 61, 0.38)",
        glow_dossier="none",
        outline_hero="1px solid rgba(175, 142, 95, 0.35)",
        glow_hero="none",
    )

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=Inter:wght@400;500;600;700;800&display=swap');
:root {{
  --text: {T['text']}; --muted: {T['muted']}; --card: {T['card']};
  --border: {T['border']}; --accent: {T['accent']}; --grid: {T['grid']};
}}
* {{
  transition: background-color .3s cubic-bezier(0.16, 1, 0.3, 1),
              color .25s ease,
              border-color .25s ease,
              box-shadow .35s ease;
}}
html {{ scroll-behavior: smooth; }}
body {{ background: {T['bg_solid']}; }}
.stApp {{
  background: {T['bg']} !important;
  color: {T['text']};
  font-family: {T['font']} !important;
}}
header[data-testid="stHeader"] {{
  background: transparent !important;
}}
section[data-testid="stSidebar"] {{
  background: {T['sidebar']} !important;
  border-right: 1px solid {T['side_border']};
}}
section[data-testid="stSidebar"] .block-container {{ padding-top: 1.4rem; }}
.block-container {{ padding-top: 1.5rem; padding-bottom: 2.8rem; max-width: 1440px; }}

/* headings & bold text */
h1, h2, h3, h4, h5, h6 {{
  color: {T['title']} !important;
  font-family: {T['font']} !important;
  letter-spacing: -0.025em;
  font-weight: 750;
}}
b, strong, [data-testid="stMarkdownContainer"] b, [data-testid="stMarkdownContainer"] strong {{
  color: {"#f8fafc" if _DARK else "#000000"} !important;
}}

/* hero */
.hero {{
  background: {T['hero']};
  border: 1px solid {T['border']};
  border-radius: 28px;
  padding: 2.2rem 2.6rem;
  margin-bottom: 1.6rem;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: {T['shadow']};
}}
.hero:hover {{
  transform: translateY(-3px);
  box-shadow: {T['shadow_hover']};
}}
.hero h1 {{
  font-size: 2.65rem !important;
  font-weight: 850;
  letter-spacing: -0.04em;
  margin-bottom: .3rem;
  background: linear-gradient(92deg, {T['accent']} 0%, {T['blue']} 52%, {T['purple']} 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.hero p {{ color: {T['muted']}; font-size: 1.05rem; margin: 0; line-height: 1.5; }}
.hero .tag {{
  display: inline-block;
  background: {T['accent_soft']};
  color: {T['accent']};
  border: 1px solid {T['accent_border']};
  padding: .24rem .85rem;
  border-radius: 999px;
  font-size: .78rem;
  font-weight: 750;
  letter-spacing: .07em;
  text-transform: uppercase;
  margin-bottom: .9rem;
}}

/* KPI */
.kpi-row {{ display: flex; gap: 14px; margin: 1.1rem 0 1.7rem; flex-wrap: wrap; }}
.kpi {{
  flex: 1 1 210px;
  background: {T['card2']};
  border: 1px solid {T['border']};
  border-radius: 20px;
  padding: 1.15rem 1.35rem;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: {T['shadow']};
}}
.kpi:hover {{
  transform: translateY(-4px);
  border-color: {T['hover']};
  box-shadow: {T['shadow_hover']};
}}
.kpi .v {{
  font-size: 2.05rem;
  font-weight: 800;
  line-height: 1.12;
  color: {T['value']};
  letter-spacing: -.025em;
}}
.kpi .l {{
  font-size: .82rem;
  color: {T['muted']};
  margin-top: .35rem;
  font-weight: 550;
  line-height: 1.35;
}}
.kpi.green .v {{ color: {T['accent']}; }}
.kpi.blue .v {{ color: {T['blue']}; }}
.kpi.purple .v {{ color: {T['purple']}; }}
.kpi.amber .v {{ color: {T['amber']}; }}

/* cards & outlines */
.card {{
  background: {T['card']};
  border: 1px solid {T['border']};
  border-radius: 24px;
  padding: 1.8rem 2.0rem;
  margin-bottom: 1.6rem;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: {T['shadow']};
}}
.card.map-card {{
  border: {T['outline_map']} !important;
  box-shadow: {T['glow_map']} !important;
}}
.card.dossier-card {{
  border: {T['outline_dossier']} !important;
  box-shadow: {T['glow_dossier']} !important;
}}
.hero {{
  border: {T['outline_hero']} !important;
  box-shadow: {T['glow_hero']} !important;
}}
.card:hover {{
  border-color: {T['hover']} !important;
  box-shadow: {T['shadow_hover']};
}}

/* Custom Atmosphere Slider Switch */
[data-testid="stToggle"] {{
  display: flex !important;
  align-items: center !important;
  margin-top: 2px !important;
}}
[data-testid="stToggle"] label p {{
  font-size: 0.94rem !important;
  font-weight: 800 !important;
  color: {"#f8fafc" if _DARK else "#000000"} !important;
  letter-spacing: -0.01em !important;
}}

""" + ('''
/* DARK MODE DISTINCT GLOWING KPI BORDERS */
.kpi.green { border: 1.5px solid rgba(34, 197, 94, 0.65) !important; box-shadow: 0 0 16px rgba(34, 197, 94, 0.20) !important; }
.kpi.blue { border: 1.5px solid rgba(56, 189, 248, 0.65) !important; box-shadow: 0 0 16px rgba(56, 189, 248, 0.20) !important; }
.kpi.purple { border: 1.5px solid rgba(168, 85, 247, 0.65) !important; box-shadow: 0 0 16px rgba(168, 85, 247, 0.20) !important; }
.kpi.amber { border: 1.5px solid rgba(245, 158, 11, 0.65) !important; box-shadow: 0 0 16px rgba(245, 158, 11, 0.20) !important; }
''' if _DARK else '''
/* BEIGE MODE SOFT HARMONIOUS KPI BORDERS */
.kpi { border: 1px solid rgba(175, 142, 95, 0.32) !important; box-shadow: 0 4px 14px rgba(78, 62, 38, 0.06) !important; }
''') + f"""

.badge {{
  display: inline-block;
  background: {T['accent_soft']};
  color: {T['accent']};
  border: 1px solid {T['accent_border']};
  padding: .20rem .72rem;
  border-radius: 999px;
  font-size: .72rem;
  font-weight: 800;
  letter-spacing: .06em;
  text-transform: uppercase;
  margin-left: .6rem;
  vertical-align: middle;
}}
.badge.blue {{ background: {T['blue_soft']}; color: {T['blue']}; border-color: {T['blue_border']}; }}

h2.sect {{ font-size: 1.55rem; font-weight: 750; color: {T['title']}; margin-bottom: .35rem; }}
p.sect-sub {{ color: {T['muted']}; font-size: .95rem; margin-bottom: 1.2rem; line-height: 1.5; }}
p.sect-sub b {{ color: {T['accent']}; }}

/* metrics */
[data-testid="stMetric"] {{
  background: {T['card2']};
  border: 1px solid {T['border']};
  border-radius: 16px;
  padding: .9rem 1.1rem;
}}
[data-testid="stMetricValue"] {{ color: {T['value']} !important; font-weight: 750; }}

/* widgets */
/* widgets */
.stButton > button, [data-testid="stButton"] > button {{
  border-radius: 999px !important;
  font-weight: 700 !important;
  border: 1.5px solid {T['border']} !important;
  background: {"#111e17" if _DARK else "#ffffff"} !important;
  color: {"#f1f5f9" if _DARK else "#292524"} !important;
  box-shadow: {"0 2px 8px rgba(0,0,0,0.3)" if _DARK else "0 2px 8px rgba(0,0,0,0.06)"} !important;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}
.stButton > button:hover {{
  transform: translateY(-2px);
  box-shadow: {T['shadow_hover']};
  border-color: {T['hover']} !important;
  background: {"#182e22" if _DARK else "#fcfaf7"} !important;
}}
/* BaseWeb Selects, Inputs, and Tags Styling */
[data-baseweb="select"] > div, [data-baseweb="input"] > div {{
  background: {T['chip']} !important;
  border-radius: 12px !important;
  border-color: {T['border']} !important;
}}
/* Force high-contrast text inside select boxes and inputs */
[data-baseweb="select"] * {{
  color: {"#f1f5f9" if _DARK else "#1c1917"} !important;
  font-family: {T['font']} !important;
}}
[data-baseweb="input"] input {{
  color: {"#f1f5f9" if _DARK else "#1c1917"} !important;
}}
/* Multiselect chips / tags with strong contrast */
[data-baseweb="tag"] {{
  background: {"rgba(16, 185, 129, 0.22)" if _DARK else "#d1fae5"} !important;
  border: 1px solid {"#10b981" if _DARK else "#86efac"} !important;
  border-radius: 999px !important;
  padding: 2px 8px !important;
}}
[data-baseweb="tag"] span {{
  color: {"#6ee7b7" if _DARK else "#065f46"} !important;
  font-weight: 700 !important;
  font-size: 0.82rem !important;
}}
[data-baseweb="tag"] svg {{
  fill: {"#6ee7b7" if _DARK else "#065f46"} !important;
}}
/* Dropdown popup menu list items */
[data-baseweb="popover"], [data-baseweb="menu"] {{
  background-color: {T['card']} !important;
}}
[data-baseweb="menu"] li, [data-baseweb="menu"] div, [data-baseweb="menu"] span {{
  color: {"#f1f5f9" if _DARK else "#1c1917"} !important;
}}
/* Sidebar labels, markdown and captions */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] label p,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] span {{
  color: {"#f1f5f9" if _DARK else "#1c1917"} !important;
  font-weight: 600;
}}
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span {{
  color: {"#f1f5f9" if _DARK else "#1c1917"} !important;
  font-weight: 700 !important;
}}

/* Bespoke styling for All States Comparison Navigation Buttons */
div[class*="st-key-btn_sidebar_nav_comparisons"] button,
section[data-testid="stSidebar"] div[class*="st-key-btn_sidebar_nav_comparisons"] button,
section[data-testid="stSidebar"] div.st-key-btn_sidebar_nav_comparisons > button,
div[class*="st-key-btn_dossier_return_comp"] button {{
  background: {"linear-gradient(135deg, rgba(16, 185, 129, 0.22) 0%, rgba(5, 150, 105, 0.32) 100%)" if _DARK else "linear-gradient(135deg, #ffffff 0%, #ecfdf5 100%)"} !important;
  color: {"#6ee7b7" if _DARK else "#065f46"} !important;
  border: 1.5px solid {"#10b981" if _DARK else "#059669"} !important;
  border-radius: 999px !important;
  font-weight: 800 !important;
  font-size: 0.90rem !important;
  letter-spacing: -0.01em !important;
  padding: 8px 16px !important;
  box-shadow: {"0 0 18px rgba(16, 185, 129, 0.28)" if _DARK else "0 4px 14px rgba(16, 185, 129, 0.18)"} !important;
  transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}
div[class*="st-key-btn_sidebar_nav_comparisons"] button:hover,
section[data-testid="stSidebar"] div[class*="st-key-btn_sidebar_nav_comparisons"] button:hover,
section[data-testid="stSidebar"] div.st-key-btn_sidebar_nav_comparisons > button:hover,
div[class*="st-key-btn_dossier_return_comp"] button:hover {{
  background: {"linear-gradient(135deg, rgba(16, 185, 129, 0.36) 0%, rgba(5, 150, 105, 0.48) 100%)" if _DARK else "linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)"} !important;
  color: {"#ffffff" if _DARK else "#064e3b"} !important;
  border-color: {"#34d399" if _DARK else "#047857"} !important;
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: {"0 0 28px rgba(16, 185, 129, 0.48)" if _DARK else "0 8px 22px rgba(16, 185, 129, 0.28)"} !important;
}}
div[class*="st-key-btn_sidebar_nav_comparisons"] button p,
div[class*="st-key-btn_sidebar_nav_comparisons"] button span,
section[data-testid="stSidebar"] div[class*="st-key-btn_sidebar_nav_comparisons"] button p,
section[data-testid="stSidebar"] div[class*="st-key-btn_sidebar_nav_comparisons"] button span,
div[class*="st-key-btn_dossier_return_comp"] button p,
div[class*="st-key-btn_dossier_return_comp"] button span {{
  color: {"#6ee7b7" if _DARK else "#065f46"} !important;
  font-weight: 800 !important;
}}
div[class*="st-key-btn_sidebar_nav_comparisons"] button:hover p,
div[class*="st-key-btn_sidebar_nav_comparisons"] button:hover span,
section[data-testid="stSidebar"] div[class*="st-key-btn_sidebar_nav_comparisons"] button:hover p,
section[data-testid="stSidebar"] div[class*="st-key-btn_sidebar_nav_comparisons"] button:hover span,
div[class*="st-key-btn_dossier_return_comp"] button:hover p,
div[class*="st-key-btn_dossier_return_comp"] button:hover span {{
  color: {"#ffffff" if _DARK else "#064e3b"} !important;
}}

hr {{ border-color: {T['hr']} !important; }}
stcaption, .stCaption, caption {{ color: {T['muted']} !important; }}
[data-testid="stMarkdownContainer"] p {{ color: {T['text']}; }}

/* segmented control (map style) */
[data-testid="stSegmentedControl"] {{
  background: {T['chip']};
  border-radius: 16px;
  padding: 6px;
  border: 1px solid {T['border']};
}}
[data-testid="stSegmentedControl"] button {{
  border-radius: 12px !important;
  background: transparent !important;
  color: {T['muted']} !important;
  font-weight: 700 !important;
}}
[data-testid="stSegmentedControl"] button[aria-checked="true"] {{
  background: {T['accent']} !important;
  color: #fff !important;
  box-shadow: 0 6px 18px rgba(21, 128, 61, .35);
}}

/* Quick Jump Regional Buttons with Bespoke Gradients */
div[class*="st-key-q_"] button, div[class*="q_"] button {{
  border-radius: 999px !important;
  font-size: 0.82rem !important;
  font-weight: 750 !important;
  padding: 6px 12px !important;
  white-space: nowrap !important;
  letter-spacing: -0.01em !important;
  transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}
div[class*="st-key-q_"] button:hover, div[class*="q_"] button:hover {{
  transform: translateY(-2px) scale(1.03) !important;
  filter: brightness(1.08) !important;
}}
""" + ('''
/* DARK MODE GEM GRADIENTS FOR QUICK JUMP */
div[class*="q_Kerala"] button {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.22) 0%, rgba(5, 150, 105, 0.36) 100%) !important;
  color: #6ee7b7 !important;
  border: 1.5px solid #10b981 !important;
  box-shadow: 0 0 16px rgba(16, 185, 129, 0.28) !important;
}
div[class*="q_Uttarakhand"] button {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.22) 0%, rgba(3, 105, 161, 0.36) 100%) !important;
  color: #7dd3fc !important;
  border: 1.5px solid #0ea5e9 !important;
  box-shadow: 0 0 16px rgba(14, 165, 233, 0.28) !important;
}
div[class*="q_Assam"] button {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.22) 0%, rgba(91, 33, 182, 0.36) 100%) !important;
  color: #c4b5fd !important;
  border: 1.5px solid #8b5cf6 !important;
  box-shadow: 0 0 16px rgba(139, 92, 246, 0.28) !important;
}
div[class*="q_West_Rajasthan"] button, div[class*="Rajasthan"] button {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.22) 0%, rgba(180, 83, 9, 0.36) 100%) !important;
  color: #fde68a !important;
  border: 1.5px solid #f59e0b !important;
  box-shadow: 0 0 16px rgba(245, 158, 11, 0.28) !important;
}
div[class*="q_Konkan"] button {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.22) 0%, rgba(14, 116, 144, 0.36) 100%) !important;
  color: #a5f3fc !important;
  border: 1.5px solid #06b6d4 !important;
  box-shadow: 0 0 16px rgba(6, 182, 212, 0.28) !important;
}
div[class*="q_Himachal"] button {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.22) 0%, rgba(21, 128, 61, 0.36) 100%) !important;
  color: #86efac !important;
  border: 1.5px solid #22c55e !important;
  box-shadow: 0 0 16px rgba(34, 197, 94, 0.28) !important;
}
''' if _DARK else '''
/* BEIGE MODE SOFT HARMONIOUS NATURE GRADIENTS */
div[class*="q_Kerala"] button {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%) !important;
  color: #065f46 !important;
  border: 1.5px solid #86efac !important;
  box-shadow: 0 3px 12px rgba(16, 185, 129, 0.16) !important;
}
div[class*="q_Uttarakhand"] button {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%) !important;
  color: #0369a1 !important;
  border: 1.5px solid #7dd3fc !important;
  box-shadow: 0 3px 12px rgba(14, 165, 233, 0.16) !important;
}
div[class*="q_Assam"] button {
  background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%) !important;
  color: #5b21b6 !important;
  border: 1.5px solid #c4b5fd !important;
  box-shadow: 0 3px 12px rgba(139, 92, 246, 0.16) !important;
}
div[class*="q_West_Rajasthan"] button, div[class*="Rajasthan"] button {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%) !important;
  color: #92400e !important;
  border: 1.5px solid #fcd34d !important;
  box-shadow: 0 3px 12px rgba(245, 158, 11, 0.16) !important;
}
div[class*="q_Konkan"] button {
  background: linear-gradient(135deg, #ecfeff 0%, #cffafe 100%) !important;
  color: #0e7490 !important;
  border: 1.5px solid #67e8f9 !important;
  box-shadow: 0 3px 12px rgba(6, 182, 212, 0.16) !important;
}
div[class*="q_Himachal"] button {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
  color: #166534 !important;
  border: 1.5px solid #86efac !important;
  box-shadow: 0 3px 12px rgba(34, 197, 94, 0.16) !important;
}
''') + f"""
.quick-jump-strip button {{
  border-radius: 12px !important;
  font-size: 0.84rem !important;
  font-weight: 750 !important;
  padding: 6px 10px !important;
  letter-spacing: -0.01em !important;
}}
.quick-jump-strip button:hover {{
  transform: translateY(-2px) scale(1.02) !important;
  filter: brightness(1.06) !important;
}}

/* Custom slider styles - Clean green/amber, no harsh red */
div[data-baseweb="slider"] div[role="slider"] {{
  background-color: {T['accent']} !important;
  border: 2px solid #ffffff !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.25) !important;
}}
div[data-baseweb="slider"] div:has(> div[role="slider"]) {{
  background: {T['accent']} !important;
}}
.stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"] {{
  color: {T['muted']} !important;
  font-weight: 700 !important;
}}

/* Sidebar luxury styling */
.sidebar-header-badge {{
  background: {T['card2']};
  border: 1px solid {T['border']};
  border-radius: 18px;
  padding: 1.1rem 1.25rem;
  margin-bottom: 1.1rem;
  box-shadow: {T['shadow']};
}}
.sidebar-stats-card {{
  background: {T['card2']};
  border: 1px solid {T['border']};
  border-radius: 16px;
  padding: 0.95rem 1.1rem;
  margin-top: 1.2rem;
  box-shadow: {T['shadow']};
}}

/* custom scrollbars */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T['border']}; border-radius: 999px; }}
::-webkit-scrollbar-thumb:hover {{ background: {T['accent']}; }}

.foot {{
  text-align: center;
  color: {T['foot']};
  font-size: .85rem;
  padding-top: 1.5rem;
  border-top: 1px solid {T['hr']};
  margin-top: 1.6rem;
  line-height: 1.6;
}}
.foot b {{ color: {T['muted']}; }}

/* smoother plotly cards inside charts and clean separation from controls */
.js-plotly-plot .plotly .main-svg {{ border-radius: 18px; }}
[data-testid="stPlotlyChart"] {{
  margin-bottom: 1.5rem !important;
  position: relative;
  z-index: 1;
}}
.maplibregl-ctrl-attrib, .mapboxgl-ctrl-attrib {{
  margin-bottom: 8px !important;
  border-radius: 6px !important;
  background-color: rgba(255, 255, 255, 0.75) !important;
  padding: 2px 6px !important;
}}

/* Fact Sheet Quadrilateral Cards */
.fact-quad-card {{
  background: {T['card2']};
  border: 1px solid {T['border']};
  border-radius: 14px;
  padding: 1.15rem 1.25rem;
  box-shadow: {T['shadow']};
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}}
.fact-quad-card:hover {{
  transform: translateY(-2px);
  border-color: {T['hover']};
  box-shadow: {T['shadow_hover']};
}}
.fact-quad-badge {{
  display: inline-flex;
  align-items: center;
  font-size: 0.70rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 3px 8px;
  border-radius: 6px;
  margin-bottom: 0.55rem;
  width: fit-content;
}}
.fact-quad-title {{
  font-size: 1.02rem;
  font-weight: 800;
  color: {T['title']};
  margin-bottom: 0.25rem;
  line-height: 1.25;
}}
.fact-quad-metric {{
  font-size: 1.55rem;
  font-weight: 850;
  color: {T['value']};
  margin-bottom: 0.45rem;
  line-height: 1.1;
}}
.fact-quad-body {{
  font-size: 0.84rem;
  color: {T['muted']};
  line-height: 1.55;
}}
.fact-quad-body ul {{
  margin: 0.25rem 0 0 0;
  padding-left: 1.1rem;
}}
.fact-quad-body li {{
  margin-bottom: 0.3rem;
}}



/* ═════════════════════════════════════════════════════════════════════════════
   DYNAMIC CLIMATIC WEATHER STAGE & DRIZZLE SIMULATION (PURE CSS)
   ═════════════════════════════════════════════════════════════════════════════ */
.weather-stage {{
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  padding: 1.4rem 1.8rem;
  margin-bottom: 1.3rem;
  border: 1px solid {T['border']};
  background: {T['card2']};
  box-shadow: {T['shadow']};
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 18px;
}}

.rain-overlay {{
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 1;
}}

.rain-overlay.heavy .rain-drop {{
  position: absolute;
  top: -45px;
  width: 1.8px;
  height: 32px;
  background: linear-gradient(180deg, rgba(56, 189, 248, 0), rgba(56, 189, 248, 0.85));
  border-radius: 999px;
  transform: rotate(14deg);
  animation: rainDropFall linear infinite;
}}

.rain-overlay.drizzle .rain-drop {{
  position: absolute;
  top: -30px;
  width: 1.2px;
  height: 20px;
  background: linear-gradient(180deg, rgba(34, 197, 94, 0), rgba(34, 197, 94, 0.75));
  border-radius: 999px;
  transform: rotate(6deg);
  animation: rainDropFall linear infinite;
}}

.rain-overlay.arid .rain-drop {{
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: rgba(245, 158, 11, 0.55);
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.7);
  animation: dustMoteFloat ease-in-out infinite alternate;
}}

@keyframes rainDropFall {{
  0% {{ transform: translateY(-40px) translateX(0) rotate(14deg); opacity: 0; }}
  20% {{ opacity: 0.95; }}
  80% {{ opacity: 0.95; }}
  100% {{ transform: translateY(220px) translateX(45px) rotate(14deg); opacity: 0; }}
}}

@keyframes dustMoteFloat {{
  0% {{ transform: translateY(160px) translateX(0); opacity: 0.2; }}
  100% {{ transform: translateY(-10px) translateX(30px); opacity: 0.85; }}
}}

.weather-info-layer {{
  position: relative;
  z-index: 2;
  flex: 1 1 360px;
}}

.weather-gauge-layer {{
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 16px;
}}

.gauge-tube {{
  width: 32px;
  height: 120px;
  border-radius: 16px;
  border: 2px solid rgba(255,255,255,0.45);
  background: rgba(0,0,0,0.07);
  box-shadow: inset 0 2px 6px rgba(0,0,0,0.22), 0 4px 14px rgba(34,197,94,0.18);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(4px);
}}

.gauge-liquid {{
  position: absolute;
  bottom: 0; left: 0; width: 100%;
  border-radius: 0 0 14px 14px;
  transition: height 1.2s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 0 10px rgba(56,189,248,0.5);
}}


@keyframes pulseDot {{
  0% {{ transform: scale(1); opacity: 1; }}
  50% {{ transform: scale(1.4); opacity: 0.6; }}
  100% {{ transform: scale(1); opacity: 1; }}
}}
</style>
""", unsafe_allow_html=True)


# ── Load data ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "raw" / "india_rainfall.csv"
GEOJSON_PATH = BASE_DIR / "data" / "geo" / "india_boundary.geojson"

# ── Unified data service: pipeline layer (1901-2015) + observed IMD (2015-2026) ──
GEO_SUBDIVISIONS = BASE_DIR / "data" / "geo" / "imd_subdivisions.geojson"
OBS_SUBDIVISIONS = BASE_DIR / "data" / "raw" / "imd_observed_subdivisions.csv"
OBS_NATIONAL_MONSOON = BASE_DIR / "data" / "raw" / "imd_all_india_monsoon.csv"
OBS_NATIONAL_MONTHLY = BASE_DIR / "data" / "raw" / "imd_all_india_monthly.csv"

# season label -> (pipeline-layer season, observed-layer season)
PRISM_SEASONS = {
    "Monsoon (Jun–Sep)": ("JAS", "MONSOON"),
    "Annual": ("ANNUAL", "ANNUAL"),
    "Winter": ("DJF", "WINTER"),
    "Pre-monsoon (Mar–May)": ("MAM", "PREMONSOON"),
    "Post-monsoon (Oct–Dec)": ("OND", "POSTMONSOON"),
}


@st.cache_data(show_spinner=False)
def load_unified_subdivisions() -> pd.DataFrame:
    """Pipeline layer (generated, 1901-2015) + observed IMD subdivisions
    (2015-2025). Observed values win for overlapping 2015. Returns
    (year, division, season, actual_mm, pct_dep, layer)."""
    frames = []
    pipe = load_data()
    div_map = {}  # pipeline division name -> observed canonical name (approximate)
    for p_name, o_name in [
        ("Orissa", "ODISHA"), ("Coastal Odisha", "ODISHA"),
        ("Uttarakhand", "UTTARAKHAND"), ("Uttaranchal", "UTTARAKHAND"),
        ("Gangetic West Bengal", "GANGETIC W.B."), ("Sub-Montane West Bengal", "SUB-HIMALAYAN W.B. & SIKKIM"),
        ("Sikkim", "SUB-HIMALAYAN W.B. & SIKKIM"), ("Jammu & Kashmir", "JAMMU & KASHMIR"),
        ("Ladakh", "JAMMU & KASHMIR"), ("Cold Desert (HP & UK)", "HIMACHAL PRADESH"),
        ("Haryana, Delhi & Chandigarh", "HARYANA-CHD-DELHI"),
        ("East Uttar Pradesh", "EAST U.P."), ("West Uttar Pradesh", "WEST U.P."),
        ("North West Uttar Pradesh", "WEST U.P."),
        ("East Rajasthan", "EAST RAJASTHAN"), ("West Rajasthan", "WEST RAJASTHAN"),
        ("Madhya Bharat", "WEST M.P."), ("Madhya Maharashtra", "MADHYA MAHARASHTRA"),
        ("Chhattisgarh", "CHHATTISGARH"), ("Bihar", "BIHAR"), ("Jharkhand", "JHARKHAND"),
        ("Coast Andhra Pradesh", "COASTAL A.P."), ("Coastal Andhra Pradesh & Yanam", "COASTAL A.P."),
        ("Telangana", "TELANGANA"), ("Rayalaseema", "RAYALASEEMA"), ("Tamil Nadu", "TAMIL NADU"),
        ("Coastal Karnataka", "COASTAL KARNATAKA"),
        ("North Interior Karnataka", "NORTH INTERIOR KARNATAKA"),
        ("South Interior Karnataka", "SOUTH INTERIOR KARNATAKA"),
        ("Kerala", "KERALA"), ("Lakshadweep", "LAKSHADWEEP"),
        ("Arunachal Pradesh", "ARUNACHAL PRADESH"),
        ("Assam & Meghalaya", "ASSAM & MEGHALAYA"),
        ("Himachal Pradesh", "HIMACHAL PRADESH"), ("Punjab", "PUNJAB"),
        ("Gujarat Region", "GUJARAT REGION"), ("Konkan & Goa", "KONKAN & GOA"),
        ("Vidarbha", "VIDARBHA"), ("Marathwada", "MARATHAWADA"),
    ]:
        div_map[p_name] = o_name
    for season_label, (p_season, _o) in PRISM_SEASONS.items():
        q = pipe[pipe["season"] == p_season][["year", "division", "rainfall_mm"]]
        q = q.assign(season=season_label, pct_dep=np.nan, layer="pipeline (generated)")
        frames.append(q)
    unified = pd.concat(frames, ignore_index=True)
    unified["division"] = unified["division"].map(lambda d: div_map.get(d, d.upper()))

    if OBS_SUBDIVISIONS.exists():
        obs = pd.read_csv(OBS_SUBDIVISIONS)
        obs = obs.rename(columns={"actual_mm": "rainfall_mm"})
        obs["layer"] = "observed IMD"
        obs = obs[obs["year"] > 2015]  # 2015 kept from pipeline for continuity; observed kept in its own file
        # re-key observed seasons to display labels
        inv = {o: label for label, (_p, o) in PRISM_SEASONS.items()}
        obs["season"] = obs["season"].map(inv)
        unified = pd.concat([unified[unified["year"] <= 2015], obs], ignore_index=True)
    # several pipeline divisions map onto one IMD subdivision (e.g. J&K + Ladakh,
    # Sikkim + Sub-Himalayan WB): aggregate to the canonical division mean
    unified = unified.groupby(["year", "division", "season"], as_index=False).agg(
        rainfall_mm=("rainfall_mm", "mean"),
        pct_dep=("pct_dep", "mean"),
        layer=("layer", "first"),
    )
    return unified.rename(columns={"rainfall_mm": "actual_mm"})


@st.cache_data(show_spinner=False)
def load_national_2026() -> dict | None:
    """Latest observed all-India monsoon numbers (2026 in progress)."""
    if not OBS_NATIONAL_MONSOON.exists():
        return None
    m = pd.read_csv(OBS_NATIONAL_MONSOON)
    row = m[(m["region"] == "ALL INDIA") & (m["year"] == m["year"].max())]
    if row.empty:
        return None
    r = row.iloc[0]
    return {"year": int(r["year"]), "mm": float(r["jun_sep"]),
            "dep": float(r["jun_sep_dep"])}


# Pipeline division name -> canonical IMD subdivision name used by the observed
# layer (same mapping as load_unified_subdivisions).
PIPE_TO_CANON = {
    "Orissa": "ODISHA", "Coastal Odisha": "ODISHA",
    "Uttarakhand": "UTTARAKHAND", "Uttaranchal": "UTTARAKHAND",
    "Gangetic West Bengal": "GANGETIC W.B.",
    "Sub-Montane West Bengal": "SUB-HIMALAYAN W.B. & SIKKIM",
    "Sikkim": "SUB-HIMALAYAN W.B. & SIKKIM",
    "Jammu & Kashmir": "JAMMU & KASHMIR", "Ladakh": "JAMMU & KASHMIR",
    "Cold Desert (HP & UK)": "HIMACHAL PRADESH",
    "Haryana, Delhi & Chandigarh": "HARYANA-CHD-DELHI",
    "East Uttar Pradesh": "EAST U.P.", "West Uttar Pradesh": "WEST U.P.",
    "North West Uttar Pradesh": "WEST U.P.",
    "East Rajasthan": "EAST RAJASTHAN", "West Rajasthan": "WEST RAJASTHAN",
    "Madhya Bharat": "WEST M.P.", "Madhya Maharashtra": "MADHYA MAHARASHTRA",
    "Chhattisgarh": "CHHATTISGARH", "Bihar": "BIHAR", "Jharkhand": "JHARKHAND",
    "Coast Andhra Pradesh": "COASTAL A.P.",
    "Telangana": "TELANGANA", "Rayalaseema": "RAYALASEEMA",
    "Tamil Nadu": "TAMIL NADU", "Coastal Karnataka": "COASTAL KARNATAKA",
    "North Interior Karnataka": "NORTH INTERIOR KARNATAKA",
    "South Interior Karnataka": "SOUTH INTERIOR KARNATAKA",
    "Kerala": "KERALA", "Lakshadweep": "LAKSHADWEEP",
    "Arunachal Pradesh": "ARUNACHAL PRADESH", "Assam & Meghalaya": "ASSAM & MEGHALAYA",
    "Himachal Pradesh": "HIMACHAL PRADESH", "Punjab": "PUNJAB",
    "Gujarat Region": "GUJARAT REGION", "Konkan & Goa": "KONKAN & GOA",
    "Vidarbha": "VIDARBHA", "Marathwada": "MARATHAWADA",
}

# Observed seasons that share the pipeline definition (annual = calendar year,
# monsoon/pre/post-monsoon identical). Observed WINTER is Jan-Feb vs the
# pipeline's Dec-Feb, so it is never merged silently.
OBS_SEASONS_MERGEABLE = {"JAS": "MONSOON", "MAM": "PREMONSOON", "OND": "POSTMONSOON", "ANNUAL": "ANNUAL"}


@st.cache_data(show_spinner=False)
def observed_rows_for_division(canon_name: str, include_winter: bool = False) -> pd.DataFrame:
    """Observed IMD rows (2016-2025) for one canonical subdivision, in the
    pipeline schema (year, division, season, rainfall_mm + layer tag).
    Winter rows are excluded unless explicitly requested (definition differs)."""
    if not OBS_SUBDIVISIONS.exists() or canon_name is None:
        return pd.DataFrame(columns=["year", "division", "season", "rainfall_mm", "layer"])
    obs = pd.read_csv(OBS_SUBDIVISIONS)
    obs = obs[obs["division"] == canon_name]
    season_map = dict(OBS_SEASONS_MERGEABLE)
    if include_winter:
        season_map["WINTER"] = "DJF"
    obs = obs[obs["season"].isin(season_map)]
    return pd.DataFrame({
        "year": obs["year"].astype(int),
        "division": canon_name,
        "season": obs["season"].map(season_map),
        "rainfall_mm": obs["actual_mm"],
        "pct_dep": obs["pct_dep"],
        "layer": "observed IMD",
    })


@st.cache_data(show_spinner=False)
def load_national_extended() -> pd.DataFrame:
    """All-India annual series across layers: pipeline mean of 36 divisions
    (1901-2015) + observed IMD annual (2016-2025; 2026 has no annual total yet).
    Columns: year, mm, layer. Monsoon Jun-Sep (observed, incl. provisional 2026)
    is attached as monsoon_mm/monsoon_dep where available."""
    base = (
        df[df["season"] == "ANNUAL"]
        .groupby("year")["rainfall_mm"]
        .mean()
        .rename("mm")
        .reset_index()
    )
    base["layer"] = "pipeline (generated)"
    out = base
    if OBS_NATIONAL_MONTHLY.exists():
        m = pd.read_csv(OBS_NATIONAL_MONTHLY)
        ai = m[(m["region"] == "ALL INDIA") & (m["month"] == "ANNUAL")][["year", "rainfall_mm"]]
        ai = ai[ai["rainfall_mm"].notna() & (ai["year"] > 2015)]
        obs = pd.DataFrame({
            "year": ai["year"].astype(int), "mm": ai["rainfall_mm"].astype(float),
            "layer": "observed IMD",
        })
        out = pd.concat([out, obs], ignore_index=True)
    if OBS_NATIONAL_MONSOON.exists():
        mon = pd.read_csv(OBS_NATIONAL_MONSOON)
        mon = mon[mon["region"] == "ALL INDIA"][["year", "jun_sep", "jun_sep_dep"]]
        mon.columns = ["year", "monsoon_mm", "monsoon_dep"]
        mon["year"] = mon["year"].astype(int)
        # outer merge so monsoon-only years (2026 in progress) survive even
        # though they have no annual total yet
        out = out.merge(mon, on="year", how="outer")
        out["layer"] = out["layer"].fillna("observed IMD (monsoon only, provisional)")
    else:
        out["monsoon_mm"] = np.nan
        out["monsoon_dep"] = np.nan
    return out.sort_values("year").reset_index(drop=True)


def _dep_color(dep: float) -> list:
    """%departure -> RGB for the prism map."""
    if dep is None or (isinstance(dep, float) and np.isnan(dep)):
        return [120, 130, 145]
    if dep >= 20:
        return [29, 78, 216]     # blue: large excess
    if dep >= 0:
        return [34, 197, 94]     # green: normal/excess
    if dep >= -20:
        return [234, 179, 8]     # amber: deficit
    if dep >= -40:
        return [249, 115, 22]    # orange: moderate deficit
    return [220, 38, 38]         # red: severe deficit


@st.cache_data(show_spinner=False)
def prism_frame(season_label: str, year: int):
    """(geojson polygons joined with values, stats) for the prism view."""
    import json as _json
    if not GEO_SUBDIVISIONS.exists():
        return None, None
    geo = _json.loads(GEO_SUBDIVISIONS.read_text(encoding="utf-8"))
    uni = load_unified_subdivisions()
    sel = uni[(uni["season"] == season_label) & (uni["year"] == year)]
    # for pipeline years colour by % anomaly vs the division's long-run mean
    if year <= 2015:
        base = uni[(uni["season"] == season_label) & (uni["year"] <= 2015)]
        means = base.groupby("division")["actual_mm"].mean()
        sel = sel.set_index("division")
        sel["pct_dep"] = 100 * (sel["actual_mm"] - means) / means
        sel = sel.reset_index()
    rows = sel.set_index("division")
    feats = []
    for f in geo["features"]:
        d = f["properties"]["division"]
        g = f["geometry"]
        if g["type"] == "Polygon":
            rings = [g["coordinates"]]
        else:
            rings = [p for p in g["coordinates"] if p and len(p[0]) >= 4]
        for ring in rings:
            rec = {"name": d, "region": f["properties"]["region"],
                   "polygon": [[pt[0], pt[1]] for pt in ring[0]]}
            if d in rows.index:
                r = rows.loc[d]
                if hasattr(r, "item"):
                    r = rows.loc[[d]].iloc[0]
                rec["mm"] = float(r["actual_mm"]) if pd.notna(r["actual_mm"]) else 0.0
                rec["dep"] = float(r["pct_dep"]) if pd.notna(r["pct_dep"]) else None
                rec["layer"] = str(r["layer"])
            else:
                rec["mm"], rec["dep"], rec["layer"] = 0.0, None, "no data"
            rec["color"] = _dep_color(rec["dep"]) + [185]
            feats.append(rec)
    return feats, rows



@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["season"] = df["season"].astype(str)
    return df

df = load_data()

@st.cache_data
def get_india_geojson():
    if GEOJSON_PATH.exists():
        try:
            with open(GEOJSON_PATH, "r", encoding="utf-8") as _f:
                return json.load(_f)
        except Exception:
            return None
    return None

# National annual series
yearly_national = (
    df[df["season"] == "ANNUAL"]
    .groupby("year")["rainfall_mm"]
    .agg(["mean", "std"])
    .reset_index()
    .rename(columns={"mean": "national_annual_mean", "std": "national_annual_std"})
)

# ── Division geographic coordinates (approximate centroids) ──────────────────
DIV_COORDS = {
    "Arunachal Pradesh": (28.1, 95.0), "Assam & Meghalaya": (26.2, 92.7),
    "Coastal Karnataka": (13.5, 74.9), "Coast Andhra Pradesh": (16.2, 81.5),
    "Coastal Odisha": (20.4, 85.6), "Cold Desert (HP & UK)": (32.9, 77.6),
    "East Rajasthan": (26.4, 75.4), "East Uttar Pradesh": (26.8, 82.0),
    "Gujarat Region": (22.6, 71.9), "Haryana, Delhi & Chandigarh": (29.1, 76.6),
    "Himachal Pradesh": (31.8, 77.2), "Jammu & Kashmir": (34.2, 74.6),
    "Jharkhand": (23.6, 85.6), "Kerala": (10.3, 76.4),
    "Konkan & Goa": (15.4, 73.9), "Lakshadweep": (10.5, 73.0),
    "Madhya Maharashtra": (19.4, 75.4), "Madhya Bharat": (23.8, 78.4),
    "North Interior Karnataka": (14.7, 76.4), "North West Uttar Pradesh": (28.4, 79.4),
    "Orissa": (20.9, 84.8), "Rayalaseema": (14.9, 78.6),
    "South Interior Karnataka": (13.1, 76.9), "Tamil Nadu": (11.1, 78.7),
    "Telangana": (17.9, 79.2), "West Rajasthan": (26.1, 71.0),
    "West Uttar Pradesh": (27.4, 79.2), "Bihar": (25.6, 85.1),
    "Chhattisgarh": (21.4, 81.7), "Gangetic West Bengal": (23.5, 87.7),
    "Ladakh": (34.5, 77.6), "Sikkim": (27.6, 88.5),
    "Sub-Montane West Bengal": (26.4, 87.6), "Uttarakhand": (30.1, 79.3),
    "Vidarbha": (20.9, 78.9), "Marathwada": (19.2, 76.0),
}

DIV_DESC = {
    "Arunachal Pradesh": "NE Himalaya — orographic extremes", "Assam & Meghalaya": "Brahmaputra plains — monsoon core",
    "Coastal Karnataka": "Western Ghats — windward belt", "Coast Andhra Pradesh": "Coromandel — cyclonic rain",
    "Coastal Odisha": "Bay coast — pre-monsoon storms", "Cold Desert (HP & UK)": "Rain shadow — near arid",
    "East Rajasthan": "Aravalli fringe", "East Uttar Pradesh": "Ganga plain",
    "Gujarat Region": "Saurashtra — arid fringe", "Haryana, Delhi & Chandigarh": "NW plains — moisture starved",
    "Himachal Pradesh": "Himalayan foothills", "Jammu & Kashmir": "Western disturbance zone",
    "Jharkhand": "Chotanagpur plateau", "Kerala": "SW coast — classic monsoon",
    "Konkan & Goa": "Ghat coast — extreme totals", "Lakshadweep": "Atoll — maritime signal",
    "Madhya Maharashtra": "Deccan leeward", "Madhya Bharat": "Central Indian plateau",
    "North Interior Karnataka": "Deccan rain shadow", "North West Uttar Pradesh": "Doab — semi-arid",
    "Orissa": "Mahanadi basin", "Rayalaseema": "SE interior — drought prone",
    "South Interior Karnataka": "Eastern Deccan", "Tamil Nadu": "NE monsoon — opposite regime",
    "Telangana": "Godavari basin", "West Rajasthan": "Thar desert — most variable",
    "West Uttar Pradesh": "Upper Ganga plain", "Bihar": "Ganga plain — flood prone",
    "Chhattisgarh": "Mahanadi plateau", "Gangetic West Bengal": "Delta belt",
    "Ladakh": "Trans-Himalaya — hyper arid", "Sikkim": "Eastern Himalaya — steep gradient",
    "Sub-Montane West Bengal": "Duars — alluvial fan", "Uttarakhand": "Central Himalaya — cloudburst zone",
    "Vidarbha": "Vidarbha plain", "Marathwada": "Godavari–Wardha gap",
}

SEASON_LABEL = {
    "ANNUAL": "Annual", "JAS": "Monsoon (Jun–Sep)",
    "OND": "Post-monsoon (Oct–Dec)", "MAM": "Pre-monsoon (Mar–May)", "DJF": "Winter (Dec–Feb)",
}




def nav_all_states_comparison():
    st.session_state.clicked_div = None
    st.session_state.active_place_dropdown_selector = "-- Select a Subdivision --"
    st.session_state.scroll_to_comparisons = True
    st.session_state.auto_scroll_to_dossier = False
    st.session_state.last_seen_map_sig = ""

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.markdown(f"""
<div class="sidebar-header-badge">
  <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
    <div style="width:38px; height:38px; border-radius:12px; background:{T['accent_soft']}; border:1px solid {T['accent_border']}; display:flex; align-items:center; justify-content:center; font-size:20px;">
      🌧️
    </div>
    <div>
      <div style="font-size:10.5px; font-weight:800; letter-spacing:0.12em; text-transform:uppercase; color:{T['accent']};">VARSA OBSERVATORY</div>
      <div style="font-size:15px; font-weight:850; color:{T['title']};">Hydroclimatic Atlas</div>
    </div>
  </div>
  <div style="font-size:11.5px; color:{T['muted']}; line-height:1.45;">
    Meteorological Almanac of India · 1901–2026
  </div>
</div>
""", unsafe_allow_html=True)

# Navigation button to view All States Comparison directly
st.sidebar.button(
    "📊 All States Comparison",
    key="btn_sidebar_nav_comparisons",
    on_click=nav_all_states_comparison,
    use_container_width=True,
    help="Reset single-place focus and view pan-India benchmark comparisons across all 36 subdivisions",
)

st.sidebar.markdown(f"<hr style='border-color:{T['hr']}; margin:14px 0;'>", unsafe_allow_html=True)

# ── Meteorological Scope Filters ─────────────────────────────────────────────
st.sidebar.markdown(f"""
<div style="font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.08em; color:{T['muted']}; margin-bottom:6px;">
  🌐 Observatory Filters
</div>
""", unsafe_allow_html=True)

all_seasons = list(SEASON_LABEL.keys())
selected_season = st.sidebar.selectbox(
    "Precipitation Season",
    options=all_seasons,
    format_func=lambda s: SEASON_LABEL[s],
)

all_divisions = sorted(df["division"].unique().tolist())
selected_divisions = st.sidebar.multiselect(
    "Meteorological Subdivisions",
    options=all_divisions,
    default=all_divisions,
    help="Pick specific subdivisions for focused comparison or keep all for pan-India overview",
)

# Coverage: pipeline layer 1901–2015; observed IMD layer extends subdivisions to
# 2025 (2020 quality-gated) and the national monsoon to 2026 (year in progress).
YEAR_MAX_DISPLAY = 2026
year_min, year_max = int(df["year"].min()), YEAR_MAX_DISPLAY
_year_help = ("1901–2015: pipeline layer (generated, IMD-calibrated). "
              "2016–2025: observed IMD values (2020 excluded — unverifiable source table). "
              "2026: national monsoon complete (−12.6%); subdivision values not yet published.")
year_range = st.sidebar.slider("Historical Record Range", year_min, year_max, (year_min, year_max),
                               help=_year_help)

# ── Sidebar Archive Stats Card ───────────────────────────────────────────────
st.sidebar.markdown(f"""
<div class="sidebar-stats-card">
  <div style="font-size:10.5px; font-weight:800; letter-spacing:0.08em; text-transform:uppercase; color:{T['accent']}; margin-bottom:8px;">
    📊 Archive Scope
  </div>
  <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:12px;">
    <span style="color:{T['muted']};">Subdivisions:</span>
    <b style="color:{T['title']};">36 Regions</b>
  </div>
  <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:12px;">
    <span style="color:{T['muted']};">Time Span:</span>
    <b style="color:{T['title']};">125 Years (1901–2026)</b>
  </div>
  <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:12px;">
    <span style="color:{T['muted']};">Pipeline:</span>
    <b style="color:{T['title']};">1901–2015</b>
  </div>
  <div style="display:flex; justify-content:space-between; font-size:12px;">
    <span style="color:{T['muted']};">Observed IMD:</span>
    <b style="color:{T['accent']};">2016–2025 (+2026 national)</b>
  </div>
</div>
<div style="margin-top:14px; text-align:center; font-size:10.5px; color:{T['muted']}; line-height:1.5;">
  IMD Subdivisional Precipitation Series · observed layer via IMD Pune ACS + CMPG<br>
  <b>VARSA</b> · Probability &amp; Statistics · BAMAT207
</div>
""", unsafe_allow_html=True)



# ── Hero with Atmosphere Theme Toggle ─────────────────────────────────────────
c_hero_main, c_hero_toggle = st.columns([3.8, 1.2])
with c_hero_main:
    st.markdown(f"""
    <div class="hero" style="margin-bottom:0; height:100%; display:flex; flex-direction:column; justify-content:center;">
      <div class="tag">VARSA · Variability, Anomalies and Regional Statistics</div>
      <h1>Explorer — Indian Rainfall Analytics</h1>
      <p>Seasonality · variability · distributions · trends across 36 meteorological subdivisions, 1901–2026</p>
    </div>
    """, unsafe_allow_html=True)

with c_hero_toggle:
    st.markdown("<div style='height:100%; display:flex; align-items:center; justify-content:flex-end; padding-top:16px;'>", unsafe_allow_html=True)

    def on_hero_theme_toggle_change():
        st.session_state.dark_mode = bool(st.session_state.hero_theme_slider)

    is_dark_slider = st.toggle(
        "🌙 Dark Mode" if _DARK else "☀️ Warm Cream",
        value=_DARK,
        key="hero_theme_slider",
        on_change=on_hero_theme_toggle_change,
        help="Switch between Warm Cream and Midnight Dark theme",
    )
    if is_dark_slider != _DARK:
        st.session_state.dark_mode = is_dark_slider
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:1.2rem;'></div>", unsafe_allow_html=True)

# ── KPI row (real findings from VARSA) ───────────────────────────────────────
st.markdown("""
<div class="kpi-row">
  <div class="kpi green"><div class="v">75.2%</div><div class="l">of rain falls Jun–Sep</div></div>
  <div class="kpi blue"><div class="v">36</div><div class="l">meteorological subdivisions</div></div>
  <div class="kpi purple"><div class="v">125</div><div class="l">years of records (1901–2026)</div></div>
  <div class="kpi amber"><div class="v">23/115</div><div class="l">years below 90% of normal (1901–2015)</div></div>
  <div class="kpi"><div class="v">η²=0.875</div><div class="l">region explains 87% of variance</div></div>
</div>
""", unsafe_allow_html=True)

# ── Live observed-monsoon banner (2026 in progress) ──────────────────────────
_nat26 = load_national_2026()
if _nat26:
    _dep_color_ = "#dc2626" if _nat26["dep"] <= -10 else ("#d97706" if _nat26["dep"] < 0 else "#15803d")
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;background:linear-gradient(90deg,
      rgba(220,38,38,0.12), rgba(11,20,40,0));border:1.5px solid {_dep_color_}55;
      border-left:6px solid {_dep_color_};border-radius:14px;padding:12px 18px;margin:10px 0 4px;">
      <div style="font-size:1.5rem;animation:varsa-pulse 2.2s ease-in-out infinite;">🌧️</div>
      <div style="flex:1;">
        <b style="color:{_dep_color_};font-size:0.98rem;">
          {_nat26['year']} monsoon in progress — {_nat26['mm']:,.0f} mm Jun–Sep
          ({_nat26['dep']:+.1f}% of normal)
        </b>
        <div style="font-size:0.78rem;color:{T['muted']};">
          Observed IMD data (CMPG), extends the dashboard to 2026 · refresh via
          <code>python scripts/data/fetch_observed.py</code>
        </div>
      </div>
      <div class="badge blue" style="white-space:nowrap;">observed · live</div>
    </div>
    <style>@keyframes varsa-pulse{{0%,100%{{opacity:1}}50%{{opacity:0.45}}}}</style>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — INTERACTIVE INDIA RAINFALL & PHYSICAL TERRAIN MAP  (highest priority)
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="card map-card">', unsafe_allow_html=True)
st.markdown('<h2 class="sect">1 · Interactive India Rainfall &amp; Physical Terrain Map <span class="badge">Highest priority</span></h2>', unsafe_allow_html=True)
st.markdown('<p class="sect-sub"><b>India in vibrant green</b>, physical mountain slopes &amp; relief contours on zoom, regional connectivity network. <b>Click any station or line</b> to inspect its deep-dive regional dossier below.</p>', unsafe_allow_html=True)

# ── Style switcher (Ultra-Fast 60-FPS WebGL Hardware Map, 3D Sculpted Model, 3D Globe) ──
MAP_STYLE_WEBGL = "⚡ 60-FPS WebGL Hardware Map (Ultra-Fast & Responsive)"
MAP_STYLE_PRISM = "🏗️ 3D Rainfall-Height Atlas (1901–2026)"
MAP_STYLE_SKETCHFAB = "🗿 3D Sculpted India Model (Blender / Sketchfab 3D)"
MAP_STYLE_GLOBE = "🌍 3D Interactive Globe"

ALL_MAP_STYLES = [MAP_STYLE_WEBGL, MAP_STYLE_PRISM, MAP_STYLE_SKETCHFAB, MAP_STYLE_GLOBE]


map_style = st.radio(
    "Map style",
    ALL_MAP_STYLES,
    index=0,
    horizontal=True,
    key="map_style_choice",
    label_visibility="collapsed",
)
if map_style not in ALL_MAP_STYLES:
    map_style = MAP_STYLE_WEBGL

# ── Terrain Focus Presets ───────────────────────────────────────────────────
FOCUS_REGIONS = {
    "🇮🇳 All India (Subcontinent Overview)": dict(center=[22.8, 79.6], zoom=5, webgl_zoom=4.2),
    "🏔️ Himalayas & Kashmir (High Slopes & Mountain Passes)": dict(center=[32.2, 76.8], zoom=7, webgl_zoom=5.8),
    "🌿 Western Ghats (Orographic Escarpment & Rain Belt)": dict(center=[14.2, 75.2], zoom=7, webgl_zoom=5.8),
    "🌧️ Northeast & Meghalaya (Monsoon Core & Deep Gorges)": dict(center=[26.0, 92.8], zoom=7, webgl_zoom=5.8),
    "🏜️ Thar Desert & Aravalli Fringe (Arid Rain Shadow)": dict(center=[26.2, 72.8], zoom=7, webgl_zoom=5.8),
    "🌋 Deccan Plateau & Central Highlands": dict(center=[19.8, 77.8], zoom=6, webgl_zoom=5.2),
}

# Initialize map magnification state if absent
if "map_zoom_level" not in st.session_state:
    st.session_state.map_zoom_level = 5
if "last_terrain_focus" not in st.session_state:
    st.session_state.last_terrain_focus = "🇮🇳 All India (Subcontinent Overview)"

# Controls bar directly above the map
if map_style == MAP_STYLE_WEBGL:
    c_bar1, c_bar2 = st.columns([1.8, 1.2])
    with c_bar1:
        terrain_focus = st.selectbox(
            "🎯 Focus Terrain & Slopes",
            options=list(FOCUS_REGIONS.keys()),
            index=0,
            key="focus_region",
            help="Quickly fly to dramatic mountain ranges, valleys and slopes across India",
        )
    with c_bar2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        show_network = st.checkbox(
            "🕸️ Connecting Network Lines",
            value=True,
            key="show_network_lines",
            help="Display meteorological connectivity lines linking neighboring subdivisions",
        )
    st.caption("💡 **Tip:** Click on any dot to isolate that place's climate records. Use the on-map ➕ and ➖ controls to magnify into mountain slopes and elevation contours.")
elif map_style == MAP_STYLE_SKETCHFAB:
    st.markdown(f"""
    <div style="font-size:0.88rem; color:{T['text']}; padding:4px 0;">
      🗿 <b>3D Sculpted Subcontinent Model:</b> Real-time 3D topographical relief model (<code>india.fbx</code>). Complete orbital rotation with lighting and elevation shading.
    </div>
    """, unsafe_allow_html=True)
    st.caption("💡 **3D Controls:** Left-click + drag to rotate 360°. Right-click or two-finger drag to pan. Scroll wheel to zoom in/out.")
    terrain_focus = "🇮🇳 All India (Subcontinent Overview)"
    show_network = False
elif map_style == MAP_STYLE_PRISM:
    import streamlit.components.v1 as _components_prism
    c_pa, c_pb, c_pc = st.columns([1.35, 1.35, 1.3])
    with c_pa:
        prism_season = st.radio(
            "Season",
            list(PRISM_SEASONS.keys()),
            index=0,
            horizontal=True,
            key="prism_season",
            label_visibility="collapsed",
        )
    with c_pb:
        prism_year = st.slider(
            "Year", 1901, 2026, 2025, 1, key="prism_year",
            help="1901–2015: pipeline layer (generated, IMD-calibrated). 2016–2025: observed IMD Annual Climate Summary values. 2026: national monsoon only so far.",
        )
    with c_pc:
        prism_place = st.selectbox(
            "Open dossier for…",
            ["— pick a subdivision —"] + sorted(load_unified_subdivisions()["division"].unique()),
            key="prism_place",
            on_change=lambda: (
                setattr(st.session_state, "clicked_div",
                        st.session_state.get("prism_place")
                        if st.session_state.get("prism_place") != "— pick a subdivision —"
                        else st.session_state.get("clicked_div")),
            ),
        )
    st.markdown(
        "<div style='font-size:0.78rem; line-height:1.5;'>Colour = % departure from normal: "
        "<span style='color:#1d4ed8'><b>■</b> +20%+</span> "
        "<span style='color:#22c55e'><b>■</b> normal/excess</span> "
        "<span style='color:#eab308'><b>■</b> −20–0%</span> "
        "<span style='color:#f97316'><b>■</b> −40–−20%</span> "
        "<span style='color:#dc2626'><b>■</b> −40% or worse</span> · "
        "<span style='color:#788291'><b>■</b> no data</span> (the generated 1901–2015 layer "
        "omits 5 official subdivisions; 2020's table is unverifiable; 2026 is national-only) · "
        "Height = seasonal rainfall (mm). Winter definitions differ slightly between layers "
        "(pipeline Dec–Feb, observed Jan–Feb).</div>",
        unsafe_allow_html=True,
    )
    terrain_focus = "🇮🇳 All India (Subcontinent Overview)"
    show_network = False
else:  # MAP_STYLE_GLOBE
    c_bar1, c_bar2 = st.columns([2.0, 1.0])
    with c_bar1:
        st.markdown(f"""
        <div style="font-size:0.88rem; color:{T['text']}; padding-top:6px;">
          🌍 <b>3D Interactive Globe:</b> Orthographic planetary view centered on India with atmospheric connectivity arcs and seasonal rainfall spheres.
        </div>
        """, unsafe_allow_html=True)
    with c_bar2:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        show_network = st.checkbox(
            "🕸️ Atmospheric Network Links",
            value=True,
            key="show_network_lines_globe",
            help="Display spatial network arcs",
        )
    st.caption("💡 **Tip:** Click any station dot to isolate that place's climate records below.")
    terrain_focus = "🇮🇳 All India (Subcontinent Overview)"

# ── Aggregate stats per division (within year filter) ────────────────────────
map_df = df[(df["season"] == "ANNUAL") & df["division"].isin(selected_divisions)]
map_df = map_df[(map_df["year"] >= year_range[0]) & (map_df["year"] <= year_range[1])]
# Extend with observed IMD annual values (2016–2025) for every selected division
# that maps to a canonical IMD subdivision. Annual = calendar year in both layers.
# Divisions that fold into one IMD subdivision (Ladakh, Sikkim, …) share the
# observed decade as a documented proxy; every row keeps its layer tag.
if year_range[1] > 2015:
    _obs_map_frames = []
    for _pd_name in map_df["division"].unique():
        _cn = PIPE_TO_CANON.get(_pd_name)
        if _cn:
            _o = observed_rows_for_division(_cn)
            if not _o.empty:
                _o = _o[(_o["season"] == "ANNUAL")
                        & (_o["year"] >= year_range[0]) & (_o["year"] <= year_range[1])].copy()
                _o["division"] = _pd_name
                _obs_map_frames.append(_o)
    if _obs_map_frames:
        map_df = pd.concat([map_df, pd.concat(_obs_map_frames, ignore_index=True)], ignore_index=True)
agg = map_df.groupby("division")["rainfall_mm"].agg(["mean", "std", "min", "max", "count"]).reset_index()
agg.columns = ["division", "mean_rain", "std_rain", "min_rain", "max_rain", "n"]
agg["cv"] = (agg["std_rain"] / agg["mean_rain"]) * 100
agg["lat"], agg["lon"] = zip(*[DIV_COORDS[d] for d in agg["division"]])
agg["desc"] = agg["division"].map(DIV_DESC)

# Compute drought frequency (percentage of years with rainfall < 75% of normal)
drought_counts = {}
for d in agg["division"]:
    sub = map_df[map_df["division"] == d]
    m_val = float(sub["rainfall_mm"].mean()) if len(sub) else 0
    # IMD Drought Year benchmark: annual rainfall < 75% of normal (deficit >= 25%)
    d_count = int((sub["rainfall_mm"] < m_val * 0.75).sum()) if m_val > 0 else 0
    drought_counts[d] = d_count

agg["drought_years"] = agg["division"].map(drought_counts).fillna(0)
agg["drought_pct"] = (agg["drought_years"] / agg["n"].clip(lower=1)) * 100

slopes = {}
for d in agg["division"]:
    _sub = map_df[map_df["division"] == d]
    if len(_sub) > 2:
        slopes[d] = float(np.polyfit(_sub["year"], _sub["rainfall_mm"], 1)[0])
agg["trend"] = agg["division"].map(slopes).fillna(0)
agg["trend_txt"] = agg["trend"].apply(lambda t: f"{t:+.1f} mm/yr")

# Climatological IMD Drought Vulnerability Classification:
# HIGH: Severe variability (CV >= 35%) OR chronic drought occurrence (drought_pct >= 25% and mean < 900mm)
# LOW: High rainfall stability (CV < 23% and drought_pct < 15%) OR deep rainforest belts (mean >= 2000mm with CV < 25%)
# MEDIUM: Moderate vulnerability (intermediate variability and periodic droughts)
def _calc_drought_risk(row):
    cv = row["cv"]
    d_pct = row["drought_pct"]
    mean_r = row["mean_rain"]
    if cv >= 35.0 or (d_pct >= 25.0 and mean_r < 900.0):
        return "HIGH"
    elif (cv < 23.0 and d_pct < 15.0) or (mean_r >= 2000.0 and cv < 25.0):
        return "LOW"
    else:
        return "MEDIUM"

agg["risk"] = agg.apply(_calc_drought_risk, axis=1)
agg = agg.sort_values("mean_rain").reset_index(drop=True)

# ── Clicked region state (wiki-link behaviour) ───────────────────────────────
if "clicked_div" not in st.session_state:
    st.session_state.clicked_div = None

# Theme-aware plotly ink
_TEXT_COLOR = "#000000" if not _DARK else "#f8fafc"
_TITLE_COLOR = "#000000" if not _DARK else "#ffffff"
_MUTED_COLOR = "#334155" if not _DARK else "#94a3b8"
_GRID_C = "rgba(0, 0, 0, 0.08)" if not _DARK else "rgba(255, 255, 255, 0.08)"
_AXIS_LINE = "rgba(0, 0, 0, 0.22)" if not _DARK else "rgba(255, 255, 255, 0.20)"
_PLOT_TEMPLATE = "plotly_white" if not _DARK else "plotly_dark"
_FG = _TEXT_COLOR

_PAPER = dict(
    template=_PLOT_TEMPLATE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'Outfit', 'Plus Jakarta Sans', 'Inter', sans-serif", color=_TEXT_COLOR),
    title_font=dict(color=_TITLE_COLOR, size=15, family="'Outfit', 'Plus Jakarta Sans', sans-serif"),
    legend_font=dict(color=_TEXT_COLOR),
)

def render_risk_table(df, is_dark):
    bg_table = "rgba(255, 253, 247, 0.95)" if not is_dark else "rgba(15, 23, 42, 0.90)"
    bg_th = "#f5ebd7" if not is_dark else "#1e293b"
    text_c = "#000000" if not is_dark else "#f8fafc"
    border_c = "rgba(175, 142, 95, 0.28)" if not is_dark else "rgba(255, 255, 255, 0.08)"
    row_even = "rgba(120, 95, 60, 0.04)" if not is_dark else "rgba(255, 255, 255, 0.02)"
    
    rows = []
    for i, r in df.iterrows():
        div = r["Division"]
        mean_val = f"{float(r['Mean (mm)']):,.0f}"
        cv_val = f"{float(r['CV %']):.1f}%"
        d_freq = f"{float(r['Drought frequency %']):.1f}%"
        worst_val = f"{float(r['Worst year (mm)']):,.0f}"
        risk = str(r["Risk"]).upper()
        
        if risk == "HIGH":
            badge = '<span style="background:#fee2e2;color:#991b1b;border:1px solid #f87171;padding:3px 10px;border-radius:999px;font-weight:750;font-size:0.75rem;">HIGH</span>' if not is_dark else '<span style="background:rgba(239,68,68,0.22);color:#fca5a5;border:1px solid #ef4444;padding:3px 10px;border-radius:999px;font-weight:750;font-size:0.75rem;">HIGH</span>'
        elif risk == "MEDIUM":
            badge = '<span style="background:#fef3c7;color:#92400e;border:1px solid #fcd34d;padding:3px 10px;border-radius:999px;font-weight:750;font-size:0.75rem;">MEDIUM</span>' if not is_dark else '<span style="background:rgba(245,158,11,0.22);color:#fde68a;border:1px solid #f59e0b;padding:3px 10px;border-radius:999px;font-weight:750;font-size:0.75rem;">MEDIUM</span>'
        else:
            badge = '<span style="background:#dcfce7;color:#166534;border:1px solid #86efac;padding:3px 10px;border-radius:999px;font-weight:750;font-size:0.75rem;">LOW</span>' if not is_dark else '<span style="background:rgba(34,197,94,0.22);color:#86efac;border:1px solid #22c55e;padding:3px 10px;border-radius:999px;font-weight:750;font-size:0.75rem;">LOW</span>'
            
        bg_row = row_even if (i % 2 == 1) else "transparent"
        rows.append(
            f'<tr style="background:{bg_row};border-bottom:1px solid {border_c};">'
            f'<td style="padding:9px 14px;font-weight:700;color:{text_c};">{div}</td>'
            f'<td style="padding:9px 14px;color:{text_c};text-align:right;">{mean_val}</td>'
            f'<td style="padding:9px 14px;color:{text_c};text-align:right;font-weight:700;">{cv_val}</td>'
            f'<td style="padding:9px 14px;color:{text_c};text-align:right;">{d_freq}</td>'
            f'<td style="padding:9px 14px;color:{text_c};text-align:right;">{worst_val}</td>'
            f'<td style="padding:9px 14px;text-align:center;">{badge}</td>'
            f'</tr>'
        )
        
    th_html = (
        f'<tr style="background:{bg_th};">'
        f'<th style="padding:11px 14px;text-align:left;color:{text_c};font-weight:800;font-size:0.86rem;letter-spacing:0.02em;">DIVISION</th>'
        f'<th style="padding:11px 14px;text-align:right;color:{text_c};font-weight:800;font-size:0.86rem;letter-spacing:0.02em;">NORMAL MEAN (MM)</th>'
        f'<th style="padding:11px 14px;text-align:right;color:{text_c};font-weight:800;font-size:0.86rem;letter-spacing:0.02em;">CV %</th>'
        f'<th style="padding:11px 14px;text-align:right;color:{text_c};font-weight:800;font-size:0.86rem;letter-spacing:0.02em;">DROUGHT FREQ (&lt;75%)</th>'
        f'<th style="padding:11px 14px;text-align:right;color:{text_c};font-weight:800;font-size:0.86rem;letter-spacing:0.02em;">DRIEST RECORD (MM)</th>'
        f'<th style="padding:11px 14px;text-align:center;color:{text_c};font-weight:800;font-size:0.86rem;letter-spacing:0.02em;">RISK TIER</th>'
        f'</tr>'
    )
    tbody_html = "".join(rows)
    return (
        f'<div style="max-height:420px;overflow-y:auto;border-radius:18px;border:1px solid {border_c};background:{bg_table};box-shadow:0 4px 18px rgba(0,0,0,0.06);margin-bottom:1.5rem;">'
        f'<table style="width:100%;border-collapse:collapse;font-family:\'Outfit\',\'Plus Jakarta Sans\',sans-serif;font-size:0.90rem;">'
        f'<thead style="position:sticky;top:0;background:{bg_th};z-index:2;box-shadow:0 1px 3px rgba(0,0,0,0.08);">{th_html}</thead>'
        f'<tbody>{tbody_html}</tbody>'
        f'</table></div>'
    )

def render_extremes_table(df, is_dark, is_wet=True):
    bg_table = "rgba(255, 253, 247, 0.95)" if not is_dark else "rgba(15, 23, 42, 0.90)"
    bg_th = "#f5ebd7" if not is_dark else "#1e293b"
    text_c = "#000000" if not is_dark else "#f8fafc"
    border_c = "rgba(175, 142, 95, 0.28)" if not is_dark else "rgba(255, 255, 255, 0.08)"
    row_even = "rgba(120, 95, 60, 0.04)" if not is_dark else "rgba(255, 255, 255, 0.02)"
    badge_bg = "#dcfce7" if (is_wet and not is_dark) else "#fee2e2" if (not is_wet and not is_dark) else "rgba(34,197,94,0.22)" if is_wet else "rgba(239,68,68,0.22)"
    badge_fg = "#166534" if (is_wet and not is_dark) else "#991b1b" if (not is_wet and not is_dark) else "#86efac" if is_wet else "#fca5a5"
    badge_border = "#86efac" if (is_wet and not is_dark) else "#fca5a5" if (not is_wet and not is_dark) else "#22c55e" if is_wet else "#ef4444"
    
    rows = []
    for i, r in df.iterrows():
        yr = int(r["Year"])
        rain = f"{float(r['Rainfall (mm)']):,.0f} mm"
        anom = str(r[df.columns[2]])
        bg_row = row_even if (i % 2 == 1) else "transparent"
        rows.append(
            f'<tr style="background:{bg_row};border-bottom:1px solid {border_c};">'
            f'<td style="padding:9px 12px;font-weight:750;color:{text_c};">{yr}</td>'
            f'<td style="padding:9px 12px;color:{text_c};text-align:right;font-weight:600;">{rain}</td>'
            f'<td style="padding:9px 12px;text-align:right;"><span style="background:{badge_bg};color:{badge_fg};border:1px solid {badge_border};padding:3px 9px;border-radius:999px;font-weight:750;font-size:0.78rem;">{anom}</span></td>'
            f'</tr>'
        )
    
    col_name = "ANOMALY VS NORMAL" if is_wet else "DEFICIT VS NORMAL"
    th_html = (
        f'<tr style="background:{bg_th};">'
        f'<th style="padding:10px 12px;text-align:left;color:{text_c};font-weight:800;font-size:0.82rem;letter-spacing:0.02em;">YEAR</th>'
        f'<th style="padding:10px 12px;text-align:right;color:{text_c};font-weight:800;font-size:0.82rem;letter-spacing:0.02em;">RAINFALL</th>'
        f'<th style="padding:10px 12px;text-align:right;color:{text_c};font-weight:800;font-size:0.82rem;letter-spacing:0.02em;">{col_name}</th>'
        f'</tr>'
    )
    tbody_html = "".join(rows)
    return (
        f'<div style="border-radius:16px;border:1px solid {border_c};background:{bg_table};box-shadow:0 3px 12px rgba(0,0,0,0.05);margin-bottom:1rem;overflow:hidden;">'
        f'<table style="width:100%;border-collapse:collapse;font-family:\'Outfit\',\'Plus Jakarta Sans\',sans-serif;font-size:0.88rem;">'
        f'<thead style="background:{bg_th};">{th_html}</thead>'
        f'<tbody>{tbody_html}</tbody>'
        f'</table></div>'
    )

# Shared hover template
HOVER = ("<b>%{customdata[0]}</b><br>"
         "Mean annual: %{customdata[1]:,.0f} mm<br>"
         "CV: %{customdata[2]:.1f}%<br>"
         "Trend: %{customdata[3]}<br>"
         "Drought risk: %{customdata[4]}<br>"
         "<i>%{customdata[5]}</i><extra></extra>")

# Lush wet→dry green ramp for markers and globe
SCALE_GREEN = [
    [0.0, "#dcfce7"],
    [0.2, "#86efac"],
    [0.45, "#22c55e"],
    [0.72, "#15803d"],
    [1.0, "#052e16"],
]

def _capture(ev):
    try:
        pts = ev.selection.points if ev and ev.selection else []
        if pts:
            cd = pts[0].get("customdata")
            if cd is not None and len(cd) > 0:
                return str(cd[0])
    except Exception:
        return None
    return None

# ── Spatial Connectivity Network (Connecting Lines) ─────────────────────────
@st.cache_data
def _compute_connectivity(coords_dict, k=3, max_dist=9.0):
    names = list(coords_dict.keys())
    pts = np.array([coords_dict[n] for n in names])
    edges = set()
    for i in range(len(pts)):
        dists = np.hypot(pts[:, 0] - pts[i, 0], pts[:, 1] - pts[i, 1])
        order = np.argsort(dists)
        count = 0
        for j in order[1:]:
            if dists[j] <= max_dist and count < k:
                edges.add(tuple(sorted((int(i), int(j)))))
                count += 1
    return names, pts, list(edges)

NETWORK_NAMES, NETWORK_PTS, NETWORK_EDGES = _compute_connectivity(DIV_COORDS, k=3, max_dist=9.0)

def _link_segments_3d(names, pts, edges):
    lo, la = [], []
    for i, j in edges:
        lat1, lon1 = pts[i]
        lat2, lon2 = pts[j]
        lo += [lon1, lon2, None]
        la += [lat1, lat2, None]
    return lo, la

def _green_ramp(v, lo, hi):
    """Rich lush green ramp from fresh pale mint to deep rainforest emerald."""
    if hi <= lo:
        f = 0.5
    else:
        f = float(np.clip((v - lo) / (hi - lo), 0, 1))
    palette = [
        (0.00, (167, 243, 208)),  # Fresh mint
        (0.30, (74, 222, 128)),   # Bright spring green
        (0.60, (22, 163, 74)),    # Grass emerald
        (0.85, (21, 128, 61)),    # Deep forest green
        (1.00, (5, 46, 22)),      # Deepest rainforest
    ]
    for idx in range(len(palette) - 1):
        x0, c0 = palette[idx]
        x1, c1 = palette[idx + 1]
        if x0 <= f <= x1:
            t = (f - x0) / (x1 - x0 + 1e-9)
            r = int(round(c0[0] + (c1[0] - c0[0]) * t))
            g = int(round(c0[1] + (c1[1] - c0[1]) * t))
            b = int(round(c0[2] + (c1[2] - c0[2]) * t))
            return f"#{r:02x}{g:02x}{b:02x}"
    return "#15803d"

def _geo_figure():
    """Lush Green India on a 3D globe with glowing connecting network lines."""
    fig = go.Figure()
    # Vibrant Green India polygon outline and fill
    fig.add_trace(go.Choropleth(
        locations=["IND"], locationmode="country names", z=[1],
        colorscale=[[0, "rgba(22, 163, 74, 0.45)"], [1, "rgba(22, 163, 74, 0.75)"]],
        showscale=False,
        marker_line_color="#15803d" if not _DARK else "#22c55e",
        marker_line_width=2.6,
        hoverinfo="skip", name="India",
    ))
    custom = agg[["division", "mean_rain", "cv", "trend_txt", "risk", "desc"]].values
    sizes = 9 + (agg["mean_rain"] / agg["mean_rain"].max()) * 36
    
    # 71 Connecting network lines in glowing green
    lo, la = _link_segments_3d(NETWORK_NAMES, NETWORK_PTS, NETWORK_EDGES)
    fig.add_trace(go.Scattergeo(
        lat=la, lon=lo, mode="lines",
        line=dict(width=1.5, color="rgba(34, 197, 94, 0.75)"),
        hoverinfo="skip", showlegend=False, name="Network Links",
    ))
    # Dark 3D base bevel
    fig.add_trace(go.Scattergeo(
        lat=agg["lat"], lon=agg["lon"], mode="markers",
        marker=dict(size=sizes + 8, color="rgba(6, 14, 10, 0.70)",
                    line=dict(width=1, color="rgba(10, 20, 14, 0.9)")),
        hoverinfo="skip", showlegend=False,
    ))
    # Green-shaded dots sized by rainfall
    fig.add_trace(go.Scattergeo(
        lat=agg["lat"], lon=agg["lon"], mode="markers",
        marker=dict(size=sizes, color=agg["mean_rain"], colorscale=SCALE_GREEN,
                    showscale=True, coloraxis="coloraxis",
                    line=dict(width=1.8, color="#f0fdf4"), opacity=0.98),
        customdata=custom, hovertemplate=HOVER,
        name="Subdivisions", showlegend=False,
    ))
    # Distinct blue marker & halo for active selected division (reverts to green when shifted)
    if st.session_state.clicked_div:
        sel = agg[agg["division"] == st.session_state.clicked_div]
        if len(sel):
            sel_idx = sel.index[0]
            sel_size = float(sizes[sel_idx])
            fig.add_trace(go.Scattergeo(
                lat=sel["lat"], lon=sel["lon"], mode="markers",
                marker=dict(size=sel_size + 28, color="rgba(14, 165, 233, 0.35)"),
                showlegend=False, hoverinfo="skip",
            ))
            fig.add_trace(go.Scattergeo(
                lat=sel["lat"], lon=sel["lon"], mode="markers+text",
                marker=dict(
                    size=sel_size + 6,
                    color="#0284c7" if not _DARK else "#38bdf8",
                    line=dict(width=3.2, color="#ffffff"),
                    opacity=1.0,
                ),
                text=[f"📍 {st.session_state.clicked_div}"],
                textposition="top center",
                textfont=dict(size=12, color="#0369a1" if not _DARK else "#7dd3fc", family="Outfit, sans-serif"),
                showlegend=False, hoverinfo="skip",
            ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=24), height=670,
        coloraxis_colorbar=dict(
            title=dict(text="Annual mm", font=dict(color=_TEXT_COLOR)),
            thickness=14, len=0.62,
            tickfont=dict(color=_TEXT_COLOR),
        ),
        showlegend=False, **_PAPER,
    )
    fig.update_geos(
        visible=False, resolution=50, bgcolor="rgba(0,0,0,0)",
        projection=dict(type="orthographic", scale=1.05,
                        rotation=dict(lon=79, lat=21)),
        center=dict(lon=79, lat=21),
        lataxis_range=[-60, 60], lonaxis_range=[-180, 180],
        showcountries=True, countrycolor="#334155" if _DARK else "#c4b595",
        showland=True, landcolor="#0c1723" if _DARK else "#f1e5cc",
        showocean=True, oceancolor="#060c14" if _DARK else "#d6e5ef",
        showlakes=True, lakecolor="#091422" if _DARK else "#d6e5ef",
        showrivers=True, rivercolor="#16253b" if _DARK else "#a7c4d7",
    )
    return fig

def _webgl_map_figure(focus_key="🇮🇳 All India (Subcontinent Overview)", show_net=True):
    """High-speed GPU-accelerated WebGL MapLibre map of India."""
    fig = go.Figure()

    # 1. India Official Boundary Layers (GeoJSON)
    india_geojson = get_india_geojson()
    layers = []
    if india_geojson:
        layers.append(dict(
            sourcetype="geojson",
            source=india_geojson,
            type="fill",
            color="rgba(22, 163, 74, 0.12)" if not _DARK else "rgba(34, 197, 94, 0.15)",
        ))
        layers.append(dict(
            sourcetype="geojson",
            source=india_geojson,
            type="line",
            color="#15803d" if not _DARK else "#22c55e",
            line=dict(width=2.5),
        ))

    # 2. Regional Connectivity Network lines
    if show_net:
        lo, la = _link_segments_3d(NETWORK_NAMES, NETWORK_PTS, NETWORK_EDGES)
        fig.add_trace(go.Scattermap(
            lat=la, lon=lo, mode="lines",
            line=dict(width=1.6, color="rgba(22, 163, 74, 0.65)" if not _DARK else "rgba(74, 222, 128, 0.70)"),
            hoverinfo="skip", showlegend=False, name="Network Links",
        ))

    # 3. Base dark bevel for markers
    sizes = 10 + (agg["mean_rain"] / agg["mean_rain"].max()) * 26
    fig.add_trace(go.Scattermap(
        lat=agg["lat"], lon=agg["lon"], mode="markers",
        marker=dict(size=sizes + 6, color="rgba(10, 30, 18, 0.65)"),
        hoverinfo="skip", showlegend=False,
    ))

    # 4. Subdivision dots: All unselected in green, selected division in vibrant blue
    custom = agg[["division", "mean_rain", "cv", "trend_txt", "risk", "desc"]].values
    cd_selected = st.session_state.get("clicked_div")

    if cd_selected and cd_selected in agg["division"].values:
        unsel_mask = (agg["division"] != cd_selected).values
        sel_mask = (agg["division"] == cd_selected).values

        unsel_agg = agg[unsel_mask]
        unsel_sizes = sizes[unsel_mask]
        unsel_custom = custom[unsel_mask]

        sel_agg = agg[sel_mask]
        sel_idx = sel_agg.index[0]
        sel_size = float(sizes[sel_idx])
        sel_custom = [custom[sel_idx]]

        # Unselected subdivisions: Always GREEN
        fig.add_trace(go.Scattermap(
            lat=unsel_agg["lat"], lon=unsel_agg["lon"], mode="markers",
            marker=dict(
                size=unsel_sizes,
                color=unsel_agg["mean_rain"],
                colorscale=SCALE_GREEN,
                showscale=True,
                coloraxis="coloraxis",
                opacity=0.98,
            ),
            customdata=unsel_custom,
            hovertemplate=HOVER,
            name="Subdivisions",
            showlegend=False,
        ))

        # Selected subdivision: Exclusively BLUE with glowing cyan/blue halos and pin label
        fig.add_trace(go.Scattermap(
            lat=sel_agg["lat"], lon=sel_agg["lon"], mode="markers",
            marker=dict(size=sel_size + 28, color="rgba(14, 165, 233, 0.40)"),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scattermap(
            lat=sel_agg["lat"], lon=sel_agg["lon"], mode="markers",
            marker=dict(size=sel_size + 14, color="rgba(56, 189, 248, 0.70)"),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scattermap(
            lat=sel_agg["lat"], lon=sel_agg["lon"], mode="markers+text",
            marker=dict(
                size=sel_size + 6,
                color="#0284c7" if not _DARK else "#38bdf8",
                opacity=1.0,
            ),
            text=[f"📍 {cd_selected}"],
            textposition="top center",
            textfont=dict(
                size=13,
                color="#0369a1" if not _DARK else "#38bdf8",
                family="Outfit, Inter, sans-serif",
            ),
            customdata=sel_custom,
            hovertemplate=HOVER,
            name=cd_selected,
            showlegend=False,
        ))
    else:
        # No division selected: Render all 36 subdivisions in GREEN
        fig.add_trace(go.Scattermap(
            lat=agg["lat"], lon=agg["lon"], mode="markers",
            marker=dict(
                size=sizes,
                color=agg["mean_rain"],
                colorscale=SCALE_GREEN,
                showscale=True,
                coloraxis="coloraxis",
                opacity=0.98,
            ),
            customdata=custom,
            hovertemplate=HOVER,
            name="Subdivisions",
            showlegend=False,
        ))

    # Focus configuration
    f_cfg = FOCUS_REGIONS.get(focus_key, FOCUS_REGIONS["🇮🇳 All India (Subcontinent Overview)"])
    c_lat, c_lon = f_cfg["center"]
    z_lvl = f_cfg.get("webgl_zoom", 4.2)

    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=32),
        height=660,
        map=dict(
            style="carto-voyager" if not _DARK else "carto-darkmatter",
            center=dict(lat=c_lat, lon=c_lon),
            zoom=z_lvl,
            layers=layers,
        ),
        coloraxis=dict(
            colorscale=SCALE_GREEN,
            colorbar=dict(
                title=dict(text="Annual mm", font=dict(color=_TEXT_COLOR)),
                thickness=14, len=0.62,
                tickfont=dict(color=_TEXT_COLOR),
            ),
        ),
        showlegend=False,
        **_PAPER,
    )
    return fig

# ── Render the Chosen Map Style (Ultra-Fast WebGL, 3D Sculpted Model, 3D Globe) ──
_picked = None

if map_style == MAP_STYLE_WEBGL:
    fig_map = _webgl_map_figure(focus_key=terrain_focus, show_net=show_network)
    ev = st.plotly_chart(
        fig_map,
        on_select="rerun",
        key="india_webgl_map",
        selection_mode="points",
        use_container_width=True,
        theme=None,
    )
    _picked = _capture(ev)
elif map_style == MAP_STYLE_PRISM:
    import pydeck as pdk
    feats, _rows = prism_frame(prism_season, prism_year)
    if feats is None:
        st.info("Subdivision boundaries not built yet — run: "
                "`python scripts/data/build_subdivision_geo.py`")
    else:
        layer = pdk.Layer(
            "PolygonLayer",
            feats,
            get_polygon="polygon",
            get_elevation="mm",
            elevation_scale=0.55,
            extruded=True,
            get_fill_color="color",
            get_line_color=[10, 16, 28],
            line_width_min_pixels=1,
            pickable=True,
            auto_highlight=True,
        )
        view = pdk.ViewState(latitude=22.6, longitude=79.6, zoom=3.85,
                             pitch=54, bearing=-14, max_zoom=9)
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            map_provider=None,
            tooltip={
                "html": ("<b>{name}</b><br/>{mm:,.0f} mm"
                         "<br/>% dep: {dep}<br/><i>{layer}</i>"),
                "style": {"background": "rgba(11,20,40,0.9)", "color": "#E8EEF7",
                          "font-family": "Outfit, sans-serif", "border-radius": "8px"},
            },
        )
        st.pydeck_chart(deck, use_container_width=True, key="india_prism_map", height=620)
        nat26 = load_national_2026()
        if prism_year == 2026 and nat26:
            st.info(f"2026 subdivision values are not published yet — all-India "
                    f"monsoon so far: **{nat26['mm']:,.0f} mm ({nat26['dep']:+.1f}% of normal)** "
                    f"(observed IMD, updates with every data refresh).")
elif map_style == MAP_STYLE_SKETCHFAB:
    import streamlit.components.v1 as components
    st.markdown(f"""
    <div style="background:{'rgba(15,23,42,0.7)' if _DARK else 'rgba(255,253,247,0.85)'}; border:1.5px solid {'rgba(34,197,94,0.35)' if _DARK else 'rgba(175,142,95,0.35)'}; border-radius:18px; padding:12px 18px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:1.3rem;">🗿</span>
        <div>
          <b style="color:{'#22c55e' if _DARK else '#15803d'}; font-size:14px;">3D Sculpted India Topographic Relief (Source Model: india.fbx)</b>
          <div style="font-size:12px; color:{T['muted']};">GPU WebGL 3D render · 360° mouse orbit, dynamic surface normals &amp; mountain escarpment textures</div>
        </div>
      </div>
      <div style="display:flex; gap:8px;">
        <span class="badge blue">WebGL 3D</span>
        <span class="badge">Model: india.fbx</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    components.html("""
    <div style="width:100%; height:660px; border-radius:20px; overflow:hidden; box-shadow:0 12px 36px rgba(0,0,0,0.35); border:1.8px solid #22c55e; background:#070b12;">
      <iframe 
        title="India 3D Sculpted Model" 
        frameborder="0" 
        allowfullscreen 
        mozallowfullscreen="true" 
        webkitallowfullscreen="true" 
        allow="autoplay; fullscreen; xr-spatial-tracking" 
        xr-spatial-tracking 
        execution-while-out-of-viewport 
        execution-while-not-rendered 
        web-share 
        width="100%" 
        height="100%" 
        src="https://sketchfab.com/models/c86b16b141e54d2d844b740941bedb0c/embed?autostart=1&ui_controls=1&ui_infos=0&ui_watermark=0&transparent=1">
      </iframe>
    </div>
    """, height=670)
else:  # MAP_STYLE_GLOBE
    fig_map = _geo_figure()
    ev = st.plotly_chart(
        fig_map,
        on_select="rerun",
        key="india_globe_map",
        selection_mode="points",
        use_container_width=True,
        theme=None,
    )
    _picked = _capture(ev)


# ── Robust State Synchronization ──
# Initial open: NO state data opened unless the user clicks!
if "clicked_div" not in st.session_state:
    st.session_state.clicked_div = None
elif st.session_state.clicked_div is not None and st.session_state.clicked_div not in all_divisions:
    st.session_state.clicked_div = None

if "active_place_dropdown_selector" not in st.session_state:
    st.session_state.active_place_dropdown_selector = "-- Select a Subdivision --"
if "last_seen_map_sig" not in st.session_state:
    st.session_state.last_seen_map_sig = ""

# Synchronize clicked place ONLY on a fresh map click event (never overwritten by buttons)
if _picked:
    clk_sig = f"plotly_{_picked}"
    if clk_sig != st.session_state.get("last_seen_map_sig"):
        st.session_state.last_seen_map_sig = clk_sig
        st.session_state.clicked_div = _picked
        st.session_state.active_place_dropdown_selector = _picked
        st.session_state.auto_scroll_to_dossier = True
        st.rerun()

# Guarantee selectbox state matches clicked_div BEFORE widget instantiation
target_select = st.session_state.clicked_div if st.session_state.clicked_div else "-- Select a Subdivision --"
if st.session_state.get("active_place_dropdown_selector") != target_select:
    st.session_state.active_place_dropdown_selector = target_select

CD = st.session_state.clicked_div

# Callbacks for instant, error-free widget state transitions
def on_place_dropdown_change():
    new_val = st.session_state.active_place_dropdown_selector
    if new_val and new_val != "-- Select a Subdivision --":
        st.session_state.clicked_div = new_val
        st.session_state.auto_scroll_to_dossier = True
    else:
        st.session_state.clicked_div = None
        st.session_state.scroll_to_comparisons = True

def on_quick_jump_click(place_name):
    st.session_state.clicked_div = place_name
    st.session_state.active_place_dropdown_selector = place_name
    st.session_state.auto_scroll_to_dossier = True

# Place Selector and Quick-Jumps directly under the map with clean spacing and no widget collision
st.markdown("<div style='margin-top:1.4rem; clear:both;'></div>", unsafe_allow_html=True)
c_sel1, c_sel2 = st.columns([1.25, 2.75], gap="large")
with c_sel1:
    dropdown_options = ["-- Select a Subdivision --"] + all_divisions
    st.selectbox(
        "📍 Active Place (click any dot on map or select here):",
        dropdown_options,
        key="active_place_dropdown_selector",
        on_change=on_place_dropdown_change,
    )

with c_sel2:
    st.markdown("<p style='font-size:0.82rem; font-weight:700; color:" + T['muted'] + "; margin:0 0 6px;'>⚡ Quick Jump to Popular Regions:</p>", unsafe_allow_html=True)
    # Extra width allocated for Uttarakhand so text is never cramped or clipped
    q_cols = st.columns([1.0, 1.45, 1.05, 1.25, 1.1, 1.2])
    q_places = [
        ("🌴 Kerala", "Kerala"),
        ("🏔️ Uttarakhand", "Uttarakhand"),
        ("🌧️ Assam", "Assam & Meghalaya"),
        ("🏜️ Rajasthan", "West Rajasthan"),
        ("🌊 Konkan", "Konkan & Goa"),
        ("🏔️ Himachal", "Himachal Pradesh"),
    ]
    for qcol, (qlbl, qdiv) in zip(q_cols, q_places):
        with qcol:
            st.button(
                qlbl,
                key=f"q_{qdiv.replace(' ', '_').replace('&', '_')}",
                on_click=on_quick_jump_click,
                args=(qdiv,),
                use_container_width=True,
            )

# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — DEDICATED PLACE CLIMATE DOSSIER: THAT PLACE ONLY (NO COMPARISON)
# ════════════════════════════════════════════════════════════════════════════
if CD and CD in df["division"].unique():
    # Pipeline layer (1901–2015) + observed IMD annual rows (2016–2025) where the
    # division maps to a canonical IMD subdivision. Annual = calendar year in both
    # layers, so merging is definitional-safe; every row keeps its layer tag.
    ann_c = df[(df["division"] == CD) & (df["season"] == "ANNUAL")].copy().sort_values("year")
    _canon = PIPE_TO_CANON.get(CD)
    _obs_ann = observed_rows_for_division(_canon)
    if not _obs_ann.empty:
        ann_c = pd.concat([ann_c, _obs_ann], ignore_index=True)
    ann_c = ann_c[(ann_c["year"] >= year_range[0]) & (ann_c["year"] <= year_range[1])]
    ann_c = ann_c.sort_values("year").reset_index(drop=True)
    _is_obs = (ann_c.get("layer") == "observed IMD") if "layer" in ann_c.columns else pd.Series(False, index=ann_c.index)
    n_years = len(ann_c)
    n_obs_years = int(_is_obs.sum())
    span_lo, span_hi = int(ann_c["year"].min()), int(ann_c["year"].max())
    span_years = span_hi - span_lo + 1
    mean_c = ann_c["rainfall_mm"].mean()
    std_c = ann_c["rainfall_mm"].std()
    cv_c = std_c / mean_c * 100 if mean_c else 0
    min_c = ann_c["rainfall_mm"].min()
    max_c = ann_c["rainfall_mm"].max()
    p5 = np.percentile(ann_c["rainfall_mm"], 5) if n_years else 0
    p95 = np.percentile(ann_c["rainfall_mm"], 95) if n_years else 0
    wet_year = int(ann_c.loc[ann_c["rainfall_mm"].idxmax(), "year"]) if n_years else "-"
    dry_year = int(ann_c.loc[ann_c["rainfall_mm"].idxmin(), "year"]) if n_years else "-"
    wet_val = float(ann_c.loc[ann_c["rainfall_mm"].idxmax(), "rainfall_mm"]) if n_years else 0
    dry_val = float(ann_c.loc[ann_c["rainfall_mm"].idxmin(), "rainfall_mm"]) if n_years else 0

    # Trend for this place
    x_c = ann_c["year"].values.astype(float)
    y_c = ann_c["rainfall_mm"].values
    slope_c, intercept_c = np.polyfit(x_c, y_c, 1) if n_years > 2 else (0, 0)
    r_c = float(np.corrcoef(x_c, y_c)[0, 1]) if n_years > 2 else 0
    t_c = r_c * np.sqrt(max(n_years - 2, 1) / max(1 - r_c**2, 1e-9)) if n_years > 3 else 0
    p_c = float(2 * _stats.t.sf(abs(t_c), max(n_years - 2, 1))) if n_years > 3 else 1.0
    lat_c, lon_c = DIV_COORDS[CD]

    # Seasonal breakdown for this place. Monsoon/pre/post-monsoon share IMD's
    # definition in both layers and are extended with observed rows; WINTER is
    # Dec–Feb in the pipeline but Jan–Feb in the observed layer, so it stays
    # pipeline-only (1901–2015) and is labelled as such.
    seas_c = df[(df["division"] == CD) & (df["season"] != "ANNUAL")]
    _canon_seas = observed_rows_for_division(_canon)
    if not _canon_seas.empty:
        _canon_seas = _canon_seas[_canon_seas["season"] != "ANNUAL"]
        _canon_seas["division"] = CD  # keep the dossier keyed on the pipeline name
        seas_c = pd.concat([seas_c, _canon_seas], ignore_index=True)
    seas_c = seas_c[(seas_c["year"] >= year_range[0]) & (seas_c["year"] <= year_range[1])]
    seas_means = seas_c.groupby("season")["rainfall_mm"].mean()
    mon_mm = seas_means.get("JAS", 0)
    post_mm = seas_means.get("OND", 0)
    pre_mm = seas_means.get("MAM", 0)
    win_mm = seas_means.get("DJF", 0)
    total_seas = mon_mm + post_mm + pre_mm + win_mm
    monsoon_pct = (mon_mm / total_seas * 100) if total_seas else 0

    below_90 = int((ann_c["rainfall_mm"] < mean_c * 0.90).sum())
    severe_dry = int((ann_c["rainfall_mm"] < mean_c * 0.75).sum())
    drought_pct_c = (severe_dry / n_years * 100) if n_years else 0
    if cv_c >= 35.0 or (drought_pct_c >= 25.0 and mean_c < 900.0):
        risk_c = "HIGH"
    elif (cv_c < 23.0 and drought_pct_c < 15.0) or (mean_c >= 2000.0 and cv_c < 25.0):
        risk_c = "LOW"
    else:
        risk_c = "MEDIUM"

    # ── Climate Regime & Dynamic Weather Simulation Parameters for THIS place ──
    if mean_c >= 2200:
        zone_title = "🌧️ HIGH MONSOON ZONE · TROPICAL DELUGE ATMOSPHERE"
        zone_desc = f"{CD} is in India's premier high precipitation belt receiving normal annual rainfall of {mean_c:,.0f} mm. Simulating active orographic southwest monsoon rainfall & tropical drizzle."
        zone_badge_color = "#22c55e"
        zone_mode = "heavy"
        drop_count = 110
        drop_speed = 1.3
        drop_angle = 0.16
    elif mean_c >= 1200:
        zone_title = "🌦️ MODERATE RAINFALL ZONE · MONSOON SHOWERS ATMOSPHERE"
        zone_desc = f"{CD} receives a healthy {mean_c:,.0f} mm/yr normal precipitation with sustained seasonal rhythm and moderate moisture influx. Simulating gentle precipitation & mist."
        zone_badge_color = "#38bdf8"
        zone_mode = "drizzle"
        drop_count = 55
        drop_speed = 0.8
        drop_angle = 0.08
    else:
        zone_title = "☀️ SEMI-ARID / LOW RAIN ZONE · ARID HEAT SHIMMER"
        zone_desc = f"{CD} receives {mean_c:,.0f} mm/yr normal precipitation, situated in an arid or rain-shadow belt with heightened interannual variability. Simulating dry dust motes & heat shimmer."
        zone_badge_color = "#f59e0b"
        zone_mode = "arid"
        drop_count = 18
        drop_speed = 0.35
        drop_angle = 0.02

    gauge_pct = min(max(int((mean_c / 3600.0) * 100), 6), 100)

    if st.session_state.get("auto_scroll_to_dossier", False):
        components.html("""
        <script>
          function scrollToDossier() {
            try {
              var p = window.parent.document;
              var el = p.getElementById('regional-dossier-section');
              if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }
            } catch(e) {}
          }
          scrollToDossier();
          setTimeout(scrollToDossier, 80);
          setTimeout(scrollToDossier, 300);
          setTimeout(scrollToDossier, 700);
          setTimeout(scrollToDossier, 1200);
        </script>
        """, height=0, width=0)

    # ── Scroll anchor & dossier header (no empty containers) ───────────────────
    scroll_js = textwrap.dedent("""
    <script>
      (function() {
        function smoothScroll() {
          var el = document.getElementById('regional-dossier-section');
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
        smoothScroll();
        setTimeout(smoothScroll, 120);
        setTimeout(smoothScroll, 400);
        setTimeout(smoothScroll, 850);
        setTimeout(smoothScroll, 1400);
      })();
    </script>
    <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
         onload="var el=document.getElementById('regional-dossier-section'); if(el){ setTimeout(function(){ el.scrollIntoView({behavior:'smooth',block:'start'}); }, 300); }"
         style="display:none;" />
    """).strip() if st.session_state.get("auto_scroll_to_dossier", False) else ""

    btn_hd1, btn_hd2 = st.columns([3.3, 1.2])
    with btn_hd1:
        st.markdown(textwrap.dedent(f"""
        <div id="regional-dossier-section" style="padding-top:1.2rem; scroll-margin-top:24px;">
          {scroll_js}
          <div style="border-left:4.5px solid {T['accent']}; padding-left:14px; margin-bottom:14px;">
            <h2 class="sect" style="margin:0 0 4px 0; font-size:1.65rem;">
              📍 {CD} — Climate &amp; Rainfall Analytics 
              <span class="badge" style="vertical-align:middle; margin-left:8px;">Particular Place Focus</span>
            </h2>
            <p class="sect-sub" style="margin:0; font-size:0.88rem;">
              <b>Terrain:</b> {DIV_DESC.get(CD, "")} · <b>Coordinates:</b> {lat_c}°N, {lon_c}°E · <b>Observations:</b> {span_lo}–{span_hi} ({span_years} years: {n_years - n_obs_years} pipeline + {n_obs_years} observed IMD). <i>Exclusively focused on {CD} (not in comparison with others).</i>
            </p>
          </div>
        </div>
        """).strip(), unsafe_allow_html=True)
    with btn_hd2:
        st.markdown("<div style='height:26px;'></div>", unsafe_allow_html=True)
        st.button("📊 Compare All States", key="btn_dossier_return_comp", on_click=nav_all_states_comparison, use_container_width=True)
    st.session_state.auto_scroll_to_dossier = False

    # ── Interactive Weather Simulation Stage (Pure CSS + Sandboxed Audio) ─────
    drops_html = "".join([
        f'<span class="rain-drop" style="left:{i * 3.8 + 1.2}%; animation-delay:{round((i * 0.17) % 1.6, 2)}s; animation-duration:{round(0.85 + (i % 5) * 0.22, 2)}s;"></span>'
        for i in range(26)
    ])
    st.markdown(f"""
    <div class="weather-stage" style="border-left: 4.5px solid {zone_badge_color};">
      <div class="rain-overlay {zone_mode}">
        {drops_html}
      </div>
      
      <div class="weather-info-layer">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
          <span style="display:inline-block; width:9px; height:9px; border-radius:50%; background:{zone_badge_color}; box-shadow:0 0 10px {zone_badge_color}; animation:pulseDot 1.8s infinite;"></span>
          <span style="font-size:0.75rem; font-weight:800; letter-spacing:0.08em; text-transform:uppercase; color:{zone_badge_color};">
            Interactive Micro-Climate Simulation Active
          </span>
        </div>
        <div style="font-size:1.22rem; font-weight:800; color:{T['title']}; margin-bottom:4px;">
          {zone_title}
        </div>
        <div style="font-size:0.86rem; color:{T['muted']}; max-width:620px; line-height:1.45; margin-bottom:10px;">
          {zone_desc}
        </div>
        <div style="font-size:0.82rem; color:{T['muted']};">
          🌧️ Normal: <b>{mean_c:,.0f} mm/yr</b> · 1-in-20-yr Low: <b>{p5:,.0f} mm</b>
        </div>
      </div>

      <div class="weather-gauge-layer">
        <div style="text-align:right;">
          <div style="font-size:0.75rem; font-weight:800; color:{T['muted']}; text-transform:uppercase; letter-spacing:0.05em;">Rain Gauge</div>
          <div style="font-size:1.35rem; font-weight:850; color:{zone_badge_color};">{mean_c:,.0f} <span style="font-size:0.8rem; font-weight:600;">mm</span></div>
          <div style="font-size:0.72rem; color:{T['muted']};">{gauge_pct}% of 3,600mm scale</div>
        </div>
        <div class="gauge-tube" title="Normal Annual Precipitation Gauge: {mean_c:,.0f} mm">
          <div class="gauge-liquid" style="height:{gauge_pct}%; background:linear-gradient(180deg, {zone_badge_color} 0%, #15803d 100%);"></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)



    # ── Place Overview Banner: Local Mini-Map & Scientific Climate Summary ───
    col_zoom, col_nums = st.columns([1.15, 1.85])

    risk_badge_color = "#ef4444" if risk_c == "HIGH" else ("#f59e0b" if risk_c == "MEDIUM" else "#22c55e")
    risk_kpi_cls = "amber" if risk_c == "HIGH" else ("blue" if risk_c == "MEDIUM" else "green")

    with col_zoom:
        # Mini-map centred on the clicked region with green India
        fig_zoom = go.Figure()
        fig_zoom.add_trace(go.Choropleth(
            locations=["IND"], locationmode="country names", z=[1],
            colorscale=[[0, "rgba(22, 163, 74, 0.28)"], [1, "rgba(22, 163, 74, 0.50)"]],
            showscale=False,
            marker_line_color="#15803d" if not _DARK else "#22c55e",
            marker_line_width=2.0,
            hoverinfo="skip",
        ))
        fig_zoom.add_trace(go.Scattergeo(
            lat=[lat_c], lon=[lon_c], mode="markers+text",
            marker=dict(size=22, color="#22c55e", line=dict(width=3, color="#ffffff")),
            text=[CD], textposition="top center",
            textfont=dict(size=11, color=_FG, family="Inter"),
            hoverinfo="skip", showlegend=False,
        ))
        fig_zoom.update_geos(
            visible=False, resolution=50,
            lataxis_range=[lat_c - 6.5, lat_c + 6.5],
            lonaxis_range=[lon_c - 8.5, lon_c + 8.5],
            bgcolor="rgba(0,0,0,0)",
            showland=True, landcolor="#0c1723" if _DARK else "#f1e5cc",
            showocean=True, oceancolor="#060c14" if _DARK else "#d6e5ef",
            showlakes=True, lakecolor="#091422" if _DARK else "#d6e5ef",
            showrivers=True, rivercolor="#16253b" if _DARK else "#a7c4d7",
            showcountries=True, countrycolor="#334155" if _DARK else "#c4b595",
        )
        fig_zoom.update_layout(
            margin=dict(l=0, r=0, t=6, b=0), height=300,
            **_PAPER,
            showlegend=False,
        )
        st.plotly_chart(fig_zoom, use_container_width=True, theme=None, key=f"zoom_map_{CD}")

    with col_nums:
        st.markdown(f"""
        <div style="background:{T['card2']}; border:1px solid {T['border']}; border-radius:18px; padding:1.25rem 1.4rem; height:100%; display:flex; flex-direction:column; justify-content:space-between; box-shadow:0 4px 16px rgba(0,0,0,0.04);">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
              <span style="font-size:0.75rem; font-weight:800; text-transform:uppercase; letter-spacing:0.06em; color:{T['accent']};">
                📍 Geographic &amp; Climate Profile
              </span>
              <span style="background:{risk_badge_color}22; color:{risk_badge_color}; border:1px solid {risk_badge_color}55; padding:3px 9px; border-radius:999px; font-size:0.75rem; font-weight:750;">
                {risk_c} DROUGHT RISK
              </span>
            </div>
            <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:0.2rem;">
              <div style="font-size:2rem; font-weight:850; color:{T['value']}; line-height:1.1;">{mean_c:,.0f} <span style="font-size:1.1rem; font-weight:600;">mm</span></div>
              <div style="font-size:0.86rem; color:{T['muted']}; font-weight:600;">Normal Annual Precipitation ({span_lo}–{span_hi}{", incl. " + str(n_obs_years) + " observed yrs" if n_obs_years else ""})</div>
            </div>
            <div style="font-size:0.85rem; color:{T['text']}; margin-bottom:0.6rem; font-style:italic;">
              {DIV_DESC.get(CD, "Regional Meteorological Division")}
            </div>
          </div>
          <div style="border-top:1px solid {T['hr']}; padding-top:0.75rem; font-size:0.84rem; line-height:1.65; color:{T['text']};">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px 16px;">
              <div><b>🌐 Centroid:</b> {lat_c}°N, {lon_c}°E</div>
              <div><b>🌧️ Monsoon Regime:</b> {monsoon_pct:.1f}% in Jun–Sep ({mon_mm:,.0f} mm)</div>
              <div><b>📊 Interannual Stability:</b> CV {cv_c:.1f}% ({'High Stability' if cv_c < 20 else 'Moderate Stability' if cv_c < 30 else 'High Variability'})</div>
              <div><b>🏆 Wettest Year:</b> {wet_year} ({wet_val:,.0f} mm)</div>
              <div><b>⚠️ Drought Frequency:</b> {drought_pct_c:.1f}% ({severe_dry} of {n_years} yrs &lt;75%)</div>
              <div><b>📉 Driest Year:</b> {dry_year} ({dry_val:,.0f} mm)</div>
              <div style="grid-column: 1 / -1;"><b>📈 Secular Trend:</b> {slope_c:+.1f} mm/yr ({'Statistically significant (p&lt;0.05)' if p_c < 0.05 else 'No statistically significant trend'})</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Key Metrics (8 cards for this place only) ───────────────────────────
    slope_kpi_cls = "green" if slope_c >= 0 else "purple"
    st.markdown("<p style='font-size:0.92rem; font-weight:750; margin:1.3rem 0 0.6rem; color:" + T['title'] + "'>📊 Key Climate Metrics for " + CD + ":</p>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi green" style="margin:0"><div class="v">{mean_c:,.0f} mm</div><div class="l">Mean Annual Rainfall<br><small>{n_years} years observed</small></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi" style="margin:10px 0 0"><div class="v">{wet_year}</div><div class="l">All-Time Wettest Year<br><small>{wet_val:,.0f} mm (+{((wet_val-mean_c)/mean_c*100):.0f}% of normal)</small></div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi blue" style="margin:0"><div class="v">{cv_c:.1f}%</div><div class="l">Coefficient of Variation<br><small>Annual standard deviation: {std_c:,.0f} mm</small></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi amber" style="margin:10px 0 0"><div class="v">{dry_year}</div><div class="l">All-Time Driest Year<br><small>{dry_val:,.0f} mm ({((dry_val-mean_c)/mean_c*100):.0f}% of normal)</small></div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi purple" style="margin:0"><div class="v">{monsoon_pct:.1f}%</div><div class="l">Monsoon Contribution<br><small>{mon_mm:,.0f} mm received Jun–Sep</small></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi {slope_kpi_cls}" style="margin:10px 0 0"><div class="v">{slope_c:+.1f} mm/yr</div><div class="l">Long-Term Linear Trend<br><small>p-value: {p_c:.4f}</small></div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi {risk_kpi_cls}" style="margin:0"><div class="v">{risk_c}</div><div class="l">Drought Vulnerability Class<br><small>{severe_dry} of {n_years} yrs in drought (&lt;75%)</small></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi" style="margin:10px 0 0"><div class="v">{p5:,.0f} mm</div><div class="l">1-in-20-Year Low (5th Pct)<br><small>Extreme drought benchmark</small></div></div>', unsafe_allow_html=True)

    # Deficit severity counts
    normal_yrs = int((ann_c["rainfall_mm"] >= mean_c * 0.90).sum())
    mild_yrs = int(((ann_c["rainfall_mm"] < mean_c * 0.90) & (ann_c["rainfall_mm"] >= mean_c * 0.75)).sum())
    severe_yrs = int((ann_c["rainfall_mm"] < mean_c * 0.75).sum())

    # ── Tabs: Exclusively Dedicated to THIS Place ────────────────────────────
    st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
    tab_series, tab_seas, tab_trend, tab_extremes, tab_conclusions = st.tabs([
        "📊 Annual Series & Decades",
        "🌧️ Seasonal Breakdown",
        "📈 Long-Term Trend & Probability",
        "📜 Historical Records & Extremes Log",
        "📋 Key Takeaways & Fact Sheet",
    ])

    # ── TAB 1: ANNUAL TIME SERIES & DECADES ──────────────────────────────────
    with tab_series:
        _span_lbl = f"{span_years}-Year ({span_lo}–{span_hi})"
        st.markdown(f"#### {_span_lbl} Annual Rainfall History — {CD}")
        _obs_note = (f" Includes {n_obs_years} observed IMD years (2016–2025, amber-outlined bars)."
                     if n_obs_years else
                     " No observed IMD rows for this division's canonical name — pipeline layer only.")
        st.caption("Each bar represents one year for this place. Color indicates water anomaly: 🟢 Normal/Above (>=90%), 🟡 Mild Deficit (75–90%), 🔴 Severe Deficit (<75%)." + _obs_note)

        # Color coding each bar for this place (observed years get a distinct teal hue)
        bar_colors = [
            ("#0d9488" if obs else ("#16a34a" if v >= mean_c * 0.90 else ("#f59e0b" if v >= mean_c * 0.75 else "#ef4444")))
            for v, obs in zip(ann_c["rainfall_mm"], _is_obs)
        ]

        # 10-year rolling smooth for this place
        roll_10 = ann_c["rainfall_mm"].rolling(10, center=True, min_periods=3).mean()

        fig_ts = go.Figure()
        fig_ts.add_trace(go.Bar(
            x=ann_c["year"], y=ann_c["rainfall_mm"],
            marker_color=bar_colors,
            name="Annual Total",
            customdata=np.stack([
                np.round(((ann_c["rainfall_mm"] - mean_c) / mean_c * 100), 1),
                np.where(_is_obs, "observed IMD", "pipeline layer"),
            ], axis=-1),
            hovertemplate="<b>%{x}</b>: %{y:,.0f} mm (Anomaly: %{customdata[0]:+.1f}%)<br><i>%{customdata[1]}</i><extra></extra>",
            opacity=0.88,
        ))
        fig_ts.add_trace(go.Scatter(
            x=ann_c["year"], y=roll_10,
            mode="lines", name="10-Year Rolling Mean",
            line=dict(color="#38bdf8" if _DARK else "#1d4ed8", width=3),
            hovertemplate="10-yr smooth: %{y:,.0f} mm<extra></extra>",
        ))
        fig_ts.add_hline(y=mean_c, line_dash="dash", line_color="#16a34a" if not _DARK else "#22c55e",
                         annotation_text=f"Mean Normal ({mean_c:,.0f} mm)",
                         annotation_font_color=_TEXT_COLOR)
        fig_ts.add_hline(y=mean_c * 0.90, line_dash="dot", line_color="#d97706" if not _DARK else "#f59e0b",
                         annotation_text="90% Deficit Threshold",
                         annotation_font_color=_TEXT_COLOR)
        fig_ts.update_layout(
            title=dict(
                text=f"Annual Rainfall ({span_lo}–{span_hi}) — {CD}",
                font=dict(color=_TITLE_COLOR, size=15, family="'Outfit', 'Plus Jakarta Sans', sans-serif"),
            ),
            height=400, **_PAPER,
            xaxis=dict(
                title=dict(text="Year", font=dict(color=_TEXT_COLOR)),
                tickfont=dict(color=_TEXT_COLOR),
                gridcolor=_GRID_C,
            ),
            yaxis=dict(
                title=dict(text="Annual Rainfall (mm)", font=dict(color=_TEXT_COLOR)),
                tickfont=dict(color=_TEXT_COLOR),
                gridcolor=_GRID_C,
            ),
            legend=dict(orientation="h", y=1.12, x=0, font=dict(color=_TEXT_COLOR)),
            margin=dict(t=50, b=20),
            bargap=0.15,
        )
        st.plotly_chart(fig_ts, use_container_width=True, theme=None, key=f"ts_{CD}")

        # Decade by Decade bar chart for THIS place only
        ann_c["decade"] = (ann_c["year"] // 10) * 10
        dec_agg = ann_c.groupby("decade")["rainfall_mm"].agg(["mean", "count"]).reset_index()
        dec_agg["decade_label"] = dec_agg["decade"].apply(lambda d: f"{int(d)}s")
        dec_agg["anomaly"] = ((dec_agg["mean"] - mean_c) / mean_c * 100)

        fig_dec = go.Figure()
        fig_dec.add_trace(go.Bar(
            x=dec_agg["decade_label"], y=dec_agg["mean"],
            marker_color=np.where(dec_agg["mean"] >= mean_c, "#22c55e", "#f59e0b"),
            name="Decadal Mean",
            customdata=dec_agg["anomaly"],
            hovertemplate="<b>%{x}</b>: %{y:,.0f} mm/yr (%{customdata:+.1f}% vs normal)<extra></extra>",
        ))
        fig_dec.add_hline(y=mean_c, line_dash="dash", line_color="#475569" if not _DARK else "#94a3b8",
                          annotation_text=f"{span_years}-Yr Mean ({mean_c:,.0f} mm)",
                          annotation_font_color=_TEXT_COLOR)
        fig_dec.update_layout(
            title=dict(
                text=f"Decade-by-Decade Climate Evolution in {CD} (1900s–2010s)",
                font=dict(color=_TITLE_COLOR, size=15, family="'Outfit', 'Plus Jakarta Sans', sans-serif"),
            ),
            height=320, **_PAPER,
            xaxis=dict(
                title=dict(text="Decade", font=dict(color=_TEXT_COLOR)),
                tickfont=dict(color=_TEXT_COLOR),
                gridcolor=_GRID_C,
            ),
            yaxis=dict(
                title=dict(text="Decadal Mean (mm)", font=dict(color=_TEXT_COLOR)),
                tickfont=dict(color=_TEXT_COLOR),
                gridcolor=_GRID_C,
            ),
            margin=dict(t=45, b=20),
            bargap=0.25,
        )
        st.plotly_chart(fig_dec, use_container_width=True, theme=None, key=f"dec_{CD}")

    # ── TAB 2: SEASONAL BREAKDOWN ────────────────────────────────────────────
    with tab_seas:
        st.markdown(f"#### Seasonal Moisture Regime — {CD}")
        st.caption("Monsoon, pre-monsoon and post-monsoon means include observed IMD years (2016–2025). "
                   "Winter is Dec–Feb in the pipeline layer but Jan–Feb in IMD's observed tables, so winter means use the pipeline record (1901–2015) only — the two are never mixed.")
        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            fig_pie = go.Figure(go.Pie(
                labels=["Monsoon (Jun–Sep)", "Post-monsoon (Oct–Dec)", "Pre-monsoon (Mar–May)", "Winter (Dec–Feb)"],
                values=[mon_mm, post_mm, pre_mm, win_mm],
                hole=0.60,
                marker=dict(colors=["#22c55e", "#38bdf8", "#fbbf24", "#a855f7"]),
                textinfo="label+percent",
                textfont=dict(size=11, color="#000000" if not _DARK else "#ffffff"),
                hovertemplate="%{label}: %{value:,.0f} mm<extra></extra>",
            ))
            fig_pie.update_layout(
                title=dict(
                    text="Seasonal Contribution (% of Annual Rain)",
                    font=dict(color=_TITLE_COLOR, size=15, family="'Outfit', 'Plus Jakarta Sans', sans-serif"),
                ),
                height=350, **_PAPER,
                margin=dict(t=45, b=20),
                annotations=[dict(text=f"<b>{monsoon_pct:.0f}%</b><br>Monsoon",
                                  x=0.5, y=0.5, font_size=17,
                                  font_color="#15803d" if not _DARK else "#22c55e", showarrow=False)],
            )
            st.plotly_chart(fig_pie, use_container_width=True, theme=None, key=f"pie_{CD}")

        with col_s2:
            fig_bar_seas = go.Figure(go.Bar(
                x=["Winter (Dec–Feb)", "Pre-Monsoon (Mar–May)", "Monsoon (Jun–Sep)", "Post-Monsoon (Oct–Dec)"],
                y=[win_mm, pre_mm, mon_mm, post_mm],
                marker_color=["#a855f7", "#fbbf24", "#22c55e", "#38bdf8"],
                text=[f"{v:,.0f} mm" for v in [win_mm, pre_mm, mon_mm, post_mm]],
                textposition="outside",
                textfont=dict(color=_TEXT_COLOR, size=11),
            ))
            fig_bar_seas.update_layout(
                title=dict(
                    text="Average Seasonal Totals (mm)",
                    font=dict(color=_TITLE_COLOR, size=15, family="'Outfit', 'Plus Jakarta Sans', sans-serif"),
                ),
                height=350, **_PAPER,
                xaxis=dict(
                    tickfont=dict(color=_TEXT_COLOR),
                    gridcolor=_GRID_C,
                ),
                yaxis=dict(
                    title=dict(text="Mean Precipitation (mm)", font=dict(color=_TEXT_COLOR)),
                    tickfont=dict(color=_TEXT_COLOR),
                    gridcolor=_GRID_C,
                ),
                margin=dict(t=45, b=20),
            )
            st.plotly_chart(fig_bar_seas, use_container_width=True, theme=None, key=f"bar_seas_{CD}")

        # Period Shift Comparison (Period A vs Period B) for THIS place
        st.markdown(f"##### Climate Shift in {CD}: Compare Two Eras")
        cp1, cp2 = st.columns(2)
        with cp1:
            per_a = st.slider("Period A (Baseline)", span_lo, span_hi, (1950, 1980), key=f"pa_{CD}")
        with cp2:
            per_b = st.slider("Period B (Recent)", span_lo, span_hi, (1981, span_hi), key=f"pb_{CD}")

        sub_a = ann_c[(ann_c["year"] >= per_a[0]) & (ann_c["year"] <= per_a[1])]["rainfall_mm"]
        sub_b = ann_c[(ann_c["year"] >= per_b[0]) & (ann_c["year"] <= per_b[1])]["rainfall_mm"]

        if len(sub_a) and len(sub_b):
            diff_p = sub_b.mean() - sub_a.mean()
            diff_pct = (diff_p / sub_a.mean() * 100) if sub_a.mean() else 0
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown(f'<div class="kpi amber" style="margin:0"><div class="v">{sub_a.mean():,.0f} mm</div><div class="l">Period A ({per_a[0]}–{per_a[1]})<br><small>CV: {(sub_a.std()/sub_a.mean()*100):.1f}% · n={len(sub_a)}</small></div></div>', unsafe_allow_html=True)
            with sc2:
                st.markdown(f'<div class="kpi green" style="margin:0"><div class="v">{sub_b.mean():,.0f} mm</div><div class="l">Period B ({per_b[0]}–{per_b[1]})<br><small>CV: {(sub_b.std()/sub_b.mean()*100):.1f}% · n={len(sub_b)}</small></div></div>', unsafe_allow_html=True)
            diff_kpi_cls = "green" if diff_p >= 0 else "purple"
            with sc3:
                st.markdown(f'<div class="kpi {diff_kpi_cls}" style="margin:0"><div class="v">{diff_p:+,.0f} mm</div><div class="l">Net Climate Change ({diff_pct:+.1f}%)<br><small>Difference between eras in {CD}</small></div></div>', unsafe_allow_html=True)

    # ── TAB 3: LONG-TERM TREND & PROBABILITY DISTRIBUTION ────────────────────
    with tab_trend:
        st.markdown(f"#### Long-Term Climate Trend & Statistical Confidence — {CD}")
        col_t1, col_t2 = st.columns([1.1, 0.9])
        with col_t1:
            # Linear trend with 95% confidence band ribbon
            yhat_c = slope_c * x_c + intercept_c
            resid_c = y_c - yhat_c
            nn_c = len(x_c)
            se_c = np.sqrt((resid_c**2).sum() / max(nn_c - 2, 1)) / np.sqrt(nn_c)
            tcc_c = _stats.t.ppf(0.975, max(nn_c - 2, 1))
            ci_c = tcc_c * se_c * np.sqrt(1 + 1 / nn_c + (x_c - x_c.mean()) ** 2 / ((x_c - x_c.mean()) ** 2).sum())

            fig_band = go.Figure()
            fig_band.add_trace(go.Scatter(
                x=np.concatenate([x_c, x_c[::-1]]),
                y=np.concatenate([yhat_c + ci_c, (yhat_c - ci_c)[::-1]]),
                fill="tonexty", fillcolor="rgba(34, 197, 94, 0.14)",
                line=dict(color="rgba(0,0,0,0)"), name="95% Confidence Band",
            ))
            fig_band.add_trace(go.Scatter(
                x=x_c, y=y_c, mode="markers+lines",
                name="Observed Rainfall", line=dict(color="#38bdf8" if _DARK else "#1d4ed8", width=1.8),
                marker=dict(color="#22c55e", size=5.5),
            ))
            fig_band.add_trace(go.Scatter(
                x=x_c, y=yhat_c, mode="lines",
                name=f"Fitted Trend ({slope_c:+.1f} mm/yr)",
                line=dict(color="#f472b6", width=2.5, dash="dash"),
            ))
            fig_band.update_layout(
                title=dict(
                    text=f"Trend Line with 95% CI — {CD} (p = {p_c:.4f})",
                    font=dict(color=_TITLE_COLOR, size=15, family="'Outfit', 'Plus Jakarta Sans', sans-serif"),
                ),
                height=380, **_PAPER,
                xaxis=dict(
                    title=dict(text="Year", font=dict(color=_TEXT_COLOR)),
                    tickfont=dict(color=_TEXT_COLOR),
                    gridcolor=_GRID_C,
                ),
                yaxis=dict(
                    title=dict(text="Rainfall (mm)", font=dict(color=_TEXT_COLOR)),
                    tickfont=dict(color=_TEXT_COLOR),
                    gridcolor=_GRID_C,
                ),
                legend=dict(orientation="h", y=1.12, x=0, font=dict(color=_TEXT_COLOR)),
                margin=dict(t=50, b=20),
            )
            st.plotly_chart(fig_band, use_container_width=True, theme=None, key=f"band_{CD}")

        with col_t2:
            fig_hist = px.histogram(
                ann_c, x="rainfall_mm", nbins=20, marginal="box",
                color_discrete_sequence=["#15803d" if not _DARK else "#22c55e"],
                title=f"Annual Rainfall Distribution — {CD}",
                template=_PLOT_TEMPLATE,
            )
            fig_hist.update_layout(
                height=380, **_PAPER,
                title=dict(
                    text=f"Annual Rainfall Distribution — {CD}",
                    font=dict(color=_TITLE_COLOR, size=15, family="'Outfit', 'Plus Jakarta Sans', sans-serif"),
                ),
                xaxis=dict(
                    title=dict(text="Rainfall (mm)", font=dict(color=_TEXT_COLOR)),
                    tickfont=dict(color=_TEXT_COLOR),
                    gridcolor=_GRID_C,
                ),
                yaxis=dict(
                    title=dict(text="Number of Years", font=dict(color=_TEXT_COLOR)),
                    tickfont=dict(color=_TEXT_COLOR),
                    gridcolor=_GRID_C,
                ),
                showlegend=False, margin=dict(t=50, b=20),
            )
            st.plotly_chart(fig_hist, use_container_width=True, theme=None, key=f"hist_{CD}")

    # ── TAB 4: HISTORICAL RECORDS & EXTREMES LOG ─────────────────────────────
    with tab_extremes:
        st.markdown(f"#### Historical Weather Records Log — {CD}")
        col_w, col_d = st.columns(2)
        with col_w:
            st.markdown(f"<div style='font-weight:750;font-size:0.96rem;color:{T['title']};margin-bottom:0.5rem;'>🌊 Top 5 Wettest Years on Record ({CD})</div>", unsafe_allow_html=True)
            top_wet = ann_c.nlargest(5, "rainfall_mm")[["year", "rainfall_mm"]].copy()
            top_wet["Anomaly vs Normal"] = ((top_wet["rainfall_mm"] - mean_c) / mean_c * 100).apply(lambda x: f"+{x:.1f}%")
            top_wet.columns = ["Year", "Rainfall (mm)", "Anomaly vs Normal"]
            st.markdown(render_extremes_table(top_wet, _DARK, is_wet=True), unsafe_allow_html=True)

        with col_d:
            st.markdown(f"<div style='font-weight:750;font-size:0.96rem;color:{T['title']};margin-bottom:0.5rem;'>🏜️ Top 5 Driest Drought Years on Record ({CD})</div>", unsafe_allow_html=True)
            top_dry = ann_c.nsmallest(5, "rainfall_mm")[["year", "rainfall_mm"]].copy()
            top_dry["Deficit vs Normal"] = ((top_dry["rainfall_mm"] - mean_c) / mean_c * 100).apply(lambda x: f"{x:.1f}%")
            top_dry.columns = ["Year", "Rainfall (mm)", "Deficit vs Normal"]
            st.markdown(render_extremes_table(top_dry, _DARK, is_wet=False), unsafe_allow_html=True)

        # Deficit severity breakdown
        st.markdown(f"##### 💧 Drought Frequency Distribution for {CD}")
        normal_yrs = int((ann_c["rainfall_mm"] >= mean_c * 0.90).sum())
        mild_yrs = int(((ann_c["rainfall_mm"] < mean_c * 0.90) & (ann_c["rainfall_mm"] >= mean_c * 0.75)).sum())
        severe_yrs = int((ann_c["rainfall_mm"] < mean_c * 0.75).sum())

        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown(f'<div class="kpi green" style="margin:0"><div class="v">{normal_yrs} / {n_years}</div><div class="l">Normal or Above-Normal Years<br><small>{(normal_yrs/n_years*100):.1f}% of historical record</small></div></div>', unsafe_allow_html=True)
        with fc2:
            st.markdown(f'<div class="kpi amber" style="margin:0"><div class="v">{mild_yrs} / {n_years}</div><div class="l">Mild Deficit Years (75–90% normal)<br><small>{(mild_yrs/n_years*100):.1f}% of historical record</small></div></div>', unsafe_allow_html=True)
        with fc3:
            st.markdown(f'<div class="kpi" style="margin:0; border-color:rgba(239,68,68,0.4);"><div class="v" style="color:#ef4444;">{severe_yrs} / {n_years}</div><div class="l">Severe Drought Years (&lt;75% normal)<br><small>{(severe_yrs/n_years*100):.1f}% of historical record</small></div></div>', unsafe_allow_html=True)

    # ── TAB 5: KEY TAKEAWAYS & EMPIRICAL FACT SHEET ──────────────────────────
    with tab_conclusions:
        st.markdown(f"#### 📋 Key Historical Takeaways & Empirical Fact Sheet — {CD}")

        # Top summary alert banner emphasizing no predictions, strictly empirical facts
        st.markdown(f"""
        <div style="background:{'rgba(34,197,94,0.08)' if _DARK else 'rgba(21,128,61,0.06)'}; border:1px solid {'rgba(34,197,94,0.3)' if _DARK else 'rgba(21,128,61,0.25)'}; border-radius:14px; padding:12px 18px; margin-bottom:1.3rem; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
          <div>
            <div style="font-weight:800; font-size:0.95rem; color:{'#22c55e' if _DARK else '#15803d'};">
              📌 Plain Fact Sheet &amp; Observational Conclusions ({span_lo}–{span_hi} Record)
            </div>
            <div style="font-size:0.83rem; color:{T['muted']}; margin-top:3px;">
              <b>No Predictive Models:</b> All takeaways below are empirical facts calculated directly from {span_years} years of records for <b>{CD}</b> ({n_years - n_obs_years} pipeline + {n_obs_years} observed IMD). Designed for rapid review without analyzing graphs.
            </div>
          </div>
          <span style="background:{'rgba(34,197,94,0.18)' if _DARK else 'rgba(21,128,61,0.12)'}; color:{'#22c55e' if _DARK else '#15803d'}; border:1px solid {'rgba(34,197,94,0.4)' if _DARK else 'rgba(21,128,61,0.3)'}; padding:4px 10px; border-radius:999px; font-size:0.75rem; font-weight:800; letter-spacing:0.04em;">
            {span_years}-YEAR GROUND TRUTH
          </span>
        </div>
        """, unsafe_allow_html=True)

        # Computation of decadal and empirical statistics
        ann_c_dec = ann_c.copy()
        ann_c_dec["decade"] = (ann_c_dec["year"] // 10) * 10
        dec_means = ann_c_dec.groupby("decade")["rainfall_mm"].mean()
        wettest_dec_yr = int(dec_means.idxmax())
        wettest_dec_val = float(dec_means.max())
        driest_dec_yr = int(dec_means.idxmin())
        driest_dec_val = float(dec_means.min())
        recent_dec = 2000 if 2000 in dec_means.index else int(dec_means.index[-1])
        recent_dec_val = float(dec_means.loc[recent_dec])
        recent_dec_lo, recent_dec_hi = recent_dec, min(recent_dec + 9, span_hi)
        recent_diff_pct = ((recent_dec_val - mean_c) / mean_c * 100) if mean_c else 0

        # Stability categorization
        if cv_c < 18.0:
            cv_label = "High Stability (Steady Annual Rains)"
            cv_badge_col = "#22c55e"
            cv_badge_bg = "rgba(34,197,94,0.15)" if _DARK else "rgba(21,128,61,0.12)"
            cv_summary = f"With a low CV of {cv_c:.1f}%, {CD} experiences consistent precipitation year after year with minimal percentage fluctuations around its mean."
        elif cv_c < 28.0:
            cv_label = "Moderate Stability (Normal Variations)"
            cv_badge_col = "#38bdf8"
            cv_badge_bg = "rgba(56,189,248,0.15)" if _DARK else "rgba(3,105,161,0.12)"
            cv_summary = f"With a moderate CV of {cv_c:.1f}%, annual rainfall fluctuates within expected climatic bounds, showing reasonable interannual predictability."
        elif cv_c < 36.0:
            cv_label = "High Volatility (Erratic Interannual Swings)"
            cv_badge_col = "#f59e0b"
            cv_badge_bg = "rgba(245,158,11,0.15)" if _DARK else "rgba(180,83,9,0.12)"
            cv_summary = f"With a high CV of {cv_c:.1f}%, precipitation is volatile; bumper water years and severe dry spells alternate frequently across the record."
        else:
            cv_label = "Extreme Volatility (Unreliable Precipitation)"
            cv_badge_col = "#ef4444"
            cv_badge_bg = "rgba(239,68,68,0.15)" if _DARK else "rgba(185,28,28,0.12)"
            cv_summary = f"With an extreme CV of {cv_c:.1f}%, annual rainfall is erratic with large percentage dispersion relative to its mean."

        # Trend summary
        if p_c < 0.05:
            if slope_c > 0:
                trend_title = "Statistically Significant Upward Drift"
                trend_badge_col = "#22c55e"
                trend_badge_bg = "rgba(34,197,94,0.15)" if _DARK else "rgba(21,128,61,0.12)"
                trend_badge_text = "SIGNIFICANT INCREASE"
                trend_desc = f"An observational upward trend of {slope_c:+.2f} mm/yr ({slope_c*10:+.1f} mm/decade, p = {p_c:.4f} &lt; 0.05) was verified in the historical data."
            else:
                trend_title = "Statistically Significant Downward Drift"
                trend_badge_col = "#ef4444"
                trend_badge_bg = "rgba(239,68,68,0.15)" if _DARK else "rgba(185,28,28,0.12)"
                trend_badge_text = "SIGNIFICANT DECREASE"
                trend_desc = f"An observational downward trend of {slope_c:+.2f} mm/yr ({slope_c*10:+.1f} mm/decade, p = {p_c:.4f} &lt; 0.05) was verified in the historical data."
        else:
            trend_title = "Stationary Long-Term Pattern"
            trend_badge_col = "#64748b" if _DARK else "#4b5563"
            trend_badge_bg = "rgba(100,116,139,0.15)" if _DARK else "rgba(100,116,139,0.12)"
            trend_badge_text = "NO SECULAR TREND"
            trend_desc = f"Observed slope is {slope_c:+.2f} mm/yr, but p = {p_c:.3f} &ge; 0.05 confirms this is not statistically distinguishable from random historical fluctuations."

        spread_ratio = (wet_val / dry_val) if dry_val > 0 else 0
        median_c = float(ann_c["rainfall_mm"].median()) if n_years else mean_c
        skew_c = float(_stats.skew(ann_c["rainfall_mm"])) if n_years > 2 else 0
        normal_band_yrs = int(((ann_c["rainfall_mm"] >= mean_c * 0.8) & (ann_c["rainfall_mm"] <= mean_c * 1.2)).sum())

        # Row 1 of Quadrilateral Fact Boxes
        qcol1, qcol2, qcol3 = st.columns(3)
        with qcol1:
            st.markdown(f"""
            <div class="fact-quad-card">
              <span class="fact-quad-badge" style="background:{'rgba(56,189,248,0.15)' if _DARK else 'rgba(3,105,161,0.12)'}; color:{T['blue']};">
                🌧️ VOLUME &amp; SPREAD
              </span>
              <div class="fact-quad-title">Annual Rain Baseline</div>
              <div class="fact-quad-metric">{mean_c:,.0f} mm</div>
              <div class="fact-quad-body">
                <ul>
                  <li><b>Median Precipitation:</b> {median_c:,.0f} mm/year.</li>
                  <li><b>Standard Deviation:</b> ±{std_c:,.0f} mm dispersion.</li>
                  <li><b>Recorded Range:</b> {dry_val:,.0f} mm ({dry_year}) to {wet_val:,.0f} mm ({wet_year}).</li>
                  <li><b>Spread Ratio:</b> Wettest year was <b>{spread_ratio:.1f}×</b> wetter than the driest.</li>
                </ul>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with qcol2:
            st.markdown(f"""
            <div class="fact-quad-card">
              <span class="fact-quad-badge" style="background:{'rgba(168,85,247,0.15)' if _DARK else 'rgba(107,33,168,0.12)'}; color:{T['purple']};">
                🗓️ SEASONAL BREAKDOWN
              </span>
              <div class="fact-quad-title">Monsoon Share (Jun–Sep)</div>
              <div class="fact-quad-metric">{monsoon_pct:.1f}%</div>
              <div class="fact-quad-body">
                <ul>
                  <li><b>Monsoon Bulk:</b> <b>{mon_mm:,.0f} mm</b> received during Jun–Sep.</li>
                  <li><b>Post-Monsoon (OND):</b> {post_mm:,.0f} mm ({(post_mm/total_seas*100) if total_seas else 0:.1f}% of total).</li>
                  <li><b>Pre-Monsoon (MAM):</b> {pre_mm:,.0f} mm ({(pre_mm/total_seas*100) if total_seas else 0:.1f}% of total).</li>
                  <li><b>Winter (DJF):</b> {win_mm:,.0f} mm ({(win_mm/total_seas*100) if total_seas else 0:.1f}% of total).</li>
                  <li>{'Strong single-season monsoon dependency.' if monsoon_pct >= 75 else 'Bimodal rainfall regime with significant post-monsoon contribution.'}</li>
                </ul>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with qcol3:
            st.markdown(f"""
            <div class="fact-quad-card">
              <span class="fact-quad-badge" style="background:{cv_badge_bg}; color:{cv_badge_col};">
                📊 STABILITY INDEX
              </span>
              <div class="fact-quad-title">Interannual Predictability</div>
              <div class="fact-quad-metric">CV {cv_c:.1f}%</div>
              <div class="fact-quad-body">
                <ul>
                  <li><b>Category:</b> {cv_label.split('(')[0].strip()}.</li>
                  <li>{cv_summary}</li>
                  <li><b>Steady Band:</b> In <b>{normal_band_yrs} of {n_years} yrs</b> ({(normal_band_yrs/n_years*100):.1f}%), rain stayed within ±20% of normal.</li>
                  <li><b>Distribution Skew:</b> {skew_c:+.2f} ({'moderately right-skewed' if skew_c > 0.3 else 'near-symmetric' if abs(skew_c) <= 0.3 else 'left-skewed'}).</li>
                </ul>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1.1rem;'></div>", unsafe_allow_html=True)

        # Row 2 of Quadrilateral Fact Boxes
        qcol4, qcol5, qcol6 = st.columns(3)
        with qcol4:
            st.markdown(f"""
            <div class="fact-quad-card">
              <span class="fact-quad-badge" style="background:{'rgba(239,68,68,0.15)' if _DARK else 'rgba(185,28,28,0.12)'}; color:#ef4444;">
                ⚠️ DEFICIT HISTORY
              </span>
              <div class="fact-quad-title">Historical Drought Rate</div>
              <div class="fact-quad-metric">{severe_yrs} / {n_years} Yrs</div>
              <div class="fact-quad-body">
                <ul>
                  <li><b>Normal or Above (&ge;90%):</b> <b>{normal_yrs} yrs</b> ({(normal_yrs/n_years*100):.1f}% of record).</li>
                  <li><b>Mild Deficit (75%–90%):</b> <b>{mild_yrs} yrs</b> ({(mild_yrs/n_years*100):.1f}% of record).</li>
                  <li><b>Severe Drought (&lt;75%):</b> <b>{severe_yrs} yrs</b> ({(severe_yrs/n_years*100):.1f}% of record).</li>
                  <li><b>1-in-20-Yr Benchmark:</b> Empirical 5th percentile is <b>{p5:,.0f} mm</b> ({((mean_c-p5)/mean_c*100):.1f}% below normal).</li>
                </ul>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with qcol5:
            st.markdown(f"""
            <div class="fact-quad-card">
              <span class="fact-quad-badge" style="background:{trend_badge_bg}; color:{trend_badge_col};">
                📈 {trend_badge_text}
              </span>
              <div class="fact-quad-title">{trend_title}</div>
              <div class="fact-quad-metric">{slope_c:+.2f} mm/yr</div>
              <div class="fact-quad-body">
                <ul>
                  <li><b>{span_years}-Yr OLS Slope:</b> {slope_c:+.2f} mm per calendar year.</li>
                  <li><b>Statistical Significance:</b> p = <b>{p_c:.4f}</b> {'(&lt; 0.05 significant)' if p_c < 0.05 else '(&ge; 0.05 not significant)'}.</li>
                  <li><b>Net Historical Shift:</b> <b>{slope_c*span_years:+.0f} mm</b> across the {span_lo}–{span_hi} observation window.</li>
                  <li><b>Observation only:</b> Represents historical ledger; no future trajectory is implied.</li>
                </ul>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with qcol6:
            st.markdown(f"""
            <div class="fact-quad-card">
              <span class="fact-quad-badge" style="background:{'rgba(245,158,11,0.15)' if _DARK else 'rgba(180,83,9,0.12)'}; color:{T['amber']};">
                🏛️ DECADAL EPOCHS
              </span>
              <div class="fact-quad-title">Historical Decade Extremes</div>
              <div class="fact-quad-metric">{wettest_dec_yr}s vs {driest_dec_yr}s</div>
              <div class="fact-quad-body">
                <ul>
                  <li><b>Wettest Decade:</b> {wettest_dec_yr}s averaged <b>{wettest_dec_val:,.0f} mm/yr</b> ({((wettest_dec_val-mean_c)/mean_c*100):+.1f}% vs normal).</li>
                  <li><b>Driest Decade:</b> {driest_dec_yr}s averaged <b>{driest_dec_val:,.0f} mm/yr</b> ({((driest_dec_val-mean_c)/mean_c*100):+.1f}% vs normal).</li>
                  <li><b>Recent Era ({recent_dec_lo}–{recent_dec_hi}):</b> Averaged <b>{recent_dec_val:,.0f} mm/yr</b> ({recent_diff_pct:+.1f}% vs baseline).</li>
                  <li>Documents multi-decadal oscillation without making forward predictions.</li>
                </ul>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 — ALL-INDIA MULTI-REGION COMPARISONS (MACRO BENCHMARK)
# ════════════════════════════════════════════════════════════════════════════
def render_all_states_comparison():
    st.markdown('<div id="all-states-comparison-section" style="padding-top:1.2rem; scroll-margin-top:24px;"></div>', unsafe_allow_html=True)
    if st.session_state.get("scroll_to_comparisons", False):
        components.html("""
        <script>
          (function() {
            function scrollToComp() {
              try {
                var p = window.parent;
                if (!p || !p.document) return false;
                var el = p.document.getElementById('all-states-comparison-section');
                if (el) {
                  el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  return true;
                }
              } catch(e) {}
              return false;
            }
            scrollToComp();
            var attempts = 0;
            var itv = setInterval(function() {
              attempts++;
              if (scrollToComp() || attempts >= 10) {
                clearInterval(itv);
              }
            }, 80);
          })();
        </script>
        """, height=1, width=1)
        st.session_state.scroll_to_comparisons = False

    st.markdown(textwrap.dedent(f'''
    <div class="card" style="margin-top:1.2rem; border-left:4.5px solid {T["blue"]};">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
        <div>
          <h2 class="sect" style="margin:0 0 4px 0; font-size:1.65rem;">
            📊 All-India Multi-Region Benchmark Comparisons <span class="badge blue">Macro Overview</span>
          </h2>
          <p class="sect-sub" style="margin:0; font-size:0.88rem;">
            Pan-India cross-division rankings, drought vulnerability classification, and national long-term trends across all 36 subdivisions.
            <b>Record: 1901–2025</b> — pipeline layer (1901–2015) + observed IMD annual values (2016–2025; 2020 quality-gated).
          </p>
        </div>
      </div>
    ''').strip(), unsafe_allow_html=True)

    annual_all = df[df["season"] == "ANNUAL"]
    # Extend rankings with observed IMD annual values (2016–2025) per division.
    if year_range[1] > 2015:
        _obs_rank_frames = []
        for _pd_name in annual_all["division"].unique():
            _cn = PIPE_TO_CANON.get(_pd_name)
            if _cn:
                _o = observed_rows_for_division(_cn)
                if not _o.empty:
                    _o = _o[(_o["season"] == "ANNUAL")
                            & (_o["year"] >= year_range[0]) & (_o["year"] <= year_range[1])].copy()
                    _o["division"] = _pd_name
                    _obs_rank_frames.append(_o)
        if _obs_rank_frames:
            annual_all = pd.concat(
                [annual_all, pd.concat(_obs_rank_frames, ignore_index=True)], ignore_index=True)
    rank = annual_all.groupby("division")["rainfall_mm"].agg(["mean", "std"]).reset_index()
    rank["cv"] = rank["std"] / rank["mean"] * 100
    rank = rank.sort_values("cv", ascending=True)

    fig_cv = px.bar(
        rank, x="cv", y="division", orientation="h",
        color="cv", color_continuous_scale=[
            [0.0, "#34d399"], [0.5, "#fbbf24"], [1.0, "#ef4444"]],
        range_x=[0, rank["cv"].max() * 1.15],
        hover_data={"mean": ":,.0f mm", "cv": ":.1f%"},
        labels={"cv": "CV (%)", "division": "", "mean": "Mean"},
        template=_PLOT_TEMPLATE,
    )
    fig_cv.update_layout(
        height=800, **_PAPER,
        coloraxis_colorbar=dict(
            title=dict(text="CV%", font=dict(color=_TEXT_COLOR)),
            thickness=14, len=0.5,
            tickfont=dict(color=_TEXT_COLOR),
        ),
        xaxis=dict(
            gridcolor=_GRID_C,
            tickfont=dict(color=_TEXT_COLOR),
            title=dict(text="CV (%)", font=dict(color=_TEXT_COLOR)),
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=11, color=_TEXT_COLOR),
            title=dict(text="", font=dict(color=_TEXT_COLOR)),
        ),
        title=dict(
            text="Rainfall Variability (CV %) across all 36 Subdivisions",
            font=dict(color=_TITLE_COLOR, size=15, family="'Outfit', 'Plus Jakarta Sans', sans-serif"),
        ),
        margin=dict(l=10, r=10),
    )
    st.plotly_chart(fig_cv, use_container_width=True, theme=None, key="fig_macro_cv_rank")

    # Drought-risk table
    df_risk = agg[["division", "mean_rain", "cv", "drought_pct", "min_rain", "risk"]].copy()
    df_risk["risk_order"] = df_risk["risk"].map({"HIGH": 0, "MEDIUM": 1, "LOW": 2})
    df_risk = df_risk.sort_values(["risk_order", "cv"], ascending=[True, False]).drop(columns="risk_order")
    df_risk.columns = ["Division", "Mean (mm)", "CV %", "Drought frequency %", "Worst year (mm)", "Risk"]

    st.markdown(f"<div style='font-weight:750;font-size:1.05rem;color:{T['title']};margin-bottom:0.25rem;'>Drought-Risk Classification Table (36 Subdivisions)</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:0.84rem;color:{T['muted']};margin-bottom:0.8rem;'>Categorized via India Meteorological Department (IMD) recurrence standards &amp; interannual variability (CV%). <b>🟢 Low Risk:</b> High hydrological stability (CV &lt; 23% and drought &lt; 15% yrs). <b>🟡 Medium Risk:</b> Intermediate variability &amp; periodic deficits. <b>🔴 High Risk:</b> Arid rain-shadow belts &amp; chronic drought recurrence (CV &ge; 35% or drought &ge; 25% yrs).</p>", unsafe_allow_html=True)
    st.markdown(render_risk_table(df_risk, _DARK), unsafe_allow_html=True)

    # All-India National Trend — pipeline layer (1901–2015, blue) + observed IMD
    # (2016–2025, amber). The two layers have slightly different calibrations, so
    # they are plotted as distinct series, never silently merged into one line.
    nat = yearly_national.copy()
    nat["year"] = nat["year"].astype(int)
    nat_ext = load_national_extended()
    nat_obs = nat_ext[nat_ext["layer"] == "observed IMD"]
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(
        x=nat["year"], y=nat["national_annual_mean"],
        marker_color=np.where(nat["national_annual_mean"] < nat["national_annual_mean"].mean() * 0.9,
                              "#ef4444", "#3b82f6"),
        opacity=0.75, name="Annual mean (pipeline 1901–2015)",
        hovertemplate="<b>%{x}</b>: %{y:,.0f} mm<extra>pipeline layer</extra>",
    ))
    if not nat_obs.empty:
        fig6.add_trace(go.Bar(
            x=nat_obs["year"], y=nat_obs["mm"],
            marker_color="#f59e0b", opacity=0.9,
            name="Observed IMD (2016–2025)",
            hovertemplate="<b>%{x}</b>: %{y:,.0f} mm<extra>observed IMD</extra>",
        ))
    _mon26 = nat_ext[(nat_ext["year"] == 2026) & nat_ext["monsoon_mm"].notna()]
    if not _mon26.empty:
        fig6.add_annotation(
            x=2026, y=_mon26["monsoon_mm"].iloc[0],
            text=f"2026: monsoon {_mon26['monsoon_mm'].iloc[0]:,.0f} mm "
                 f"({_mon26['monsoon_dep'].iloc[0]:+.1f}%) — year in progress",
            showarrow=True, arrowhead=2, arrowcolor="#ef4444",
            font=dict(color=_TEXT_COLOR, size=11),
            ay=-60,
        )
    fig6.add_trace(go.Scatter(
        x=nat["year"], y=nat["national_annual_mean"].rolling(10, center=True, min_periods=3).mean(),
        mode="lines", name="10-yr smooth (pipeline)", line=dict(color="#f59e0b" if not _DARK else "#fbbf24", width=3),
    ))
    mean_all = nat["national_annual_mean"].mean()
    fig6.add_hline(y=mean_all, line_dash="dash", line_color="#475569" if not _DARK else "#94a3b8",
                   annotation_text=f"Pipeline 1901–2015 mean {mean_all:,.0f} mm",
                   annotation_font_color=_TEXT_COLOR)
    fig6.add_hline(y=mean_all * 0.9, line_dash="dot", line_color="#dc2626" if not _DARK else "#ef4444",
                   annotation_text="90% of normal (dry threshold)",
                   annotation_font_color=_TEXT_COLOR)
    fig6.update_layout(
        title=dict(
            text="All-India annual rainfall 1901–2026 — blue: pipeline (1901–2015) · amber: observed IMD (2016–2025) · red bars below 90%",
            font=dict(color=_TITLE_COLOR, size=15, family="'Outfit', 'Plus Jakarta Sans', sans-serif"),
        ),
        height=400, **_PAPER,
        xaxis=dict(
            title=dict(text="Year", font=dict(color=_TEXT_COLOR)),
            tickfont=dict(color=_TEXT_COLOR),
            gridcolor=_GRID_C,
        ),
        yaxis=dict(
            title=dict(text="mm", font=dict(color=_TEXT_COLOR)),
            tickfont=dict(color=_TEXT_COLOR),
            gridcolor=_GRID_C,
        ),
        legend=dict(
            orientation="h", y=1.13, x=0,
            font=dict(color=_TEXT_COLOR),
        ),
        bargap=0.2,
        margin=dict(t=55),
    )
    st.plotly_chart(fig6, use_container_width=True, theme=None, key="fig_macro_national_trend")

    col_x1, col_x2, col_x3 = st.columns(3)
    with col_x1:
        st.markdown('<div class="kpi green" style="margin:0"><div class="v">16 → 9</div><div class="l">raw-significant divisions surviving BH at 5% FDR</div></div>', unsafe_allow_html=True)
    with col_x2:
        inc = int((agg["trend"] > 0).sum())
        st.markdown(f'<div class="kpi blue" style="margin:0"><div class="v">{inc} / {len(agg)}</div><div class="l">divisions with a positive slope</div></div>', unsafe_allow_html=True)
    with col_x3:
        st.markdown(f'<div class="kpi purple" style="margin:0"><div class="v">78.6%</div><div class="l">of division pairs correlate — tests are not independent</div></div>', unsafe_allow_html=True)

    # 5 headline findings (from VARSA)
    st.markdown(f"<div style='margin-top:1.5rem;font-weight:750;font-size:1.05rem;color:{T['title']};margin-bottom:0.6rem;'>Five things the multi-region record tells us:</div>", unsafe_allow_html=True)
    f1, f2, f3, f4, f5 = st.columns(5)
    findings = [
        ("Rain is concentrated", "75.2% falls Jun–Sep; month alone explains 41% of variance."),
        ("Regions differ sharply", "Region explains 87% of monsoon variance; CV 12% → 41%."),
        ("Normal is the wrong model", "Monsoon totals are right-skewed; Gamma & Lognormal fit better."),
        ("Trends need caution", "16 of 36 look significant, but only 9 survive correction."),
        ("Drought risk is local", "1-in-20-year deficit: 47.6% of normal in W Rajasthan vs 77.8% in Kerala."),
    ]
    for col, (t, d) in zip([f1, f2, f3, f4, f5], findings):
        with col:
            st.markdown('<div class="kpi" style="min-height:150px">'
                        f'<div style="font-weight:750;font-size:0.92rem;color:{T["title"]};margin-bottom:0.4rem;">' + t +
                        f'</div><div style="margin-top:0.35rem;font-size:0.83rem;color:{T["muted"]};line-height:1.45;">' + d + '</div></div>',
                        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if CD and CD in df["division"].unique():
    with st.expander("🌐 Compare with All Other States (View Macro Benchmark Comparisons)", expanded=False):
        render_all_states_comparison()
else:
    st.markdown(textwrap.dedent(f'''
    <div style="background:{T['card2']}; border:1px solid {T['border']}; border-radius:18px; padding:16px 22px; margin:1.2rem 0; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
      <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:1.6rem;">🗺️</span>
        <div>
          <b style="font-size:0.95rem; color:{T['title']};">All-India Comparisons Active</b>
          <p style="margin:2px 0 0; font-size:0.84rem; color:{T['muted']};">Showing all 36 subdivisions across India. Click any dot on the map or select a quick-jump region to inspect a single place's dossier.</p>
        </div>
      </div>
    </div>
    ''').strip(), unsafe_allow_html=True)
    render_all_states_comparison()

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="foot">
  <b style="color:#94a3b8">VARSA</b> · Variability, Anomalies and Regional Statistics of Indian Rainfall<br>
  Data: India Meteorological Department (IMD) · pipeline layer 1901–2015 + observed IMD 2016–2026 · 36 subdivisions<br>
  Probability &amp; Statistics (BAMAT207) · Dr. Juhi Baroi · Pratik 25BCE0337 · Adarsh 25BCE0401 · Arunya 25BCE0344
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.foot + div { display:none; }
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)
