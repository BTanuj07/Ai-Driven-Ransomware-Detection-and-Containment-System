#!/usr/bin/env python3
"""
Sync User Role from Supabase to MongoDB
This ensures consistency between Supabase auth and MongoDB user records
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# MongoDB connection
MONGODB_URL = os.getenv('MONGODB_URL')

if not MONGODB_URL:
    print("❌ Error: MONGODB_URL not found in backend/.env")
    sys.exit(1)

# Role mapping (Supabase → MongoDB)
ROLE_MAPPING = {
    'superadmin': 'admin',      # Supabase superadmin → MongoDB admin
    'responder': 'analyst',     # Supabase responder → MongoDB analyst
    'analyst': 'analyst',       # Supabase analyst → MongoDB analyst
    'viewer': 'viewer'          # Supabase viewer → MongoDB viewer
}

def main():
    print("=" * 70)
    print("  🔄 SYNC USER ROLE TO MONGODB")
    print("=" * 70)
    
    # Connect to MongoDB
    try:
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        db = client['arcs_db']
        users_collection = db['users']
        print("\n✅ Connected to MongoDB")
    except Exception as e:
        print(f"\n❌ Failed to connect to MongoDB: {e}")
        return
    
    # Get user details
    print("\n📧 Enter user details:")
    email = input("   Email: ").strip().lower()
    
    if not email:
        print("❌ Email cannot be empty")
        return
    
    # Display role options
    print("\n🎯 Select Supabase role (what you set in Supabase):")
    print("   1. superadmin - Super Admin")
    print("   2. responder - Incident Responder")
    print("   3. analyst - SOC Analyst")
    print("   4. viewer - Viewer")
    print("   5. Cancel")
    
    choice = input("\n👉 Select option (1-5): ").strip()
    
    if choice == '5':
        print("\n👋 Cancelled")
        return
    
    role_map = {
        '1': 'superadmin',
        '2': 'responder',
        '3': 'analyst',
        '4': 'viewer'
    }
    
    if choice not in role_map:
        print("\n❌ Invalid option")
        return
    
    supabase_role = role_map[choice]
    mongodb_role = ROLE_MAPPING[supabase_role]
    
    print(f"\n📝 Role mapping:")
    print(f"   Supabase role: {supabase_role}")
    print(f"   MongoDB role: {mongodb_role}")
    
    # Check if user exists in MongoDB
    existing_user = users_collection.find_one({"email": email})
    
    if existing_user:
        print(f"\n✅ User found in MongoDB")
        print(f"   Current MongoDB role: {existing_user.get('role', 'N/A')}")
        
        # Update existing user
        result = users_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "role": mongodb_role,
                    "updated_at": datetime.utcnow(),
                    "supabase_role": supabase_role
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"\n✅ Updated user role in MongoDB")
        else:
            print(f"\n⚠️  No changes made (role already set)")
    else:
        print(f"\n⚠️  User not found in MongoDB")
        print(f"   Creating new user record...")
        
        # Get username from email
        username = email.split('@')[0]
        
        # Create new user record
        user_data = {
            "username": username,
            "email": email,
            "role": mongodb_role,
            "supabase_role": supabase_role,
            "full_name": username.title(),
            "active": True,
            "created_at": datetime.utcnow(),
            "synced_from_supabase": True,
            "last_login": None
        }
        
        result = users_collection.insert_one(user_data)
        print(f"\n✅ Created user in MongoDB with role: {mongodb_role}")
    
    print(f"\n📋 Summary:")
    print(f"   Email: {email}")
    print(f"   Supabase Role: {supabase_role}")
    print(f"   MongoDB Role: {mongodb_role}")
    print(f"\n⚠️  Remember:")
    print(f"   1. Update the role in Supabase first (using SQL)")
    print(f"   2. User must log out and log back in")
    print(f"   3. This script only syncs to MongoDB for consistency")
    
    client.close()

if __name__ == "__main__":
    main()
