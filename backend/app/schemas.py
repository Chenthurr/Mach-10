from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TrafficEventCreate(BaseModel):
  junction_id: str
  vehicle_count: int
  pedestrian_count: int
  emergency_detected: bool
  timestamp: float

class SignalStateOut(BaseModel):
  junction_id: str
  phase: str
  duration_seconds: float
  updated_at: Optional[datetime]

  class Config:
    orm_mode = True
