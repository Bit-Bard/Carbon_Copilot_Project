# app/mcp_server/mock_api.py

from fastapi import FastAPI
from datetime import datetime
import random

app = FastAPI(title="Carbon MCP Mock Server")


# ---------- realistic synthetic generator ----------
def generate_activity():

    weekday = datetime.today().weekday()

    # higher usage on weekdays
    multiplier = 1.2 if weekday < 5 else 0.7

    electricity = int(random.gauss(1500, 100) * multiplier)
    diesel = int(random.gauss(280, 20) * multiplier)
    logistics = int(random.gauss(1000, 80) * multiplier)
    purchases = int(random.gauss(50000, 4000) * multiplier)

    return {
        "date": str(datetime.today().date()),
        "electricity_kwh": max(electricity, 0),
        "diesel_liters": max(diesel, 0),
        "logistics_km": max(logistics, 0),
        "purchase_spend": max(purchases, 0)
    }


# ---------- routes ----------

@app.get("/")
def health():
    return {"status": "MCP running"}


@app.get("/today")
def today_data():
    return generate_activity()
