"""
Fix user role to superadmin so they can save settings
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv('backend/.env')
sys.path.insert(0, 'backend')

from services.database import DatabaseService

print("=" * 60)
print("FIX USER ROLE TO SUPERADMIN")
print("=" * 60)

db = DatabaseService()

# Your email
user_email = "tanuj077777@gmail.com"

print(f"\n1. Checking user: {user_email}")

# Find user in database
user = db.users.find_one({"email": user_email})

if not user:
    print(f"   ❌ User not found: {user_email}")
    print("\n   Creating user with superadmin role...")
    
    # Create user with superadmin role
    new_user = {
        "email": user_email,
        "role": "superadmin",
        "created_at": db.now_ist() if hasattr(db, 'now_ist') else None
    }
    
    db.users.insert_one(new_user)
    print(f"   ✅ User created with superadmin role")
else:
    current_role = user.get('role', 'user')
    print(f"   ✓ User found")
    print(f"   Current role: {current_role}")
    
    if current_role != 'superadmin':
        print(f"\n2. Updating role to superadmin...")
        
        result = db.users.update_one(
            {"email": user_email},
            {"$set": {"role": "superadmin"}}
        )
        
        if result.modified_count > 0:
            print(f"   ✅ Role updated to superadmin")
        else:
            print(f"   ⚠️  No changes made (might already be superadmin)")
    else:
        print(f"   ✅ User already has superadmin role")

# Verify
print(f"\n3. Verifying...")
user = db.users.find_one({"email": user_email})
if user:
    print(f"   Email: {user.get('email')}")
    print(f"   Role: {user.get('role')}")
    
    if user.get('role') == 'superadmin':
        print(f"\n🎉 SUCCESS! User is now superadmin")
        print(f"\nYou can now:")
        print(f"1. Go to Settings Module in dashboard")
        print(f"2. Change email and phone")
        print(f"3. Click 'Save Configuration'")
        print(f"4. Settings will be saved successfully")
    else:
        print(f"\n❌ Role is still: {user.get('role')}")
else:
    print(f"   ❌ User not found after update")

print("\n" + "=" * 60)
