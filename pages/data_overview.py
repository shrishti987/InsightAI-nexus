import pandas as pd
import streamlit as st

from utils.ui import apply_premium_theme, dataset_profile, empty_state, render_fab, render_sidebar_controls, search_dataframe


apply_premium_theme()
render_sidebar_controls()
render_fab()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Data Overview</div>
        <h1>Know your dataset before you model it.</h1>
        <p>Inspect schema quality, missing values, samples, and searchable row previews.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "df" not in st.session_state:
    empty_state("Upload a dataset first", "The overview page becomes interactive once a CSV is loaded from the main workspace.")
    st.stop()

df = st.session_state["df"]
if df is None or df.empty:
    empty_state("Dataset is empty", "Try uploading a CSV with at least one row and one column.")
    st.stop()

profile = dataset_profile(df)
cols = st.columns(6)
cols[0].metric("Rows", f"{profile['rows']:,}")
cols[1].metric("Columns", profile["columns"])
cols[2].metric("Missing", f"{profile['missing']:,}")
cols[3].metric("Numeric", profile["numeric"])
cols[4].metric("Categories", profile["categorical"])
cols[5].metric("Duplicates", f"{profile['duplicates']:,}")

st.subheader("Live Row Explorer")
search_cols = st.multiselect("Columns", df.columns.tolist(), default=df.columns.tolist()[: min(6, len(df.columns))])
query = st.text_input("Search", placeholder="Find customers, categories, IDs, cities...")
filtered = search_dataframe(df, query, search_cols)
st.caption(f"{len(filtered):,} rows shown after filters")
st.dataframe(filtered.head(50), width="stretch", hide_index=True)

st.subheader("Column Health")
col_info = pd.DataFrame(
    {
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Non Null": df.count().values,
        "Missing": df.isnull().sum().values,
        "Unique": df.nunique(dropna=True).values,
    }
)
st.dataframe(col_info, width="stretch", hide_index=True)

if profile["numeric"]:
    st.subheader("Statistical Summary")
    st.dataframe(df.describe().T, width="stretch")
else:
    empty_state("No numeric columns", "Statistical summaries appear here when the dataset includes numeric fields.")
