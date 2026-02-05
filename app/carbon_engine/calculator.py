# app/carbon_engine/calculator.py

from typing import Dict


# ----------------------
# emission factors
# ----------------------

ELECTRICITY_FACTOR = 0.82     # kg per kWh
DIESEL_FACTOR = 2.68          # kg per liter
LOGISTICS_FACTOR = 0.12       # kg per km
PURCHASE_FACTOR = 0.0005      # kg per ₹


# ----------------------
# core calculator
# ----------------------

def calculate_emissions(activity: Dict) -> Dict:

    electricity = activity["electricity_kwh"] * ELECTRICITY_FACTOR
    diesel = activity["diesel_liters"] * DIESEL_FACTOR
    logistics = activity["logistics_km"] * LOGISTICS_FACTOR
    purchase = activity["purchase_spend"] * PURCHASE_FACTOR

    scope1 = diesel                     # direct fuel
    scope2 = electricity                # purchased energy
    scope3 = logistics + purchase       # indirect

    total = scope1 + scope2 + scope3

    return {
        "scope1": round(scope1, 2),
        "scope2": round(scope2, 2),
        "scope3": round(scope3, 2),
        "total": round(total, 2)
    }
