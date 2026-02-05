import os
from dotenv import load_dotenv
from google import genai

from app.database.db import SessionLocal
from app.database.models import DailyEmission
from app.rag.retriever import get_retriever


# -------------------------
# setup
# -------------------------

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3-flash-preview"


# -------------------------
# fetch latest metrics
# -------------------------

def get_latest_metrics():
    db = SessionLocal()

    rows = (
        db.query(DailyEmission)
        .order_by(DailyEmission.date.desc())
        .limit(2)
        .all()
    )

    db.close()

    today = rows[0]
    yesterday = rows[1] if len(rows) > 1 else None

    return today, yesterday


# -------------------------
# build context text
# -------------------------

def build_metrics_text(today, yesterday):

    change = 0
    if yesterday:
        change = round(
            (yesterday.total - today.total) / yesterday.total * 100, 2
        )

    return f"""
Today's Emissions:
Scope 1 (fuel): {today.scope1} kg
Scope 2 (electricity): {today.scope2} kg
Scope 3 (indirect): {today.scope3} kg
Total: {today.total} kg

Change from yesterday: {change} %
"""


# -------------------------
# main advisor
# -------------------------

def generate_advice():

    today, yesterday = get_latest_metrics()

    # ---------- numbers ----------
    metrics_text = build_metrics_text(today, yesterday)

    # ---------- RAG retrieval ----------
    retriever = get_retriever()

    docs = retriever.invoke(
        "How can this company reduce its carbon emissions effectively?"
    )

    company_context = "\n\n".join(d.page_content for d in docs)

    # ---------- prompt ----------
    prompt = f"""
You are a sustainability advisor.

Use the company context and emission data below.

Rules:
- Maximum 6 bullet points
- Each bullet ≤ 15 words
- No explanations
- No tables
- No introductions or conclusions

Company Context:
{company_context}

Emission Data:
{metrics_text}

Generate:
- Key emission causes
- Actionable reduction steps
"""


    # ---------- Gemini call ----------
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text

