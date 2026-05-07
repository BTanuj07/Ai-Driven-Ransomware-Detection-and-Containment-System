"""
Verify backend configuration for Supabase authentication
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("BACKEND CONFIGURATION VERIFICATION")
print("=" * 60)

# Load .env
load_dotenv('backend/.env')

# Check SUPABASE_JWT_SECRET
supabase_secret = os.getenv("SUPABASE_JWT_SECRET")

print("\n1. Checking SUPABASE_JWT_SECRET:")
if supabase_secret:
    print(f"   ✅ Found in backend/.env")
    print(f"   Value: {supabase_secret[:50]}...")
else:
    print(f"   ❌ NOT FOUND in backend/.env")
    print(f"\n   FIX: Add this line to backend/.env:")
    print(f"   SUPABASE_JWT_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhzYmNqb256Ym53am5mdGZvaHlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4NDYyODQsImV4cCI6MjA5MjQyMjI4NH0.US2wYmEBEUAvi0tgmLcYT6upTWcY5OkgFD3eJhiLP3Q")

# Check MongoDB URL
mongodb_url = os.getenv("MONGODB_URL")
print("\n2. Checking MONGODB_URL:")
if mongodb_url:
    print(f"   ✅ Found")
else:
    print(f"   ❌ NOT FOUND")

# Check other configs
print("\n3. Other configurations:")
print(f"   SENDGRID_API_KEY: {'✅ Set' if os.getenv('SENDGRID_API_KEY') else '❌ Not set'}")
print(f"   TWILIO_ACCOUNT_SID: {'✅ Set' if os.getenv('TWILIO_ACCOUNT_SID') else '❌ Not set'}")
print(f"   ADMIN_EMAIL: {os.getenv('ADMIN_EMAIL', 'Not set')}")
print(f"   ADMIN_PHONE_NUMBER: {os.getenv('ADMIN_PHONE_NUMBER', 'Not set')}")

print("\n" + "=" * 60)
print("NEXT STEPS")
print("=" * 60)

if not supabase_secret:
    print("\n❌ SUPABASE_JWT_SECRET is missing!")
    print("\n1. Open backend/.env")
    print("2. Add the SUPABASE_JWT_SECRET line shown above")
    print("3. Save the file")
    print("4. Restart backend: python backend/main.py")
else:
    print("\n✅ Configuration looks good!")
    print("\nIf you're still getting 401 errors:")
    print("1. Make sure backend is RESTARTED")
    print("2. Check backend logs for:")
    print("   - '✅ Supabase JWT validation enabled'")
    print("   - '🔑 Trying Supabase JWT validation...'")
    print("3. If you don't see these logs, backend didn't restart properly")

print("\n" + "=" * 60)
