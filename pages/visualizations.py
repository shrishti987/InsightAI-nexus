import streamlit as st
import plotly.express as px

from utils.ui import add_activity, apply_premium_theme, dataset_profile, empty_state, render_fab, render_sidebar_controls


apply_premium_theme()
render_sidebar_controls()
render_fab()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Visual Lab</div>
        <h1>Explore patterns interactively.</h1>
        <p>Build focused charts with clean controls, hover states, and responsive Plotly views.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "df" not in st.session_state:
    empty_state("No dataset loaded", "Load data from the main workspace to unlock the visual lab.")
    st.stop()

df = st.session_state["df"]
if df is None or df.empty:
    empty_state("Dataset is empty", "Charts need a valid dataset with rows and columns.")
    st.stop()

profile = dataset_profile(df)
numeric_cols = [col for col in profile["numeric_cols"] if "id" not in col.lower()]
categorical_cols = profile["categorical_cols"]

if not numeric_cols and not categorical_cols:
    empty_state("No chartable fields", "InsightAI needs numeric or categorical columns to build visualizations.")
    st.stop()

control_col, chart_col = st.columns([.85, 1.7])
with control_col:
    with st.container(border=True):
        st.markdown("#### Chart Controls")
        chart_type = st.selectbox("Chart type", ["Auto", "Scatter", "Line", "Histogram", "Box", "Bar", "Pie", "Correlation"])
        sample_rows = st.slider("Sample rows", 50, max(50, min(len(df), 1000)), min(len(df), 400), step=50)
        color_col = st.selectbox("Color by", ["None"] + categorical_cols) if categorical_cols else "None"
        build_chart = st.button("Generate chart", type="primary", width="stretch")

work_df = df.head(sample_rows)
fig = None
title = "Chart"

try:
    if chart_type == "Auto":
        chart_type = "Scatter" if len(numeric_cols) >= 2 else "Histogram" if numeric_cols else "Bar"

    if chart_type == "Scatter" and len(numeric_cols) >= 2:
        x_col = st.selectbox("X axis", numeric_cols)
        y_col = st.selectbox("Y axis", numeric_cols, index=min(1, len(numeric_cols) - 1))
        fig = px.scatter(work_df, x=x_col, y=y_col, color=None if color_col == "None" else color_col)
        title = f"{x_col} vs {y_col}"
    elif chart_type == "Line" and numeric_cols:
        y_col = st.selectbox("Line metric", numeric_cols)
        fig = px.line(work_df.reset_index(), x="index", y=y_col, markers=True)
        title = f"{y_col} trend"
    elif chart_type == "Histogram" and numeric_cols:
        x_col = st.selectbox("Distribution column", numeric_cols)
        fig = px.histogram(work_df, x=x_col, nbins=32, color=None if color_col == "None" else color_col)
        title = f"{x_col} distribution"
    elif chart_type == "Box" and numeric_cols:
        y_col = st.selectbox("Box metric", numeric_cols)
        fig = px.box(work_df, y=y_col, color=None if color_col == "None" else color_col)
        title = f"{y_col} spread"
    elif chart_type == "Bar" and categorical_cols:
        cat_col = st.selectbox("Category", categorical_cols)
        top_df = work_df[cat_col].astype(str).value_counts().head(12).reset_index()
        top_df.columns = [cat_col, "count"]
        fig = px.bar(top_df, x=cat_col, y="count", color="count", color_continuous_scale="Blues")
        title = f"Top {cat_col} values"
    elif chart_type == "Pie" and categorical_cols:
        cat_col = st.selectbox("Category", categorical_cols)
        top_df = work_df[cat_col].astype(str).value_counts().head(8).reset_index()
        top_df.columns = [cat_col, "count"]
        fig = px.pie(top_df, names=cat_col, values="count", hole=.5)
        title = f"{cat_col} share"
    elif chart_type == "Correlation" and len(numeric_cols) >= 2:
        fig = px.imshow(work_df[numeric_cols].corr(numeric_only=True), text_auto=True, color_continuous_scale="RdBu")
        title = "Correlation map"
except Exception as exc:
    st.toast("Chart failed to render")
    st.error(f"Could not generate that chart: {exc}")

with chart_col:
    with st.container(border=True):
        st.markdown(f"#### {title}")
        if fig is None:
            empty_state("Choose compatible fields", "Try another chart type or use a dataset with richer numeric/category fields.")
        else:
            fig.update_layout(
                template="plotly_white" if st.session_state.get("theme") == "light" else "plotly_dark",
                margin=dict(l=12, r=12, t=32, b=12),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, width="stretch")
            if build_chart:
                st.toast("Chart generated")
                add_activity(f"Generated {title} chart", "success")
