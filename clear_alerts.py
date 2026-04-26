from pymongo import MongoClient

# Connect to MongoDB Atlas
client = MongoClient("mongodb://tanuj:tanuj1234@ac-utvb68u-shard-00-00.ushqevx.mongodb.net:27017,ac-utvb68u-shard-00-01.ushqevx.mongodb.net:27017,ac-utvb68u-shard-00-02.ushqevx.mongodb.net:27017/?ssl=true&replicaSet=atlas-a4hgsp-shard-0&authSource=admin&appName=Major")

db = client["arcs_db"]

# Clear all collections
print("Clearing all collections...")
db.alerts.delete_many({})
db.logs.delete_many({})
db.risk_scores.delete_many({})
db.containment_actions.delete_many({})
db.system_status.delete_many({})

print("✅ All collections cleared!")
print("\nNow restart the backend and send new test data.")

client.close()
