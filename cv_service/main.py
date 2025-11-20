import os
import time
import cv2
import requests
from ultralytics import YOLO

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CAMERA_STREAM_URL = os.getenv("CAMERA_STREAM_URL", 0)  # 0 for webcam

# Load YOLOv8 model (can be yolov8n.pt, yolov8s.pt, or custom)
model = YOLO("yolov8n.pt")

# Class names you care about (COCO ids for cars, buses, trucks, person, bicycle, etc.)
INTERESTING_CLASSES = {
    "car", "bus", "truck", "person", "bicycle", "motorbike", "ambulance"
}

def send_event_to_backend(event: dict):
  try:
    requests.post(f"{BACKEND_URL}/events/traffic", json=event, timeout=1)
  except Exception as e:
    print("Failed to send event:", e)

def main():
  cap = cv2.VideoCapture(CAMERA_STREAM_URL)

  if not cap.isOpened():
    print("Cannot open camera stream")
    return

  while True:
    ret, frame = cap.read()
    if not ret:
      print("Frame grab failed, retrying...")
      time.sleep(1)
      continue

    # Run YOLO inference
    results = model(frame, verbose=False)

    vehicle_count = 0
    pedestrian_count = 0
    emergency_detected = False

    for r in results:
      boxes = r.boxes
      for box in boxes:
        cls_id = int(box.cls)
        cls_name = model.names[cls_id]

        if cls_name not in INTERESTING_CLASSES:
          continue

        if cls_name in ["person"]:
          pedestrian_count += 1
        elif cls_name in ["car", "bus", "truck", "bicycle", "motorbike"]:
          vehicle_count += 1

        # crude emergency check: if custom model label "ambulance"
        if cls_name == "ambulance":
          emergency_detected = True

    event = {
      "junction_id": "Uppilipalayam_Junction",
      "vehicle_count": vehicle_count,
      "pedestrian_count": pedestrian_count,
      "emergency_detected": emergency_detected,
      "timestamp": time.time()
    }

    print("Event:", event)
    send_event_to_backend(event)

    # Simple frame rate control
    time.sleep(0.5)

if __name__ == "__main__":
  main()
