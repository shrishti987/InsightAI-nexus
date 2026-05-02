import time

import pandas as pd
import streamlit as st

from utils.recommendation import recommend_analysis
from utils.ui import (
    add_activity,
    apply_premium_theme,
    build_dashboard_charts,
    dataset_profile,
    empty_state,
    generate_smart_insights,
    highlight_match,
    render_activity_timeline,
    render_fab,
    render_sidebar_controls,
    save_preferences,
    search_dataframe,
)


st.set_page_config(page_title="InsightAI", page_icon="IA", layout="wide")
apply_premium_theme()
render_sidebar_controls()
render_fab()


@st.cache_data(show_spinner=False)
def load_data(file):
    try:
        df = pd.read_csv(file)
        df = df.loc[:, ~df.columns.duplicated()]
        return df if not df.empty else None
    except pd.errors.EmptyDataError:
        return None
    except Exception as exc:
        st.session_state["last_upload_error"] = str(exc)
        return None


def load_sample_dataset(name):
    path = f"data/{name}"
    return pd.read_csv(path)


st.sidebar.markdown("### Dataset")
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type=["csv"],
    help="Drop in a CSV and InsightAI will profile it instantly.",
)

sample_choice = st.sidebar.selectbox(
    "Or explore a sample",
    ["No sample", "sales_dataset_500.csv", "finance_dataset_500.csv", "healthcare_dataset_500.csv"],
)

if uploaded_file is not None:
    with st.spinner("Reading your dataset..."):
        df = load_data(uploaded_file)
    if df is not None:
        st.session_state["df"] = df
        st.session_state["dataset_name"] = uploaded_file.name
        st.toast("Dataset uploaded successfully")
        add_activity(f"Uploaded {uploaded_file.name}", "success")
    else:
        st.toast("Could not read that CSV")
        st.error("The uploaded file is empty or not a valid CSV.")

if sample_choice != "No sample" and st.sidebar.button("Load sample", width="stretch"):
    with st.spinner("Preparing sample workspace..."):
        st.session_state["df"] = load_sample_dataset(sample_choice)
        st.session_state["dataset_name"] = sample_choice
        time.sleep(.35)
    st.toast("Sample dataset loaded")
    add_activity(f"Loaded sample {sample_choice}", "success")
    st.rerun()


st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">AI Analytics Workspace</div>
        <h1>InsightAI</h1>
        <p>
            Upload data, find patterns, generate recommendations, and move from raw CSV
            to a decision-ready dashboard in one polished flow.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

hero_col, action_col = st.columns([1.8, 1])
with hero_col:
    st.markdown(
        '<span class="chip">Live dashboard</span><span class="chip">Smart search</span>'
        '<span class="chip">AI insights</span><span class="chip">Persistent preferences</span>',
        unsafe_allow_html=True,
    )
with action_col:
    primary_clicked = st.button(
        "Analyze dataset",
        type="primary",
        width="stretch",
        help="Runs a fresh insight pass on the active dataset.",
    )


if "df" not in st.session_state:
    st.progress(18, text="Step 1 of 4: upload or load a dataset")
    step_cols = st.columns(4)
    labels = ["Load data", "Profile", "Explore", "Export"]
    for idx, col in enumerate(step_cols, start=1):
        col.markdown(
            f'<div class="step {"active" if idx == 1 else ""}"><span class="step-num">{idx}</span>{labels[idx-1]}</div>',
            unsafe_allow_html=True,
        )

    empty_state(
        "Your analytics workspace is ready",
        "Upload a CSV from the sidebar or load a sample dataset to unlock charts, search, AI recommendations, and report actions.",
    )

    with st.container(border=True):
        st.subheader("What opens up after loading data")
        c1, c2, c3 = st.columns(3)
        c1.metric("Dashboard cards", "6", "+ charts")
        c2.metric("Smart actions", "8", "CTA, FAB, save")
        c3.metric("UX states", "Ready", "loading + toast")
    st.stop()


df = st.session_state["df"]
dataset_name = st.session_state.get("dataset_name", "Active dataset")
profile = dataset_profile(df)
recommendation = recommend_analysis(df)

if primary_clicked:
    progress = st.progress(0, text="Profiling schema...")
    for value, label in [(28, "Scanning missing values..."), (56, "Building recommendations..."), (82, "Ranking signals..."), (100, "Done")]:
        time.sleep(.18)
        progress.progress(value, text=label)
    st.session_state["generated_insights"] = generate_smart_insights(df)
    st.toast("Fresh insights generated")
    add_activity("Generated a fresh insight pack", "success")


st.progress(76, text="Step 3 of 4: explore and refine your analysis")
step_cols = st.columns(4)
labels = ["Load data", "Profile", "Explore", "Export"]
for idx, col in enumerate(step_cols, start=1):
    col.markdown(
        f'<div class="step {"active" if idx <= 3 else ""}"><span class="step-num">{idx}</span>{labels[idx-1]}</div>',
        unsafe_allow_html=True,
    )

st.sidebar.success(f"Active: {dataset_name}")
st.sidebar.write("Rows:", f"{profile['rows']:,}")
st.sidebar.write("Columns:", profile["columns"])
with st.sidebar.expander("Saved items", expanded=False):
    bookmarks = st.session_state.get("bookmarks", [])
    if bookmarks:
        for item in bookmarks:
            st.write("-", item)
    else:
        st.caption("Saved insights and views appear here.")


st.subheader("Command Center")
metric_cols = st.columns(6)
metric_cols[0].metric("Rows", f"{profile['rows']:,}")
metric_cols[1].metric("Columns", profile["columns"])
metric_cols[2].metric("Missing", f"{profile['missing']:,}")
metric_cols[3].metric("Numeric", profile["numeric"])
metric_cols[4].metric("Categories", profile["categorical"])
metric_cols[5].metric("Duplicates", f"{profile['duplicates']:,}")

left, right = st.columns([1.25, .75])
with left:
    with st.container(border=True):
        st.markdown("#### Smart Search")
        search_cols = st.multiselect(
            "Search within columns",
            options=df.columns.tolist(),
            default=df.columns.tolist()[: min(5, len(df.columns))],
        )
        query = st.text_input(
            "Search rows",
            placeholder="Type to search live suggestions...",
            help="Matches are highlighted in the live suggestions below.",
        )
        sort_col = st.selectbox("Sort by", df.columns.tolist())
        sort_dir = st.radio("Direction", ["Ascending", "Descending"], horizontal=True)
        result_df = search_dataframe(df, query, search_cols)
        if sort_col in result_df.columns:
            result_df = result_df.sort_values(sort_col, ascending=sort_dir == "Ascending", kind="mergesort")

        st.caption(f"{len(result_df):,} matching rows")
        if query and result_df.empty:
            empty_state("No matching rows", "Try a broader keyword or search across more columns.")
        else:
            preview = result_df.head(8)
            st.dataframe(preview, width="stretch", hide_index=True)
            if query:
                suggestions = []
                for _, row in preview.head(5).iterrows():
                    text = " | ".join(highlight_match(row[col], query) for col in search_cols[:3] if col in row)
                    suggestions.append(f"<li>{text}</li>")
                st.markdown("<ul>" + "".join(suggestions) + "</ul>", unsafe_allow_html=True)

with right:
    with st.container(border=True):
        st.markdown("#### AI Recommendation")
        st.info(recommendation)
        if st.button("Save recommendation", width="stretch", help="Bookmark this recommendation"):
            bookmark = f"{dataset_name}: {recommendation}"
            if bookmark not in st.session_state["bookmarks"]:
                st.session_state["bookmarks"].append(bookmark)
            save_preferences()
            st.toast("Recommendation saved")
            add_activity("Saved a recommendation", "success")

    with st.container(border=True):
        st.markdown("#### Notifications")
        render_activity_timeline()


st.subheader("Interactive Dashboard")
filter_col, category_col = st.columns([1, 1])
with filter_col:
    sample_size = st.slider("Rows used in charts", 50, max(50, min(len(df), 500)), min(len(df), 300), step=25)
with category_col:
    category = None
    if profile["categorical_cols"]:
        category = st.selectbox("Category filter", ["All"] + profile["categorical_cols"])
        category = None if category == "All" else category

dashboard_df = df.head(sample_size)
charts = build_dashboard_charts(dashboard_df, category=category)
if not charts:
    empty_state("No visual chart data", "This dataset needs at least one numeric or categorical column for dashboard charts.")
else:
    chart_cols = st.columns(2)
    for idx, (title, fig) in enumerate(charts):
        with chart_cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"#### {title}")
                st.plotly_chart(fig, width="stretch")


st.subheader("Generated Insight Pack")
if "generated_insights" not in st.session_state:
    with st.container(border=True):
        st.markdown('<p class="pulse">Insight pack is waiting for your first analysis run.</p>', unsafe_allow_html=True)
        if st.button("Generate Insight", width="stretch", help="Creates AI-style recommendations from the active data profile."):
            with st.spinner("Generating insight pack..."):
                time.sleep(.45)
                st.session_state["generated_insights"] = generate_smart_insights(df)
            st.toast("Insight pack ready")
            add_activity("Generated insight pack from dashboard", "success")
            st.rerun()
else:
    for insight in st.session_state["generated_insights"]:
        with st.container(border=True):
            st.write(insight)

    col_a, col_b = st.columns(2)
    if col_a.button("Regenerate insights", width="stretch"):
        with st.spinner("Refreshing recommendations..."):
            time.sleep(.4)
            st.session_state["generated_insights"] = generate_smart_insights(df)
        st.toast("Insights refreshed")
        add_activity("Regenerated insight pack", "success")
        st.rerun()
    if col_b.button("Clear insight pack", width="stretch"):
        if "generated_insights" in st.session_state:
            del st.session_state["generated_insights"]
        st.toast("Insight pack cleared")
        add_activity("Cleared insight pack", "info")
        st.rerun()
