import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import redis

from .db import Base, engine, get_db
from . import models, schemas, rules

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MACH-10 Backend", version="0.1.0")

origins = ["*"]  # tighten later
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

@app.get("/health")
def health():
  return {"status": "ok"}

@app.post("/events/traffic", response_model=schemas.SignalStateOut)
def ingest_traffic_event(
  event_in: schemas.TrafficEventCreate,
  db: Session = Depends(get_db)
):
  # Save event
  event = models.TrafficEvent(
    junction_id=event_in.junction_id,
    vehicle_count=event_in.vehicle_count,
    pedestrian_count=event_in.pedestrian_count,
    emergency_detected=event_in.emergency_detected,
  )
  db.add(event)
  db.commit()
  db.refresh(event)

  # Apply rules
  state = rules.apply_rules(db, event)

  # Publish to Redis (for any listener / signal controller adapter)
  redis_client.publish(
    f"junction:{state.junction_id}",
    f"{state.phase}:{state.duration_seconds}",
  )

  return state

@app.get("/junctions/{junction_id}/state", response_model=schemas.SignalStateOut)
def get_junction_state(junction_id: str, db: Session = Depends(get_db)):
  state = (
    db.query(models.SignalState)
    .filter(models.SignalState.junction_id == junction_id)
    .first()
  )
  if not state:
    # return default state
    state = models.SignalState(
      junction_id=junction_id,
      phase="UNKNOWN",
      duration_seconds=0,
    )
    db.add(state)
    db.commit()
    db.refresh(state)
  return state
