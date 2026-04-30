import json
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

REPORTS_DIR = Path(__file__).parent.parent / "reports"

st.set_page_config(page_title="Auto Blog Generator", page_icon="✍️", layout="wide")
st.title("Auto Blog Generator — Dashboard")


def load_reports() -> list[tuple[str, dict]]:
    files = sorted(REPORTS_DIR.glob("*.json"), reverse=True)
    result = []
    for f in files:
        try:
            result.append((f.stem, json.loads(f.read_text(encoding="utf-8"))))
        except Exception:
            continue
    return result


reports = load_reports()

if not reports:
    st.info("No reports found yet. Run `python main.py` to generate the first report.")
    st.stop()

# Sidebar — date selector
dates = [r[0] for r in reports]
selected_date = st.sidebar.selectbox("Report date", dates, index=0)
report = next(data for date_str, data in reports if date_str == selected_date)

# Top metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Topics Scanned", len(report.get("topics_found", [])))
col2.metric("Blogs Published", len(report.get("blogs_published", [])))
col3.metric("Errors", len(report.get("errors", [])))

published = report.get("blogs_published", [])
if published:
    avg_quality = sum(b.get("quality_score", 0) for b in published) / len(published)
    col4.metric("Avg Quality Score", f"{avg_quality:.1f}/10")

st.divider()

# Topics found
with st.expander(f"Topics scanned ({len(report.get('topics_found', []))})", expanded=False):
    for t in report.get("topics_found", []):
        st.markdown(f"- {t}")

# Published blogs
st.subheader("Published Blogs")
if published:
    for blog in published:
        url = blog.get("url", "")
        title = blog.get("title", "Untitled")
        quality = blog.get("quality_score", "—")
        seo = blog.get("seo_score", "—")
        flagged = blog.get("needs_review", False)

        label = f"[{title}]({url})" if url else title
        flag = " ⚠️ needs review" if flagged else ""
        st.markdown(
            f"**{label}**{flag}  \nQuality: `{quality}/10` · SEO: `{seo}/10`"
        )
else:
    st.info("No blogs published in this report.")

# Errors
if report.get("errors"):
    st.subheader("Errors")
    for err in report["errors"]:
        with st.expander(err[:80], expanded=False):
            st.code(err)

# Historical trend
if len(reports) > 1:
    st.divider()
    st.subheader("Historical — Blogs Published per Day")
    chart_data = {
        r[0]: len(r[1].get("blogs_published", [])) for r in reports
    }
    # Streamlit bar chart expects a dict or DataFrame
    import pandas as pd
    df = pd.DataFrame.from_dict(
        {"date": list(chart_data.keys()), "blogs": list(chart_data.values())}
    ).set_index("date")
    st.bar_chart(df)
