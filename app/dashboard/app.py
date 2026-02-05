import streamlit as st
import pandas as pd
import plotly.express as px
from app.database.db import SessionLocal
from app.database.models import DailyEmission
from app.llm_agent.advisor import generate_advice
from app.ingestion.daily_job import run_daily_job

import sys
import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


# -------------------------
# page config
# -------------------------

st.set_page_config(
    page_title="Carbon Copilot",
    layout="wide"
)

st.title("🌱 Enterprise Carbon Intelligence Copilot")


# -------------------------
# fetch DB data
# -------------------------

def load_data():
    db = SessionLocal()
    rows = db.query(DailyEmission).order_by(DailyEmission.date).all()
    db.close()

    data = [
        {
            "date": r.date,
            "scope1": r.scope1,
            "scope2": r.scope2,
            "scope3": r.scope3,
            "total": r.total
        }
        for r in rows
    ]

    return pd.DataFrame(data)


# -------------------------
# Sidebar actions
# -------------------------

st.sidebar.header("Controls")

if st.sidebar.button("Run Today's Calculation"):
    run_daily_job()
    st.sidebar.success("Today's emissions calculated!")


# -------------------------
# Load data
# -------------------------

df = load_data()

if df.empty:
    st.warning("No emission data yet. Click 'Run Today's Calculation'")
    st.stop()


# -------------------------
# KPIs
# -------------------------

today = df.iloc[-1]

yesterday_total = df.iloc[-2]["total"] if len(df) > 1 else today["total"]
change = round((yesterday_total - today["total"]) / yesterday_total * 100, 2)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total CO₂ (kg)", today["total"])
col2.metric("Scope 1", today["scope1"])
col3.metric("Scope 2", today["scope2"])
col4.metric("Change vs Yesterday", f"{change} %")


# -------------------------
# charts
# -------------------------

st.subheader("Emission Trend")

fig = px.line(df, x="date", y="total", markers=True)
st.plotly_chart(fig, use_container_width=True)


st.subheader("Scope Breakdown")

scope_df = pd.DataFrame({
    "Scope": ["Scope 1", "Scope 2", "Scope 3"],
    "Value": [today["scope1"], today["scope2"], today["scope3"]]
})

fig2 = px.bar(scope_df, x="Scope", y="Value")
st.plotly_chart(fig2, use_container_width=True)


# -------------------------
# Gemini Advisor
# -------------------------

st.subheader("🤖 Daily Sustainability Advisor")

if st.button("Generate AI Advice"):
    with st.spinner("Thinking..."):
        advice = generate_advice()
        st.success(advice)
