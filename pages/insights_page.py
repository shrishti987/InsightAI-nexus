import time

import streamlit as st

from utils.ui import (
    add_activity,
    apply_premium_theme,
    empty_state,
    generate_smart_insights,
    render_fab,
    render_sidebar_controls,
    save_preferences,
)


apply_premium_theme()
render_sidebar_controls()
render_fab()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">AI Insights</div>
        <h1>Generate recommendations you can act on.</h1>
        <p>Run a smart scan for quality risks, correlations, category leaders, and modeling opportunities.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "df" not in st.session_state:
    empty_state("No data to analyze", "Upload or load a dataset from the main workspace to generate insights.")
    st.stop()

df = st.session_state["df"]
if df is None or df.empty:
    empty_state("Dataset is empty", "A valid dataset is required before InsightAI can generate recommendations.")
    st.stop()

cta_col, save_col = st.columns([1.4, 1])
with cta_col:
    run = st.button("Generate Insight", type="primary", width="stretch", help="Runs a fresh smart scan.")
with save_col:
    save_all = st.button("Save current insights", width="stretch")

if run or "page_insights" not in st.session_state:
    with st.spinner("Generating insight cards..."):
        progress = st.progress(0, text="Profiling columns...")
        for value, label in [(30, "Checking data quality..."), (62, "Finding relationships..."), (100, "Packaging insights...")]:
            time.sleep(.18)
            progress.progress(value, text=label)
        st.session_state["page_insights"] = generate_smart_insights(df)
    st.toast("Insights generated")
    add_activity("Generated insights from Insights page", "success")

if save_all:
    for insight in st.session_state.get("page_insights", []):
        if insight not in st.session_state["bookmarks"]:
            st.session_state["bookmarks"].append(insight)
    save_preferences()
    st.toast("Insights saved")
    add_activity("Saved insight cards", "success")

st.subheader("Insight Cards")
for idx, insight in enumerate(st.session_state.get("page_insights", []), start=1):
    with st.container(border=True):
        st.markdown(f"#### Insight {idx}")
        st.write(insight)
        if st.button("Bookmark", key=f"bookmark_insight_{idx}", width="stretch"):
            if insight not in st.session_state["bookmarks"]:
                st.session_state["bookmarks"].append(insight)
                save_preferences()
            st.toast("Insight bookmarked")
