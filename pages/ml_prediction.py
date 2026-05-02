import time

import streamlit as st

from utils.automl import run_automl
from utils.deep_learning import run_deep_learning
from utils.prediction import sales_prediction
from utils.ui import add_activity, apply_premium_theme, dataset_profile, empty_state, render_fab, render_sidebar_controls


apply_premium_theme()
render_sidebar_controls()
render_fab()

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Prediction Studio</div>
        <h1>Run modeling when you are ready.</h1>
        <p>Use guided actions for baseline prediction, AutoML comparison, and deep learning feedback.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "df" not in st.session_state:
    empty_state("No dataset loaded", "Load data first to activate prediction workflows.")
    st.stop()

df = st.session_state["df"]
if df is None or df.empty:
    empty_state("Dataset is empty", "Prediction workflows require a valid dataset.")
    st.stop()

profile = dataset_profile(df)
if profile["numeric"] == 0:
    empty_state("No numeric features", "Add numeric columns before running prediction workflows.")
    st.stop()

st.subheader("Modeling Actions")
action_cols = st.columns(3)

with action_cols[0]:
    with st.container(border=True):
        st.markdown("#### Baseline Forecast")
        st.write("Fast estimate using the existing sales/value prediction utility.")
        if st.button("Run forecast", type="primary", width="stretch"):
            with st.spinner("Calculating forecast..."):
                time.sleep(.3)
                try:
                    prediction = sales_prediction(df)
                    st.success(f"Predicted future value: {prediction}")
                    st.toast("Forecast complete")
                    add_activity("Ran baseline forecast", "success")
                except Exception as exc:
                    st.error(f"Forecast failed: {exc}")
                    st.toast("Forecast failed")

with action_cols[1]:
    with st.container(border=True):
        st.markdown("#### AutoML Selection")
        st.write("Compare candidate models and surface the best option.")
        if st.button("Run AutoML", width="stretch"):
            try:
                progress = st.progress(0, text="Preparing models...")
                for value, label in [(35, "Training candidates..."), (70, "Scoring models..."), (100, "Done")]:
                    time.sleep(.22)
                    progress.progress(value, text=label)
                best_model, scores = run_automl(df)
                st.success(f"Best model: {best_model}")
                st.dataframe(scores, width="stretch")
                st.toast("AutoML complete")
                add_activity("Completed AutoML selection", "success")
            except Exception as exc:
                st.error(f"AutoML failed: {exc}")
                st.toast("AutoML failed")

with action_cols[2]:
    with st.container(border=True):
        st.markdown("#### Neural Check")
        st.write("Run a lightweight deep learning diagnostic and inspect loss.")
        if st.button("Run neural check", width="stretch"):
            try:
                with st.spinner("Training neural diagnostic..."):
                    dl_result = run_deep_learning(df)
                st.success(f"Neural network loss: {dl_result}")
                st.progress(max(0, min(100, int(100 - float(dl_result) * 10))), text="Model confidence proxy")
                st.toast("Neural diagnostic complete")
                add_activity("Ran neural diagnostic", "success")
            except Exception as exc:
                st.error(f"Neural diagnostic failed: {exc}")
                st.toast("Neural check failed")
