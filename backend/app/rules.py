from .models import SignalState, TrafficEvent
from sqlalchemy.orm import Session

# VERY SIMPLE RULES:
# 1. If emergency_detected => give "EMERGENCY_GREEN" for 30s
# 2. Else if pedestrian_count high => "PED_GREEN" for 20s
# 3. Else if vehicle_count high => "VEHICLE_GREEN" for 30s
# You would later map these abstract phases to actual signal controller commands.

def apply_rules(db: Session, event: TrafficEvent) -> SignalState:
  phase = "IDLE"
  duration = 10.0

  if event.emergency_detected:
    phase = "EMERGENCY_GREEN"
    duration = 30.0
  elif event.pedestrian_count >= 10:
    phase = "PED_GREEN"
    duration = 20.0
  elif event.vehicle_count >= 15:
    phase = "VEHICLE_GREEN"
    duration = 30.0
  else:
    phase = "BALANCED"
    duration = 15.0

  # Upsert simple SignalState
  state = (
    db.query(SignalState)
    .filter(SignalState.junction_id == event.junction_id)
    .first()
  )

  if not state:
    state = SignalState(
      junction_id=event.junction_id,
      phase=phase,
      duration_seconds=duration,
    )
    db.add(state)
  else:
    state.phase = phase
    state.duration_seconds = duration

  db.commit()
  db.refresh(state)
  return state
