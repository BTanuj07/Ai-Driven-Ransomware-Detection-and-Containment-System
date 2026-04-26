import requests

try:
    response = requests.get("http://localhost:8000/api/alerts")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nAlerts count: {data['count']}")
        if data['alerts']:
            print(f"First alert: {data['alerts'][0]}")
except Exception as e:
    print(f"Error: {e}")
