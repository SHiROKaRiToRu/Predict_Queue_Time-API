from fastapi import FastAPI, HTTPException, Query
import joblib
import os
from .db import fetch_appointments_for_doctor
import numpy as np

app = FastAPI(title="Queue Time Prediction API")

# ======= Paths for Model & Preprocessing =======
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "supervised_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "..", "models", "scaler.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "..", "models", "encoders.pkl")

# ======= Load Model & Preprocessing Objects =======
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
encoders = joblib.load(ENCODERS_PATH)
feature_cols = ["Doctor_ID", "Doctor_Age", "Doctor_Type", "reason"]

# ======= Predict Queue Time =======
@app.post("/predict_queue_time")
def predict_queue_time(doctor_id: str = Query(..., description="Doctor_ID for queue")):
    # Fetch doctor's appointments
    appointments = fetch_appointments_for_doctor(doctor_id)
    if not appointments:
        raise HTTPException(status_code=404, detail="No upcoming appointments found for this doctor.")

    results = []
    cumulative_time = 0  # To calculate queue-aware serve time

    for appt in appointments:
        # Encode & scale features
        features = []
        for col in feature_cols:
            if col in ["Doctor_ID", "Doctor_Type", "reason"]:
                le = encoders[col]
                if appt[col] not in le.classes_:
                    raise HTTPException(status_code=400, detail=f"Unknown category '{appt[col]}' for column '{col}'")
                features.append(le.transform([appt[col]])[0])
            else:
                features.append(appt[col])

        # Scale features
        features_scaled = scaler.transform([features])

        # Predict serve time
        predicted_time = model.predict(features_scaled)[0]

        # Queue-aware serve time
        cumulative_time += predicted_time

        # Round to nearest minute
        predicted_minutes = int(np.round(cumulative_time / 60))

        results.append({
            "booking_id": str(appt["_id"]),
            "patientName": appt["patientName"],
            "predicted_queue_time_minutes": predicted_minutes
        })

    return {"doctor_id": doctor_id, "queue_predictions": results}
