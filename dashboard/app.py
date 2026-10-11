"""Streamlit dashboard for the Financial AI Risk Engine."""

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 15


def api_request(method: str, path: str, **kwargs):
    """Call the backend and show a clear UI error instead of raising."""
    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{path}",
            timeout=REQUEST_TIMEOUT_SECONDS,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        st.error(
            f"Cannot reach the API at {API_BASE_URL}. Start the FastAPI server and try again. "
            f"({error})"
        )
        return None


def load_articles() -> list[dict]:
    articles = api_request("GET", "/articles")
    return articles if isinstance(articles, list) else []


def feed_table(articles: list[dict]) -> pd.DataFrame:
    rows = []
    for article in articles:
        analysis = article.get("analysis", article)
        rows.append({
            "headline": article.get("text", analysis.get("title", "")),
            "source": article.get("source", analysis.get("source", "unknown")),
            "event": analysis.get("event_type", "Other"),
            "sentiment_score": analysis.get("sentiment_score", 0.0),
            "impact_score": analysis.get("impact_score", 0),
        })
    return pd.DataFrame(rows)


def impact_color(value: float) -> str:
    if value > 7:
        return "background-color: #f8d7da; color: #842029"
    if value >= 4:
        return "background-color: #fff3cd; color: #664d03"
    return "background-color: #d1e7dd; color: #0f5132"


def show_stress_charts(result: dict) -> None:
    breakdown = pd.DataFrame(result.get("by_asset_class", []))
    if breakdown.empty:
        st.warning("The API response did not include an asset-class breakdown.")
        return

    labels = breakdown["asset_class"].str.replace("_", " ").str.title()
    values_in_crore = 10_000_000
    value_chart = go.Figure([
        go.Bar(name="Before", x=labels, y=breakdown["pre_value"] / values_in_crore),
        go.Bar(name="After", x=labels, y=breakdown["post_value"] / values_in_crore),
    ])
    value_chart.update_layout(
        barmode="group", title="Portfolio value by asset class", yaxis_title="INR crore"
    )
    st.plotly_chart(value_chart, use_container_width=True)

    loss_chart = go.Figure(go.Bar(
        x=labels,
        y=breakdown["loss"] / values_in_crore,
        marker_color="#c62828",
        name="Loss",
    ))
    loss_chart.update_layout(title="Loss by asset class", yaxis_title="INR crore")
    st.plotly_chart(loss_chart, use_container_width=True)


st.set_page_config(page_title="Financial Risk Engine", layout="wide")
st.title("Financial Risk Engine")

if "articles" not in st.session_state:
    st.session_state.articles = load_articles()
if "stress_result" not in st.session_state:
    st.session_state.stress_result = None

with st.sidebar:
    st.header("Controls")
    if st.button("Load sample news feed", use_container_width=True):
        articles = api_request("GET", "/ingest", params={"use_sample": "true"})
        if isinstance(articles, list):
            st.session_state.articles = articles
            st.session_state.stress_result = None
            st.success(f"Loaded {len(articles)} sample articles.")

    st.divider()
    custom_headline = st.text_input("Custom headline")
    if st.button("Analyze", use_container_width=True):
        if not custom_headline.strip():
            st.warning("Enter a headline to analyze.")
        else:
            analysis = api_request(
                "POST",
                "/analyze",
                json={"text": custom_headline.strip(), "source": "dashboard"},
            )
            if isinstance(analysis, dict):
                st.session_state.articles.insert(0, {
                    "text": custom_headline.strip(),
                    "source": "dashboard",
                    "timestamp": None,
                    "company": None,
                    "analysis": analysis,
                })
                st.success("Headline analyzed.")

st.header("1. Live risk feed")
feed = feed_table(st.session_state.articles)
if feed.empty:
    st.info("No articles loaded. Use the sample-news button to populate the feed.")
else:
    st.dataframe(
        feed.style.map(impact_color, subset=["impact_score"]),
        use_container_width=True,
        hide_index=True,
    )

st.header("2. Stress test")
if not st.session_state.articles:
    st.info("Load or analyze an article before running a stress test.")
else:
    options = list(range(len(st.session_state.articles)))
    selected_index = st.selectbox(
        "Article",
        options,
        format_func=lambda index: st.session_state.articles[index].get("text", "Untitled"),
    )
    selected = st.session_state.articles[selected_index]
    selected_analysis = selected.get("analysis", selected)
    selected_impact = float(selected_analysis.get("impact_score", 0))
    if selected_impact <= 7:
        st.caption("This article is below the automatic trigger threshold (impact score > 7); the demo will force the test.")

    if st.button("Run stress test"):
        result = api_request(
            "POST", "/stress-test", json={"signal_id": selected_index, "force": True}
        )
        if isinstance(result, dict):
            st.session_state.stress_result = result

if st.session_state.stress_result:
    stress_result = st.session_state.stress_result
    value_in_crore = 10_000_000
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("Portfolio value before", f"₹{stress_result['pre_value'] / value_in_crore:.2f} cr")
    metric_b.metric("Portfolio value after", f"₹{stress_result['post_value'] / value_in_crore:.2f} cr")
    metric_c.metric("Loss", f"{stress_result['loss_pct']:.2f}%")
    show_stress_charts(stress_result)

st.header("3. History")
history = api_request("GET", "/stress-tests")
if isinstance(history, list) and history:
    st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
elif history == []:
    st.info("No stress tests have been recorded yet.")
