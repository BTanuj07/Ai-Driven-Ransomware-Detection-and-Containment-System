#!/usr/bin/env python3
"""
Update User Role in Supabase
This script updates a user's role in the ARCS system
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('frontend/.env')

# Get Supabase credentials
SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Need service role key for admin operations

if not SUPABASE_URL:
    print("❌ Error: VITE_SUPABASE_URL not found in frontend/.env")
    sys.exit(1)

if not SUPABASE_SERVICE_KEY:
    print("⚠️  Warning: SUPABASE_SERVICE_ROLE_KEY not found")
    print("   You'll need to use the SQL script instead (update_user_role.sql)")
    print("   Or add SUPABASE_SERVICE_ROLE_KEY to your .env file")
    sys.exit(1)

# Available roles
ROLES = {
    '1': ('superadmin', 'Super Admin - Full system access'),
    '2': ('analyst', 'SOC Analyst - Monitoring and investigation'),
    '3': ('responder', 'Incident Responder - Action execution and containment'),
    '4': ('viewer', 'Viewer - Read-only access')
}

def main():
    print("=" * 70)
    print("  👤 ARCS USER ROLE UPDATER")
    print("=" * 70)
    
    try:
        # Create Supabase client with service role key
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("\n✅ Connected to Supabase")
    except Exception as e:
        print(f"\n❌ Failed to connect to Supabase: {e}")
        return
    
    # Get user email
    print("\n📧 Enter the user's email address:")
    email = input("   Email: ").strip().lower()
    
    if not email:
        print("❌ Email cannot be empty")
        return
    
    # Check if user exists
    try:
        # Note: This requires service role key to access auth.users
        response = supabase.auth.admin.list_users()
        users = [u for u in response if u.email == email]
        
        if not users:
            print(f"\n❌ User not found: {email}")
            return
        
        user = users[0]
        current_role = user.user_metadata.get('role', 'viewer')
        print(f"\n✅ User found: {email}")
        print(f"   Current role: {current_role}")
        
    except Exception as e:
        print(f"\n⚠️  Could not verify user: {e}")
        print("   Proceeding anyway...")
    
    # Display role options
    print("\n🎯 Select new role:")
    for key, (role, description) in ROLES.items():
        print(f"   {key}. {role.upper()} - {description}")
    print("   5. Cancel")
    
    choice = input("\n👉 Select option (1-5): ").strip()
    
    if choice == '5':
        print("\n👋 Cancelled")
        return
    
    if choice not in ROLES:
        print("\n❌ Invalid option")
        return
    
    new_role, description = ROLES[choice]
    
    # Confirm
    print(f"\n⚠️  Confirm role update:")
    print(f"   Email: {email}")
    print(f"   New Role: {new_role.upper()}")
    print(f"   Description: {description}")
    
    confirm = input("\n   Proceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("\n👋 Cancelled")
        return
    
    # Update user role
    try:
        # Update user metadata
        supabase.auth.admin.update_user_by_id(
            user.id,
            {
                "user_metadata": {
                    "role": new_role
                }
            }
        )
        
        print(f"\n✅ Successfully updated user role!")
        print(f"   Email: {email}")
        print(f"   New Role: {new_role.upper()}")
        print(f"\n📝 The user needs to:")
        print(f"   1. Log out of the ARCS dashboard")
        print(f"   2. Log back in to see the new role")
        
    except Exception as e:
        print(f"\n❌ Failed to update user role: {e}")
        print("\n💡 Alternative: Use the SQL script instead")
        print("   1. Open Supabase Dashboard → SQL Editor")
        print("   2. Run the SQL from update_user_role.sql")
        print(f"   3. Replace 'user@example.com' with '{email}'")
        print(f"   4. Replace '\"viewer\"' with '\"{new_role}\"'")

if __name__ == "__main__":
    main()
