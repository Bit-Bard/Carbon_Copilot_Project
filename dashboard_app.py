import streamlit as st
import pandas as pd
import plotly.express as px

from app.database.db import SessionLocal
from app.database.models import DailyEmission
from app.llm_agent.advisor import generate_advice
from app.ingestion.daily_job import run_daily_job


# ------------------------------------------------
# Page config
# ------------------------------------------------

st.set_page_config(
    page_title="Carbon Copilot",
    layout="wide"
)

st.title("🌱 Carbon Intelligence Dashboard")
st.caption("Track emissions • Identify waste • Get AI recommendations")


# ------------------------------------------------
# Load data
# ------------------------------------------------

def load_data():
    db = SessionLocal()
    rows = db.query(DailyEmission).order_by(DailyEmission.date).all()
    db.close()

    data = [
        {
            "date": r.date,
            "fuel": r.scope1,
            "electricity": r.scope2,
            "indirect": r.scope3,
            "total": r.total
        }
        for r in rows
    ]

    return pd.DataFrame(data)


# ------------------------------------------------
# Sidebar
# ------------------------------------------------

st.sidebar.header("Controls")

if st.sidebar.button("Run Today's Calculation"):
    run_daily_job()
    st.sidebar.success("Updated today's emissions")


# ------------------------------------------------
# Main
# ------------------------------------------------

df = load_data()

if df.empty:
    st.warning("No data yet. Run today's calculation first.")
    st.stop()

today = df.iloc[-1]

yesterday_total = df.iloc[-2]["total"] if len(df) > 1 else today["total"]
change = round((yesterday_total - today["total"]) / yesterday_total * 100, 2)


# ------------------------------------------------
# KPI cards (business-friendly)
# ------------------------------------------------

st.subheader("📊 Today's Carbon Footprint")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Emissions (kg CO₂)",
    round(today["total"], 2)
)

col2.metric(
    "🚚 Fuel Usage Emissions",
    round(today["fuel"], 2),
    help="Direct emissions from diesel/petrol vehicles & generators"
)

col3.metric(
    "⚡ Electricity Emissions",
    round(today["electricity"], 2),
    help="Emissions from grid electricity consumption"
)

col4.metric(
    "📦 Supply Chain Emissions",
    round(today["indirect"], 2),
    help="Logistics, vendors, and indirect purchases"
)

st.metric("Change vs Yesterday", f"{change} %")


# ------------------------------------------------
# Charts
# ------------------------------------------------

st.divider()

colA, colB = st.columns(2)

# Trend line
with colA:
    st.subheader("📈 Emission Trend Over Time")

    fig = px.line(
        df,
        x="date",
        y="total",
        markers=True,
        labels={"total": "kg CO₂", "date": "Date"}
    )

    st.plotly_chart(fig, use_container_width=True)


# Breakdown pie chart
with colB:
    st.subheader("📊 Today's Emission Breakdown")

    pie_df = pd.DataFrame({
        "Category": ["Fuel", "Electricity", "Supply Chain"],
        "Value": [today["fuel"], today["electricity"], today["indirect"]]
    })

    fig2 = px.pie(pie_df, values="Value", names="Category")

    st.plotly_chart(fig2, use_container_width=True)


# ------------------------------------------------
# AI Advisor
# ------------------------------------------------

st.divider()
st.subheader("🤖 AI Sustainability Advisor")

if st.button("Generate AI Suggestions"):
    with st.spinner("Analyzing emissions..."):
        advice = generate_advice()
        st.success(advice)
