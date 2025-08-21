import os
from pymongo import MongoClient

# ======= Load Environment Variables =======
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "HealthQ")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "bookings")

# ======= MongoDB Connection =======
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
appointments_collection = db[COLLECTION_NAME]

# ======= Extract Appointments for a Specific Doctor =======
def fetch_appointments_for_doctor(doctor_id: str):
    """
    Fetch upcoming/confirmed appointments for a doctor, map 'specialty' to 'Doctor_Type',
    and ensure only entries with 'Doctor_ID' exist to prevent errors.
    """
    appointments = list(appointments_collection.find(
        {
            "doctorId": doctor_id,
            "status": {"$in": ["upcoming", "confirmed"]},
            "Doctor_ID": {"$exists": True}  # filter out entries missing Doctor_ID
        },
        {
            "_id": 1,
            "doctorId": 1,
            "patientName": 1,
            "age": 1,
            "reason": 1,
            "Doctor_Age": 1,
            "specialty": 1,
            "date": 1,
            "timeSlotId": 1
        }
    ).sort("date", 1))

    # Map 'specialty' to 'Doctor_Type'
    for appt in appointments:
        appt['Doctor_Type'] = appt.pop('specialty')

    return appointments
