import requests
from datetime import datetime

from app.carbon_engine.calculator import calculate_emissions
from app.database.db import SessionLocal, engine
from app.database.models import Base, DailyEmission


# ------------------------------------------------
# create tables (safe to run multiple times)
# ------------------------------------------------
Base.metadata.create_all(bind=engine)


MCP_URL = "http://127.0.0.1:8000/today"


# ------------------------------------------------
# main ingestion job
# ------------------------------------------------
def run_daily_job():

    # ---------- fetch activity from MCP ----------
    response = requests.get(MCP_URL)

    if response.status_code != 200:
        raise Exception("MCP server not reachable")

    activity = response.json()

    # ---------- calculate emissions ----------
    result = calculate_emissions(activity)

    db = SessionLocal()

    try:
        today_date = activity["date"]

        # ---------- UPSERT logic ----------
        existing = (
            db.query(DailyEmission)
            .filter(DailyEmission.date == today_date)
            .first()
        )

        if existing:
            # update existing row
            existing.scope1 = result["scope1"]
            existing.scope2 = result["scope2"]
            existing.scope3 = result["scope3"]
            existing.total = result["total"]

            action = "Updated"

        else:
            # insert new row
            new_record = DailyEmission(
                date=today_date,
                scope1=result["scope1"],
                scope2=result["scope2"],
                scope3=result["scope3"],
                total=result["total"]
            )

            db.add(new_record)

            action = "Inserted"

        db.commit()

        print(f"{action} emissions for {today_date}: {result}")

    finally:
        db.close()
