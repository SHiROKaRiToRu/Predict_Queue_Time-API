# api/api.py
from fastapi import FastAPI, HTTPException, Query
from .db import fetch_appointments_for_doctor
from joblib import load
import os
import numpy as np

app = FastAPI()

# Load model and preprocessing objects
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "supervised_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "..", "models", "scaler.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "..", "models", "encoders.pkl")

model = load(MODEL_PATH)
scaler = load(SCALER_PATH)
encoders = load(ENCODERS_PATH)

feature_cols = ["Doctor_ID", "Doctor_Age", "Doctor_Type", "Reason"]

@app.post("/predict_queue_time")
def predict_queue_time(doctor_id: str = Query(..., description="Doctor_ID to predict queue for")):
    try:
        appointments = fetch_appointments_for_doctor(doctor_id)
        if not appointments:
            raise HTTPException(status_code=404, detail="No upcoming appointments found for this doctor")

        queue_predictions = []
        cumulative_time = 0

        for appt in appointments:
            # Prepare features
            features = []
            for col in feature_cols:
                if col in ["Doctor_ID", "Doctor_Type", "Reason"]:
                    le = encoders[col]
                    val = appt.get(col, None)
                    if val not in le.classes_:
                        val = le.classes_[0]  # fallback to first category if unknown
                    features.append(le.transform([val])[0])
                else:
                    features.append(appt.get(col, 0))

            # Scale features
            features_scaled = scaler.transform([features])

            # Predict serve time
            pred_time = model.predict(features_scaled)[0]
            pred_time = max(0, pred_time)  # ensure non-negative

            cumulative_time += pred_time

            queue_predictions.append({
                "booking_id": str(appt["_id"]),
                "patient_name": appt.get("patientName", ""),
                "predicted_serve_time_seconds": float(pred_time),
                "cumulative_wait_time_seconds": float(cumulative_time)
            })

        return {"doctor_id": doctor_id, "queue_predictions": queue_predictions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
