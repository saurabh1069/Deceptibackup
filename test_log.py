import requests

# The decoy data to send
test_data = {
    "type": "Port Scan",
    "source": "192.168.1.99",
    "message": "Multiple SYN packets from unknown host",
    "timestamp": "2025-07-04 14:25:00"
}

# URL of your Flask endpoint
url = "http://localhost:5000/log"

# Send the POST request
try:
    response = requests.post(url, json=test_data)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Failed to connect to Flask server:", e)
