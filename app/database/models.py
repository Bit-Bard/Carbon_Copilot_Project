from sqlalchemy import Column, Integer, Float, String
from .db import Base 

class DailyEmission(Base):
    __tablename__ = "daily_emissions"

    id = Column(Integer, primary_key=True , index = True)
    date = Column(String , unique=True)

    
    scope1 = Column(Float)
    scope2 = Column(Float)
    scope3 = Column(Float)
    total = Column(Float)