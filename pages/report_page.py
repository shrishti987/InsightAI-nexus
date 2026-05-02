import time

import streamlit as st

from utils.report_generator import generate_report
from utils.ui import add_activity, apply_premium_theme, empty_state, render_fab, render_sidebar_controls


apply_premium_theme()
render_sidebar_controls()
render_fab()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Report Center</div>
        <h1>Package the analysis for handoff.</h1>
        <p>Generate a report preview, inspect it, and download a clean CSV export.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "df" not in st.session_state:
    empty_state("No dataset loaded", "Load data from the main workspace before generating a report.")
    st.stop()

df = st.session_state["df"]
if df is None or df.empty:
    empty_state("Dataset is empty", "Reports require a valid dataset.")
    st.stop()

left, right = st.columns([1.2, .8])
with left:
    generate = st.button("Generate report", type="primary", width="stretch")
with right:
    st.caption("Tip: saved recommendations remain available from the sidebar.")

if generate or "report" not in st.session_state:
    try:
        progress = st.progress(0, text="Collecting summary data...")
        for value, label in [(35, "Adding insights..."), (72, "Formatting rows..."), (100, "Ready")]:
            time.sleep(.18)
            progress.progress(value, text=label)
        st.session_state["report"] = generate_report(df)
        st.toast("Report generated")
        add_activity("Generated report preview", "success")
    except Exception as exc:
        st.error(f"Report generation failed: {exc}")
        st.toast("Report failed")
        st.stop()

report = st.session_state["report"]
st.subheader("Report Preview")
st.dataframe(report, width="stretch", hide_index=True)

csv = report.to_csv(index=False).encode()
st.download_button(
    label="Download AI Report",
    data=csv,
    file_name="insightai_report.csv",
    mime="text/csv",
    width="stretch",
)
