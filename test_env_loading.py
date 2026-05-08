"""
Test if .env is being loaded correctly
"""
import os
import sys
from dotenv import load_dotenv

print("=" * 60)
print("TESTING .ENV LOADING")
print("=" * 60)

print(f"\nCurrent working directory: {os.getcwd()}")

# Try loading from backend/.env
print(f"\n1. Loading from backend/.env...")
load_dotenv('backend/.env')

supabase_secret = os.getenv('SUPABASE_JWT_SECRET')

if supabase_secret:
    print(f"   ✅ SUPABASE_JWT_SECRET loaded")
    print(f"   Value: {supabase_secret[:50]}...")
else:
    print(f"   ❌ SUPABASE_JWT_SECRET not found")

# Try loading from current directory
print(f"\n2. Loading from .env (current dir)...")
load_dotenv('.env')

supabase_secret2 = os.getenv('SUPABASE_JWT_SECRET')

if supabase_secret2:
    print(f"   ✅ SUPABASE_JWT_SECRET loaded")
    print(f"   Value: {supabase_secret2[:50]}...")
else:
    print(f"   ❌ SUPABASE_JWT_SECRET not found")

print("\n" + "=" * 60)
