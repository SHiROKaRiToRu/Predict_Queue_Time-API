import requests

# Replace with Railway URL if live
url = "https://web-production-e709.up.railway.app/predict_queue_time"

# Query parameter format
params = {"doctor_id": "D00001"}

response = requests.post(url, params=params)

print(response.json())
