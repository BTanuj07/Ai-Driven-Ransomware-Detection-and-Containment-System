from pymongo import MongoClient
import json
import sys
sys.path.insert(0, 'backend')

from services.database import DatabaseService

# Create database service
db_service = DatabaseService()

# Get alerts
alerts = db_service.get_recent_alerts(10)

print(f"Got {len(alerts)} alerts")

if alerts:
    print("\nFirst alert:")
    alert = alerts[0]
    for key, value in alert.items():
        print(f"  {key}: {value} (type: {type(value).__name__})")
    
    print("\nTrying to JSON serialize...")
    try:
        json_str = json.dumps(alert)
        print("✅ Serialization successful!")
        print(f"JSON: {json_str[:200]}...")
    except Exception as e:
        print(f"❌ Serialization failed: {e}")
        print(f"Error type: {type(e).__name__}")
