import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Manufacturing Opportunity Intelligence",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Manufacturing Opportunity Intelligence")
st.caption("Government schemes, subsidies, grants and funding opportunities for Indian manufacturing.")

DATA_FILE = Path("data/schemes.csv")

if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "scheme_name",
        "ministry",
        "sector",
        "state",
        "benefit",
        "eligibility",
        "deadline",
        "source_url"
    ])

# Sidebar
st.sidebar.header("Filters")

if not df.empty:
    sectors = ["All"] + sorted(df["sector"].dropna().unique().tolist())
    selected_sector = st.sidebar.selectbox("Sector", sectors)

    if selected_sector != "All":
        df = df[df["sector"] == selected_sector]

    search = st.sidebar.text_input(
        "Search",
        placeholder="e.g. machinery, MSME, electronics"
    )

    if search:
        mask = df.astype(str).apply(
            lambda row: row.str.contains(search, case=False, na=False).any(),
            axis=1
        )
        df = df[mask]

# KPIs
c1, c2, c3 = st.columns(3)

c1.metric("Opportunities", len(df))
c2.metric(
    "Manufacturing / MSME",
    len(df[df.astype(str).apply(
        lambda x: x.str.contains(
            "manufactur|MSME|industrial",
            case=False,
            na=False
        ).any(),
        axis=1
    )]) if not df.empty else 0
)
c3.metric(
    "States / Sources",
    df["state"].nunique() if "state" in df.columns and not df.empty else 0
)

st.divider()

if df.empty:
    st.info(
        "No scheme data has been loaded yet. "
        "The next step will connect this dashboard to government sources."
    )
else:
    st.subheader("Government Opportunities")

    display_columns = [
        "scheme_name",
        "ministry",
        "sector",
        "state",
        "benefit",
        "eligibility",
        "deadline"
    ]

    available = [c for c in display_columns if c in df.columns]

    st.dataframe(
        df[available],
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.caption(
    "Data is collected from public government sources. "
    "Always verify eligibility and deadlines on the official source."
)
