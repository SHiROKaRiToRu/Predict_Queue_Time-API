import requests

# Replace with Railway URL if live
url = "http://127.0.0.1:8001/predict_queue_time"

# Query parameter format
params = {"doctor_id": "D00001"}

response = requests.post(url, params=params)

print(response.json())
