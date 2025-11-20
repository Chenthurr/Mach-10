from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.sql import func
from .db import Base

class TrafficEvent(Base):
  __tablename__ = "traffic_events"

  id = Column(Integer, primary_key=True, index=True)
  junction_id = Column(String, index=True)
  vehicle_count = Column(Integer)
  pedestrian_count = Column(Integer)
  emergency_detected = Column(Boolean, default=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())

class SignalState(Base):
  __tablename__ = "signal_states"

  id = Column(Integer, primary_key=True, index=True)
  junction_id = Column(String, index=True)
  phase = Column(String)  # e.g. "NS_GREEN", "EW_GREEN", "PED_GREEN"
  duration_seconds = Column(Float)
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
