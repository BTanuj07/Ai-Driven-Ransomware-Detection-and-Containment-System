"""
Check what's actually in MongoDB settings collection
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv('backend/.env')
sys.path.insert(0, 'backend')

from services.database import DatabaseService

db = DatabaseService()

print("=" * 60)
print("MONGODB SETTINGS COLLECTION")
print("=" * 60)

# Get settings document
settings_doc = db.settings.find_one({"type": "system"})

if settings_doc:
    print("\nSettings document found:")
    print("-" * 60)
    for key, value in settings_doc.items():
        if key != '_id':
            print(f"{key}: {value}")
    print("-" * 60)
    
    # Check specifically for email and phone
    print("\n📧 Email Address:", settings_doc.get('emailAddress', 'NOT FOUND'))
    print("📱 Phone Number:", settings_doc.get('phoneNumber', 'NOT FOUND'))
    
else:
    print("\n⚠️  No settings document found in MongoDB!")
    print("This is normal for first run. Settings will be created when you save in UI.")
