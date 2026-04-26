import requests

# Test simple endpoint
response = requests.get("http://localhost:8000/api/health")
print(f"Health: {response.status_code} - {response.json()}")

# Test stats
response = requests.get("http://localhost:8000/api/stats")
print(f"Stats: {response.status_code} - {response.json()}")

# Test alerts
try:
    response = requests.get("http://localhost:8000/api/alerts")
    print(f"Alerts: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Count: {data['count']}")
    else:
        print(f"  Error: {response.text}")
except Exception as e:
    print(f"  Exception: {e}")
