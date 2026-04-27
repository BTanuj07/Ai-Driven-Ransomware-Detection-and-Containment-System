"""
Clear ALL old endpoint data from database
This will give you a fresh start
"""
import sys
sys.path.insert(0, 'backend')
from services.database import DatabaseService

print("=" * 70)
print("CLEAR ALL ENDPOINT DATA")
print("=" * 70)

db = DatabaseService()

print("\n⚠️  WARNING: This will delete ALL data from the database!")
print("   - All alerts")
print("   - All logs")
print("   - All risk scores")
print("   - All system statuses")
print("   - All containment actions")
print("\n   This gives you a completely fresh start.")

confirm = input("\nAre you sure? Type 'yes' to confirm: ").strip().lower()

if confirm != 'yes':
    print("\n❌ Cancelled. No data was deleted.")
    exit(0)

print("\n🧹 Clearing all collections...")

# Clear all collections
collections = {
    'alerts': db.db['alerts'],
    'logs': db.db['logs'],
    'risk_scores': db.db['risk_scores'],
    'system_status': db.db['system_status'],
    'containment_actions': db.db['containment_actions']
}

for name, collection in collections.items():
    count = collection.count_documents({})
    if count > 0:
        result = collection.delete_many({})
        print(f"  ✅ {name}: Deleted {result.deleted_count} documents")
    else:
        print(f"  ℹ️  {name}: Already empty")

print("\n" + "=" * 70)
print("✅ ALL DATA CLEARED!")
print("=" * 70)

print("\nDatabase is now completely clean.")
print("\nNext steps:")
print("  1. Start centralized agent: python centralized_agent.py")
print("  2. Wait 1-2 minutes for fresh data")
print("  3. Refresh dashboard (Ctrl+Shift+R)")
print("  4. You should see only current endpoint data")
