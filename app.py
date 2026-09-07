import json
from pathlib import Path

import pandas as pd
import streamlit as st

SCHEMES_PATH = Path(__file__).parent / "data" / "schemes.json"

st.set_page_config(page_title="Manufacturing Scheme Tracker", layout="wide")
st.title("🏭 Manufacturing Scheme Tracker")
st.caption("Auto-updated daily from myScheme.gov.in and other public sources.")

if not SCHEMES_PATH.exists():
    st.warning("No data yet. Run the scraper pipeline first (see README).")
    st.stop()

raw = json.loads(SCHEMES_PATH.read_text())
df = pd.DataFrame(raw.values())

if df.empty:
    st.warning("data/schemes.json is empty. Run the scraper pipeline first.")
    st.stop()

# --- Filters ---
col1, col2, col3 = st.columns(3)

with col1:
    only_manufacturing = st.checkbox("Manufacturing-relevant only", value=True)

with col2:
    ministries = sorted(df["ministry"].dropna().unique().tolist())
    ministry_filter = st.multiselect("Ministry", ministries)

with col3:
    search = st.text_input("Search scheme name / eligibility")

filtered = df.copy()
if only_manufacturing and "manufacturing_relevant" in filtered.columns:
    filtered = filtered[filtered["manufacturing_relevant"] == True]  # noqa: E712
if ministry_filter:
    filtered = filtered[filtered["ministry"].isin(ministry_filter)]
if search:
    s = search.lower()
    filtered = filtered[
        filtered["scheme_name"].str.lower().str.contains(s, na=False)
        | filtered["eligibility_summary"].str.lower().str.contains(s, na=False)
    ]

st.markdown(f"**{len(filtered)}** schemes match your filters (of {len(df)} total collected)")

for _, row in filtered.sort_values("last_seen", ascending=False).iterrows():
    with st.expander(f"{row.get('scheme_name', 'Untitled scheme')}  —  {row.get('ministry') or 'Ministry not identified'}"):
        st.write(f"**Sectors:** {', '.join(row.get('sector_tags') or []) or '—'}")
        st.write(f"**Eligibility:** {row.get('eligibility_summary', '—')}")
        st.write(f"**Benefit:** {row.get('benefit_summary', '—')}")
        st.write(f"**Deadline:** {row.get('deadline') or 'Ongoing / not specified'}")
        st.write(f"**Confidence in extraction:** {row.get('confidence', '—')}")
        if row.get("url"):
            st.markdown(f"[Open official page]({row['url']})")
        st.caption(f"Last checked: {row.get('last_seen', '—')}")
