# api/db.py
from pymongo import MongoClient
import os

MONGO_USER = os.environ["MONGO_USER"]
MONGO_PASS = os.environ["MONGO_PASS"]

# MongoDB connection from environment variables
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.4ayta.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "HealthQ"
COLLECTION_NAME = "bookings"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
appointments_collection = db[COLLECTION_NAME]

def fetch_appointments_for_doctor(doctor_id: str):
    """
    Fetch upcoming appointments for a given doctor.
    Handles both ISODate and string-based Appointment_Date.
    """

    today = datetime.now()

    # Get all appointments for the doctor
    appointments = list(appointments_collection.find({"Doctor_ID": doctor_id}))

    # Convert Appointment_Date to datetime if needed
    for appt in appointments:
        date_val = appt.get("Appointment_Date")
        if isinstance(date_val, str):
            try:
                appt["Appointment_Date"] = parser.parse(date_val)
            except Exception:
                continue  # skip if invalid format

    # Keep only upcoming
    upcoming = [a for a in appointments if a.get("Appointment_Date") and a["Appointment_Date"] >= today]

    # ✅ Map specialty → Doctor_Type
    for appt in upcoming:
        if "Specialty" in appt:
            appt["Doctor_Type"] = appt.pop("Specialty")

    return upcoming
