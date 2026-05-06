"""
Test Reports API Endpoints
"""

import requests

BASE_URL = "http://localhost:8000"

def test_reports_without_auth():
    """Test reports endpoints without authentication"""
    print("Testing Reports API without authentication...")
    print("=" * 60)
    
    endpoints = [
        "/api/reports/summary",
        "/api/reports/trend?days=7",
        "/api/reports/attack-types",
        "/api/reports/incidents?limit=10"
    ]
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\nTesting: {endpoint}")
        try:
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code == 401:
                print(f"  ❌ Requires authentication (expected)")
                print(f"  Response: {response.json()}")
            elif response.status_code == 200:
                print(f"  ✅ Success (unexpected - should require auth)")
                data = response.json()
                print(f"  Data keys: {list(data.keys())}")
            else:
                print(f"  ⚠️  Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_reports_data_availability():
    """Check if there's data in MongoDB for reports"""
    print("\n\nChecking MongoDB data availability...")
    print("=" * 60)
    
    try:
        # Test alerts endpoint (should have data)
        response = requests.get(f"{BASE_URL}/api/alerts?limit=5", timeout=5)
        print(f"\nAlerts endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            alert_count = len(data.get('alerts', []))
            print(f"  ✅ Found {alert_count} alerts")
            if alert_count > 0:
                print(f"  Sample alert: {data['alerts'][0].get('hostname')} - {data['alerts'][0].get('risk_level')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_reports_without_auth()
    test_reports_data_availability()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("- Reports endpoints require authentication (401)")
    print("- Frontend needs to pass valid JWT token")
    print("- Check browser console for actual error messages")
    print("- Verify Supabase session is valid")
