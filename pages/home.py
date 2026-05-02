import time

import streamlit as st

from utils.ui import add_activity, apply_premium_theme, empty_state, render_fab, render_sidebar_controls


apply_premium_theme()
render_sidebar_controls()
render_fab()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Welcome</div>
        <h1>Turn datasets into decisions.</h1>
        <p>
            InsightAI gives you a focused analytics workspace with profiling,
            visual exploration, AI-style recommendations, and report-ready output.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1.5, 1])
with col1:
    if st.button("Get Started", type="primary", width="stretch"):
        progress = st.progress(0, text="Opening workspace...")
        for value, label in [(35, "Checking data state..."), (70, "Preparing dashboard..."), (100, "Ready")]:
            time.sleep(.16)
            progress.progress(value, text=label)
        st.toast("Workspace is ready")
        add_activity("Started a new InsightAI session", "success")
with col2:
    st.image("assets/insight.svg", width="stretch")

st.divider()

st.subheader("Product Flow")
steps = st.columns(4)
for idx, label in enumerate(["Upload", "Profile", "Analyze", "Export"], start=1):
    steps[idx - 1].markdown(
        f'<div class="step {"active" if idx <= 2 else ""}"><span class="step-num">{idx}</span>{label}</div>',
        unsafe_allow_html=True,
    )

st.subheader("Core Capabilities")
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.markdown("#### Interactive EDA")
        st.write("Search, filter, sort, and inspect quality signals without leaving the workspace.")
with c2:
    with st.container(border=True):
        st.markdown("#### Smart Recommendations")
        st.write("Generate prioritized next steps from columns, missing values, spread, and correlations.")
with c3:
    with st.container(border=True):
        st.markdown("#### Report Actions")
        st.write("Save important findings and export analysis-ready summaries when you are done.")

if "df" not in st.session_state:
    empty_state("No dataset loaded yet", "Use the main app sidebar to upload a CSV or load a sample dataset.")
