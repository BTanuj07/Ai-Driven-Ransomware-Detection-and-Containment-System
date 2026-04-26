from pymongo import MongoClient
import json

# Connect to MongoDB Atlas
client = MongoClient("mongodb://tanuj:tanuj1234@ac-utvb68u-shard-00-00.ushqevx.mongodb.net:27017,ac-utvb68u-shard-00-01.ushqevx.mongodb.net:27017,ac-utvb68u-shard-00-02.ushqevx.mongodb.net:27017/?ssl=true&replicaSet=atlas-a4hgsp-shard-0&authSource=admin&appName=Major")

db = client["arcs_db"]
alerts = db.alerts

# Get one alert
alert = alerts.find_one()

if alert:
    print("Found alert:")
    print(f"ID: {alert['_id']}")
    print(f"Hostname: {alert.get('hostname')}")
    print(f"Risk Level: {alert.get('risk_level')}")
    print(f"Risk Score: {alert.get('risk_score')}, Type: {type(alert.get('risk_score'))}")
    print(f"\nFull alert:")
    for key, value in alert.items():
        print(f"  {key}: {value} (type: {type(value).__name__})")
else:
    print("No alerts found")

client.close()
