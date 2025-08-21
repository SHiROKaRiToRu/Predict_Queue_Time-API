# api/db.py
from pymongo import MongoClient
import os
from datetime import datetime
from dateutil import parser

MONGO_USER = os.environ["MONGO_USER"]
MONGO_PASS = os.environ["MONGO_PASS"]

MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.4ayta.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

DB_NAME = "HealthQ"
COLLECTION_NAME = "bookings"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
appointments_collection = db[COLLECTION_NAME]


def fetch_appointments_for_doctor(doctor_id: str):
    """
    Fetch upcoming appointments for a specific doctor.
    Converts string dates into datetime and filters past ones.
    Maps specialty -> Doctor_Type.
    """

    query = {
        "doctorId": doctor_id,
        "status": {"$in": ["upcoming", "confirmed"]},
        "Doctor_ID": {"$exists": True}  # Only entries with Doctor_ID
    }
    projection = {
        "_id": 1,
        "doctorId": 1,
        "Doctor_ID": 1,
        "patientName": 1,
        "age": 1,
        "reason": 1,
        "Doctor_Age": 1,
        "specialty": 1,
        "date": 1,
        "timeSlotId": 1
    }

    raw_appointments = list(appointments_collection.find(query, projection))

    upcoming = []
    now = datetime.now()

    for appt in raw_appointments:
        date_val = appt.get("date")

        # Parse string dates safely
        if isinstance(date_val, str):
            try:
                date_val = parser.parse(date_val)
            except Exception:
                continue

        if date_val and date_val >= now:
            appt["date"] = date_val
            if "specialty" in appt:
                appt["Doctor_Type"] = appt.pop("specialty")
            upcoming.append(appt)

    # Sort by date ascending
    upcoming.sort(key=lambda x: x["date"])

    return upcoming
