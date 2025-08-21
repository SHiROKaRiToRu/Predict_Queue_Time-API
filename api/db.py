# api/db.py
from pymongo import MongoClient
import os

# MongoDB connection from environment variables
MONGO_URI = f"mongodb+srv://{os.environ['Traventure']}:{os.environ['W2qolroXtlw6qsPS']}@cluster0.4ayta.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "HealthQ"
COLLECTION_NAME = "bookings"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
appointments_collection = db[COLLECTION_NAME]

def fetch_appointments_for_doctor(doctor_id: str):
    """
    Fetch upcoming appointments for a specific doctor.
    Only considers entries containing Doctor_ID to avoid errors.
    Returns sorted list by date.
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

    appointments = list(appointments_collection.find(query, projection).sort("date", 1))

    # Map specialty to Doctor_Type if needed
    for appt in appointments:
        if "specialty" in appt:
            appt["Doctor_Type"] = appt["specialty"]

    return appointments
