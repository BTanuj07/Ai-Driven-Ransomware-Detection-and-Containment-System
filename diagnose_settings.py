"""
Diagnose Settings Module - Check if settings are saved and loaded correctly
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Add backend to path
sys.path.insert(0, 'backend')

from services.database import DatabaseService
from services.settings_manager import SettingsManager

def diagnose_settings():
    print("=" * 60)
    print("SETTINGS DIAGNOSIS")
    print("=" * 60)
    
    # 1. Check MongoDB connection
    print("\n1. Checking MongoDB connection...")
    db = DatabaseService()
    if db.db is not None:
        print("   ✅ MongoDB connected")
    else:
        print("   ❌ MongoDB connection failed")
        return
    
    # 2. Check settings in MongoDB
    print("\n2. Checking settings in MongoDB...")
    settings = db.get_settings()
    print(f"   Settings found: {len(settings)} keys")
    
    if 'emailAddress' in settings:
        print(f"   📧 Email Address: {settings['emailAddress']}")
    else:
        print("   ⚠️  No emailAddress in settings")
    
    if 'phoneNumber' in settings:
        print(f"   📱 Phone Number: {settings['phoneNumber']}")
    else:
        print("   ⚠️  No phoneNumber in settings")
    
    # 3. Check settings manager
    print("\n3. Checking Settings Manager...")
    settings_manager = SettingsManager()
    settings_manager.set_database(db)
    
    email_from_manager = settings_manager.get('emailAddress')
    phone_from_manager = settings_manager.get('phoneNumber')
    
    print(f"   📧 Email from manager: {email_from_manager}")
    print(f"   📱 Phone from manager: {phone_from_manager}")
    
    # 4. Check .env fallback values
    print("\n4. Checking .env fallback values...")
    env_email = os.getenv('ADMIN_EMAIL')
    env_phone = os.getenv('ADMIN_PHONE_NUMBER')
    
    print(f"   📧 ADMIN_EMAIL in .env: {env_email}")
    print(f"   📱 ADMIN_PHONE_NUMBER in .env: {env_phone}")
    
    # 5. Simulate what alert services will use
    print("\n5. Simulating alert service behavior...")
    
    # Email logic
    if email_from_manager and email_from_manager != 'admin@arcs.local':
        final_email = email_from_manager
        email_source = "Settings Module"
    else:
        final_email = env_email or 'admin@arcs.local'
        email_source = ".env fallback"
    
    print(f"   📧 Email alerts will go to: {final_email}")
    print(f"      Source: {email_source}")
    
    # Phone logic
    if phone_from_manager and phone_from_manager != '+1 (555) 123-4567':
        final_phone = phone_from_manager
        phone_source = "Settings Module"
    else:
        final_phone = env_phone or '+1 (555) 123-4567'
        phone_source = ".env fallback"
    
    print(f"   📱 SMS alerts will go to: {final_phone}")
    print(f"      Source: {phone_source}")
    
    # 6. Check if backend is using old instances
    print("\n6. Checking for potential issues...")
    
    issues = []
    
    if email_from_manager == 'admin@arcs.local':
        issues.append("Email in MongoDB is still default placeholder")
    
    if phone_from_manager == '+1 (555) 123-4567':
        issues.append("Phone in MongoDB is still default placeholder")
    
    if not email_from_manager:
        issues.append("No emailAddress key in MongoDB settings")
    
    if not phone_from_manager:
        issues.append("No phoneNumber key in MongoDB settings")
    
    if issues:
        print("   ⚠️  Issues found:")
        for issue in issues:
            print(f"      - {issue}")
    else:
        print("   ✅ No issues found")
    
    # 7. Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if email_from_manager == 'admin@arcs.local' or phone_from_manager == '+1 (555) 123-4567':
        print("\n⚠️  Settings in MongoDB are still default values")
        print("\nTo fix:")
        print("1. Open dashboard: http://localhost:3000")
        print("2. Go to Settings Module")
        print("3. Enter your email and phone")
        print("4. Click 'Save Configuration'")
        print("5. Wait 5 seconds")
        print("6. Run this diagnosis again")
    
    elif final_email == env_email or final_phone == env_phone:
        print("\n⚠️  Backend may be using old service instances")
        print("\nTo fix:")
        print("1. Restart the backend: python backend/main.py")
        print("2. The backend needs to be restarted to use new service instances")
    
    else:
        print("\n✅ Everything looks good!")
        print("\nSettings should be working correctly.")
        print("If alerts still go to wrong address, restart backend:")
        print("   python backend/main.py")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    diagnose_settings()
