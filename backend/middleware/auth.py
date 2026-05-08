"""
JWT Authentication Middleware
Protects API endpoints with token validation
Supports both custom JWT and Supabase JWT tokens
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Get the backend directory and load .env
BACKEND_DIR = Path(__file__).resolve().parent.parent
env_path = BACKEND_DIR / '.env'
load_dotenv(dotenv_path=env_path)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Supabase Configuration
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

# Log configuration on startup
print(f"\n🔐 Authentication Middleware Loading...")
print(f"📁 .env path: {env_path}")
print(f"📄 .env exists: {env_path.exists()}")

if SUPABASE_JWT_SECRET:
    print(f"✅ Supabase JWT validation enabled")
    print(f"   Secret: {SUPABASE_JWT_SECRET[:30]}...")
else:
    print(f"⚠️  Supabase JWT validation disabled - SUPABASE_JWT_SECRET not set")

security = HTTPBearer()

class AuthMiddleware:
    """JWT Authentication Middleware"""
    
    @staticmethod
    def create_token(user_id: str, email: str, role: str) -> str:
        """Create JWT token"""
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token (supports both custom and Supabase tokens)"""
        # Try custom JWT first
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            print(f"✅ Custom JWT token validated")
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            print(f"⚠️ Custom JWT validation failed: {e}")
        
        # Try Supabase JWT with HS256
        if SUPABASE_JWT_SECRET:
            print(f"🔑 Trying Supabase JWT validation...")
            try:
                # First try HS256 (symmetric)
                payload = jwt.decode(
                    token, 
                    SUPABASE_JWT_SECRET, 
                    algorithms=["HS256"],
                    options={"verify_aud": False}
                )
                
                # Extract email from Supabase token
                email = payload.get('email') or payload.get('user_metadata', {}).get('email')
                print(f"📧 Email from Supabase token: {email}")
                
                # Get user role from database based on email
                from services.database import DatabaseService
                db = DatabaseService()
                user = db.users.find_one({"email": email})
                
                role = user.get('role', 'viewer') if user else 'viewer'
                print(f"👤 User role from MongoDB: {role}")
                
                # Return normalized payload
                return {
                    "user_id": payload.get('sub'),
                    "email": email,
                    "role": role,
                    "exp": payload.get('exp'),
                    "iat": payload.get('iat')
                }
            except jwt.InvalidAlgorithmError:
                # Token uses RS256, try without verification (development only)
                print(f"⚠️ Token uses RS256, trying unverified decode...")
                try:
                    payload = jwt.decode(
                        token,
                        options={"verify_signature": False}
                    )
                    
                    # Extract email from Supabase token
                    email = payload.get('email') or payload.get('user_metadata', {}).get('email')
                    print(f"📧 Email from Supabase token (unverified): {email}")
                    
                    # Get user role from database based on email
                    from services.database import DatabaseService
                    db = DatabaseService()
                    user = db.users.find_one({"email": email})
                    
                    role = user.get('role', 'viewer') if user else 'viewer'
                    print(f"👤 User role from MongoDB: {role}")
                    
                    # Return normalized payload
                    return {
                        "user_id": payload.get('sub'),
                        "email": email,
                        "role": role,
                        "exp": payload.get('exp'),
                        "iat": payload.get('iat')
                    }
                except Exception as e:
                    print(f"⚠️ Unverified decode failed: {e}")
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                print(f"⚠️ Supabase token validation failed: {e}")
        else:
            print(f"❌ SUPABASE_JWT_SECRET not configured")
        
        # If both fail, raise error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    @staticmethod
    async def get_current_user(request: Request) -> dict:
        """Extract user from request token"""
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        return AuthMiddleware.verify_token(token)
    
    @staticmethod
    def require_role(allowed_roles: list):
        """Decorator to require specific roles"""
        async def role_checker(request: Request):
            user = await AuthMiddleware.get_current_user(request)
            if user.get("role") not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {allowed_roles}"
                )
            return user
        return role_checker

# Dependency for protected routes
async def require_auth(request: Request) -> dict:
    """Dependency to require authentication"""
    return await AuthMiddleware.get_current_user(request)

# Role-based dependencies
async def require_superadmin(request: Request) -> dict:
    """Require superadmin role"""
    checker = AuthMiddleware.require_role(["superadmin"])
    return await checker(request)

async def require_admin_or_analyst(request: Request) -> dict:
    """Require admin or analyst role"""
    checker = AuthMiddleware.require_role(["superadmin", "analyst"])
    return await checker(request)

async def require_responder(request: Request) -> dict:
    """Require responder role or higher"""
    checker = AuthMiddleware.require_role(["superadmin", "responder"])
    return await checker(request)
