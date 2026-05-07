"""
Manually save settings to MongoDB to test
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv('backend/.env')
sys.path.insert(0, 'backend')

from services.database import DatabaseService
from services.settings_manager import settings_manager

print("=" * 60)
print("SAVING SETTINGS TO MONGODB")
print("=" * 60)

# Create database service
db = DatabaseService()

# Settings to save
settings_to_save = {
    'anomalyThreshold': -0.5,
    'highRiskThreshold': 0.8,
    'mediumRiskThreshold': 0.6,
    'lowRiskThreshold': 0.4,
    'falsePositiveSensitivity': 0.65,
    'modelConfidence': 0.85,
    'autoIsolate': True,
    'autoKillProcess': True,
    'autoDisableUser': False,
    'requireApproval': True,
    'emailAlerts': True,
    'smsAlerts': True,
    'criticalEscalation': True,
    'emailAddress': 'tanuj077777@gmail.com',  # Your email
    'phoneNumber': '+919353938326'  # Your phone
}

print("\n📝 Saving settings:")
print(f"   📧 Email: {settings_to_save['emailAddress']}")
print(f"   📱 Phone: {settings_to_save['phoneNumber']}")

# Save to database
success = db.update_settings(settings_to_save)

if success:
    print("\n✅ Settings saved to MongoDB successfully!")
    
    # Update settings manager
    settings_manager.set_database(db)
    settings_manager.reload()
    
    # Verify
    email = settings_manager.get('emailAddress')
    phone = settings_manager.get('phoneNumber')
    
    print(f"\n✓ Verified in settings manager:")
    print(f"   📧 Email: {email}")
    print(f"   📱 Phone: {phone}")
    
    if email == 'tanuj077777@gmail.com' and phone == '+919353938326':
        print("\n🎉 SUCCESS! Settings are now configured correctly.")
        print("\nNext steps:")
        print("1. Restart backend: python backend/main.py")
        print("2. Run test: python test_dynamic_alerts.py")
    else:
        print("\n⚠️  Settings saved but values don't match")
else:
    print("\n❌ Failed to save settings to MongoDB")

print("\n" + "=" * 60)
