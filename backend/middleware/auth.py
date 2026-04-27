"""
JWT Authentication Middleware
Protects API endpoints with token validation
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
import os
from datetime import datetime, timedelta

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

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
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
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
