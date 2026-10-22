#!/usr/bin/env python3
"""Fix the app.py header section."""
with open('app.py', 'r') as f:
    content = f.read()

# Find and fix the broken header section
broken = '''st.title("🌧� Indian Monsoon Rainfall Explorer")
st.markdown(
# ── "rainweb" button in main content ─────────────────────────────────────────
st.markdown("---")
col_b1, col_b2 = st.columns([2, 1])
with col_b2:
    if st.button("🔗 rainweb", type="primary", use_container_width=True):
        st.sidebar.success("🌐 Opening rainfall explorer...")
        st.rerun()

st.markdown("---")


    f"Analysis of IMD subdivision rainfall, <strong>1901–2015</strong> | "'''

fixed = '''st.title("🌧️ Indian Monsoon Rainfall Explorer")
st.markdown(
    f"Analysis of IMD subdivision rainfall, <strong>1901–2015</strong> | "
    f"{len(selected_divisions)} divisions | Season: <strong>{selected_season}</strong>"
)

# ── "rainweb" button in main content ─────────────────────────────────────────
st.markdown("---")
col_b1, col_b2 = st.columns([2, 1])
with col_b2:
    if st.button("🔗 rainweb", type="primary", use_container_width=True):
        st.sidebar.success("🌐 Opening rainfall explorer...")
        st.rerun()

st.markdown("---")'''

if broken in content:
    content = content.replace(broken, fixed)
    with open('app.py', 'w') as f:
        f.write(content)
    print("Fixed header section")
else:
    print("Pattern not found")
