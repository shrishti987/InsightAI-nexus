import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


PREF_PATH = Path(".insightai_preferences.json")


def load_preferences():
    if "preferences_loaded" in st.session_state:
        return

    defaults = {"theme": "dark", "bookmarks": [], "recent_activity": []}
    try:
        saved = json.loads(PREF_PATH.read_text(encoding="utf-8"))
        defaults.update(saved)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    st.session_state.setdefault("theme", defaults["theme"])
    st.session_state.setdefault("bookmarks", defaults["bookmarks"])
    st.session_state.setdefault("recent_activity", defaults["recent_activity"])
    st.session_state["preferences_loaded"] = True


def save_preferences():
    payload = {
        "theme": st.session_state.get("theme", "dark"),
        "bookmarks": st.session_state.get("bookmarks", []),
        "recent_activity": st.session_state.get("recent_activity", []),
    }
    try:
        PREF_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError:
        st.toast("Preference sync is unavailable on this device.")


def add_activity(message, level="info"):
    item = {
        "message": message,
        "level": level,
        "time": time.strftime("%I:%M %p"),
    }
    activity = [item] + st.session_state.get("recent_activity", [])
    st.session_state["recent_activity"] = activity[:8]
    save_preferences()


def apply_premium_theme():
    load_preferences()
    is_light = st.session_state.get("theme") == "light"
    colors = {
        "bg": "#f7f8fb" if is_light else "#070b13",
        "panel": "#ffffff" if is_light else "#0e1422",
        "panel_2": "#eef2ff" if is_light else "#111827",
        "text": "#172033" if is_light else "#f8fafc",
        "muted": "#5b667a" if is_light else "#a7b1c2",
        "border": "#dbe3ef" if is_light else "#223049",
        "accent": "#2563eb",
        "accent_2": "#14b8a6",
        "warning": "#f59e0b",
        "danger": "#ef4444",
    }
    st.session_state["theme_colors"] = colors
    st.markdown(
        f"""
        <style>
        :root {{
            --bg: {colors["bg"]};
            --panel: {colors["panel"]};
            --panel-2: {colors["panel_2"]};
            --text: {colors["text"]};
            --muted: {colors["muted"]};
            --border: {colors["border"]};
            --accent: {colors["accent"]};
            --accent-2: {colors["accent_2"]};
            --warning: {colors["warning"]};
            --danger: {colors["danger"]};
        }}
        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(37,99,235,.16), transparent 32rem),
                linear-gradient(135deg, var(--bg), {"#eaf0ff" if is_light else "#05070c"});
            color: var(--text);
        }}
        section[data-testid="stSidebar"] {{
            background: var(--panel);
            border-right: 1px solid var(--border);
        }}
        h1, h2, h3, h4, p, label, span, div {{
            letter-spacing: 0;
        }}
        h1, h2, h3 {{
            color: var(--text);
        }}
        p, label, .stMarkdown, [data-testid="stCaptionContainer"] {{
            color: var(--muted);
        }}
        .main .block-container {{
            padding-top: 1.4rem;
            max-width: 1320px;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: var(--border);
            background: color-mix(in srgb, var(--panel) 92%, transparent);
            border-radius: 10px;
            transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            transform: translateY(-2px);
            border-color: color-mix(in srgb, var(--accent) 55%, var(--border));
            box-shadow: 0 16px 40px rgba(2, 6, 23, .16);
        }}
        .hero {{
            padding: 1.2rem 0 .4rem;
        }}
        .hero h1 {{
            font-size: clamp(2.1rem, 5vw, 4.7rem);
            line-height: .96;
            margin: 0 0 1rem;
        }}
        .hero p {{
            font-size: 1.05rem;
            max-width: 720px;
        }}
        .eyebrow {{
            color: var(--accent-2);
            text-transform: uppercase;
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .08em;
            margin-bottom: .6rem;
        }}
        .stButton > button, .stDownloadButton > button {{
            border: 0;
            border-radius: 8px;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: #fff;
            font-weight: 800;
            min-height: 2.8rem;
            transition: transform .16s ease, filter .16s ease, box-shadow .16s ease;
            box-shadow: 0 10px 26px rgba(37,99,235,.24);
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            transform: translateY(-1px) scale(1.01);
            filter: brightness(1.06);
        }}
        .stButton > button:active, .stDownloadButton > button:active {{
            transform: scale(.98);
        }}
        [data-testid="metric-container"] {{
            background: var(--panel);
            border: 1px solid var(--border);
            padding: 1rem;
            border-radius: 10px;
            transition: transform .18s ease, border-color .18s ease;
        }}
        [data-testid="metric-container"]:hover {{
            transform: translateY(-2px);
            border-color: var(--accent);
        }}
        .fab {{
            position: fixed;
            right: 1.2rem;
            bottom: 1.2rem;
            z-index: 999;
            width: 3.35rem;
            height: 3.35rem;
            border-radius: 999px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: #fff;
            font-size: 1.35rem;
            box-shadow: 0 20px 44px rgba(20,184,166,.28);
            animation: floatIn .35s ease both;
        }}
        @keyframes floatIn {{
            from {{ opacity: 0; transform: translateY(14px) scale(.9); }}
            to {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}
        .chip {{
            display: inline-flex;
            align-items: center;
            gap: .35rem;
            padding: .34rem .7rem;
            border-radius: 999px;
            background: var(--panel-2);
            color: var(--text);
            border: 1px solid var(--border);
            margin: .15rem .25rem .15rem 0;
            font-size: .84rem;
        }}
        .timeline-item {{
            border-left: 2px solid var(--accent);
            padding: .1rem 0 .75rem .85rem;
            margin-left: .35rem;
        }}
        .timeline-item strong {{
            color: var(--text);
        }}
        .search-hit {{
            background: rgba(20,184,166,.16);
            color: var(--text);
            border-radius: 4px;
            padding: .04rem .18rem;
            font-weight: 800;
        }}
        .empty-state {{
            text-align: center;
            padding: 2.5rem 1rem;
            border: 1px dashed var(--border);
            border-radius: 10px;
            background: color-mix(in srgb, var(--panel) 78%, transparent);
        }}
        .step {{
            display: flex;
            align-items: center;
            gap: .65rem;
            color: var(--muted);
        }}
        .step-num {{
            width: 1.85rem;
            height: 1.85rem;
            border-radius: 999px;
            display: grid;
            place-items: center;
            background: var(--panel-2);
            border: 1px solid var(--border);
            color: var(--text);
            font-weight: 800;
        }}
        .step.active .step-num {{
            background: var(--accent);
            color: #fff;
            border-color: var(--accent);
        }}
        .pulse {{
            animation: pulse .9s ease-in-out infinite alternate;
        }}
        @keyframes pulse {{
            from {{ opacity: .55; }}
            to {{ opacity: 1; }}
        }}
        @media (max-width: 760px) {{
            .main .block-container {{ padding-inline: 1rem; }}
            .hero h1 {{ font-size: 2.35rem; }}
            .fab {{ right: .85rem; bottom: .85rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_controls():
    load_preferences()
    st.sidebar.markdown("### Workspace")
    theme_choice = st.sidebar.toggle(
        "Light mode",
        value=st.session_state.get("theme") == "light",
        help="Switch the interface theme. Your choice is remembered.",
    )
    next_theme = "light" if theme_choice else "dark"
    if next_theme != st.session_state.get("theme"):
        st.session_state["theme"] = next_theme
        save_preferences()
        st.toast(f"{next_theme.title()} mode enabled")
        st.rerun()

    with st.sidebar.expander("Notifications", expanded=False):
        activity = st.session_state.get("recent_activity", [])
        if not activity:
            st.caption("No notifications yet.")
        for item in activity[:5]:
            st.markdown(f"**{item['time']}**  \n{item['message']}")


def render_fab():
    st.markdown(
        '<div class="fab" title="Quick action: generate fresh insight">+</div>',
        unsafe_allow_html=True,
    )


def empty_state(title, body, asset=None):
    image_html = f'<img src="{asset}" width="150" />' if asset else ""
    st.markdown(
        f"""
        <div class="empty-state">
            {image_html}
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dataset_profile(df):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    date_cols = [
        col for col in df.columns
        if "date" in col.lower() or pd.api.types.is_datetime64_any_dtype(df[col])
    ]
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing": int(df.isnull().sum().sum()),
        "numeric": len(numeric_cols),
        "categorical": len(categorical_cols),
        "duplicates": int(df.duplicated().sum()),
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "date_cols": date_cols,
    }


def generate_smart_insights(df):
    profile = dataset_profile(df)
    insights = [
        f"Dataset has {profile['rows']:,} rows, {profile['columns']} columns, and {profile['missing']:,} missing values.",
        f"{profile['numeric']} numeric and {profile['categorical']} categorical fields are available for analysis.",
    ]

    if profile["duplicates"]:
        insights.append(f"{profile['duplicates']:,} duplicate rows may need review before modeling.")
    else:
        insights.append("No duplicate rows were detected in this sample.")

    numeric_cols = profile["numeric_cols"]
    if numeric_cols:
        missing_by_col = df[numeric_cols].isna().mean().sort_values(ascending=False)
        if missing_by_col.iloc[0] > 0:
            insights.append(f"{missing_by_col.index[0]} has the highest missing-rate among numeric columns.")

        variable_col = df[numeric_cols].std(numeric_only=True).sort_values(ascending=False)
        if not variable_col.empty and pd.notna(variable_col.iloc[0]):
            insights.append(f"{variable_col.index[0]} shows the strongest spread and is worth monitoring.")

    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True).abs()
        np.fill_diagonal(corr.values, 0)
        strongest = corr.stack().sort_values(ascending=False)
        if not strongest.empty:
            pair = strongest.index[0]
            score = strongest.iloc[0]
            insights.append(f"{pair[0]} and {pair[1]} have the strongest relationship ({score:.2f}).")

    if profile["categorical_cols"]:
        col = profile["categorical_cols"][0]
        top = df[col].astype(str).value_counts().head(1)
        if not top.empty:
            insights.append(f"{top.index[0]} is the most common value in {col}.")

    return insights


def build_dashboard_charts(df, category=None):
    colors = st.session_state.get("theme_colors", {})
    numeric_cols = dataset_profile(df)["numeric_cols"]
    categorical_cols = dataset_profile(df)["categorical_cols"]
    charts = []

    if numeric_cols:
        y_col = numeric_cols[0]
        trend_df = df[[y_col]].dropna().reset_index().tail(80)
        if not trend_df.empty:
            charts.append(
                (
                    "Trend",
                    px.line(
                        trend_df,
                        x="index",
                        y=y_col,
                        markers=True,
                        color_discrete_sequence=[colors.get("accent", "#2563eb")],
                    ),
                )
            )

        charts.append(
            (
                "Distribution",
                px.histogram(
                    df,
                    x=y_col,
                    nbins=28,
                    color_discrete_sequence=[colors.get("accent_2", "#14b8a6")],
                ),
            )
        )

    if categorical_cols:
        cat_col = category or categorical_cols[0]
        top_df = df[cat_col].astype(str).value_counts().head(8).reset_index()
        top_df.columns = [cat_col, "count"]
        if not top_df.empty:
            charts.append(
                (
                    "Category Mix",
                    px.bar(
                        top_df,
                        x=cat_col,
                        y="count",
                        color="count",
                        color_continuous_scale="Blues",
                    ),
                )
            )
            charts.append(
                (
                    "Share",
                    px.pie(top_df, names=cat_col, values="count", hole=.55),
                )
            )

    for _, fig in charts:
        fig.update_layout(
            template="plotly_white" if st.session_state.get("theme") == "light" else "plotly_dark",
            margin=dict(l=12, r=12, t=32, b=12),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, Segoe UI, sans-serif"),
        )
    return charts


def highlight_match(value, query):
    text = str(value)
    if not query:
        return text
    lower = text.lower()
    needle = query.lower()
    idx = lower.find(needle)
    if idx < 0:
        return text
    return (
        text[:idx]
        + '<span class="search-hit">'
        + text[idx: idx + len(query)]
        + "</span>"
        + text[idx + len(query):]
    )


def search_dataframe(df, query, columns):
    if not query:
        return df.copy()
    if not columns:
        columns = df.columns.tolist()
    mask = pd.Series(False, index=df.index)
    for col in columns:
        mask = mask | df[col].astype(str).str.contains(query, case=False, na=False)
    return df[mask]


def render_activity_timeline():
    activity = st.session_state.get("recent_activity", [])
    if not activity:
        st.caption("Activity appears here as you explore, save, and generate insights.")
        return
    for item in activity:
        st.markdown(
            f"""
            <div class="timeline-item">
                <strong>{item['time']}</strong><br />
                <span>{item['message']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
