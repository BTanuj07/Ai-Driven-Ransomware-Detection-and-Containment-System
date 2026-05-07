"""
Test Supabase token validation
"""
import os
import sys
import jwt
from dotenv import load_dotenv

load_dotenv('backend/.env')

# Get Supabase JWT secret
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

print("=" * 60)
print("TESTING SUPABASE TOKEN VALIDATION")
print("=" * 60)

print(f"\n1. Checking SUPABASE_JWT_SECRET in .env:")
if SUPABASE_JWT_SECRET:
    print(f"   ✅ Found: {SUPABASE_JWT_SECRET[:50]}...")
else:
    print(f"   ❌ NOT FOUND in .env")
    print(f"   Add this to backend/.env:")
    print(f"   SUPABASE_JWT_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    sys.exit(1)

# Test token (you need to get this from browser)
print(f"\n2. To test token validation:")
print(f"   a. Open browser console on http://localhost:3000")
print(f"   b. Run: (await supabase.auth.getSession()).data.session.access_token")
print(f"   c. Copy the token")
print(f"   d. Paste it below when prompted")

test_token = input("\nPaste Supabase token (or press Enter to skip): ").strip()

if test_token:
    print(f"\n3. Testing token validation...")
    try:
        payload = jwt.decode(
            test_token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        
        print(f"   ✅ Token is valid!")
        print(f"\n   Token payload:")
        print(f"   - sub (user_id): {payload.get('sub')}")
        print(f"   - email: {payload.get('email')}")
        print(f"   - exp: {payload.get('exp')}")
        print(f"   - iat: {payload.get('iat')}")
        
        # Check if user exists in MongoDB
        sys.path.insert(0, 'backend')
        from services.database import DatabaseService
        
        db = DatabaseService()
        email = payload.get('email')
        user = db.users.find_one({"email": email})
        
        if user:
            print(f"\n   ✅ User found in MongoDB:")
            print(f"   - Email: {user.get('email')}")
            print(f"   - Role: {user.get('role')}")
        else:
            print(f"\n   ⚠️  User NOT found in MongoDB")
            print(f"   Run: python fix_user_role.py")
        
    except jwt.ExpiredSignatureError:
        print(f"   ❌ Token has expired")
        print(f"   Logout and login again to get a new token")
    except jwt.InvalidTokenError as e:
        print(f"   ❌ Token is invalid: {e}")
        print(f"   Check if SUPABASE_JWT_SECRET is correct")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print(f"\n   Skipped token test")

print(f"\n4. Backend restart check:")
print(f"   ⚠️  Make sure you RESTARTED the backend after adding SUPABASE_JWT_SECRET")
print(f"   Stop backend (Ctrl+C) and run: python backend/main.py")

print("\n" + "=" * 60)
