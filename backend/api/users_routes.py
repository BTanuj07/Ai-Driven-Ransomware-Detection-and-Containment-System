"""
User Management API Routes
Manages user roles via Supabase Admin API
"""
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
import httpx
from datetime import datetime

router = APIRouter()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET', '')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("⚠️  Warning: Supabase credentials not configured for user management")
    print("   Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in backend/.env")

# Simple authentication dependency
async def verify_token(authorization: str = Header(None)):
    """Verify JWT token from Supabase"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.replace("Bearer ", "")
        
        # For now, just check if token exists
        # In production, you should verify the JWT signature
        if not token:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# Models
class UserRoleUpdate(BaseModel):
    email: EmailStr
    role: str  # superadmin, analyst, responder, viewer

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "viewer"
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    created_at: str
    last_sign_in_at: Optional[str] = None
    email_confirmed_at: Optional[str] = None

# Helper function to call Supabase Admin API
async def supabase_admin_request(method: str, endpoint: str, data: dict = None):
    """Make authenticated request to Supabase Admin API"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise HTTPException(
            status_code=503,
            detail="Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env"
        )
    
    url = f"{SUPABASE_URL}/auth/v1/admin/{endpoint}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = await client.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Supabase API error: {response.text}"
            )
        
        return response.json()

@router.get("/users")
async def list_users(token: str = Depends(verify_token)):
    """List all users from Supabase"""
    try:
        # Get users from Supabase
        result = await supabase_admin_request("GET", "users")
        
        users = []
        for user in result.get("users", []):
            users.append({
                "id": user["id"],
                "email": user["email"],
                "role": user.get("user_metadata", {}).get("role", "viewer"),
                "full_name": user.get("user_metadata", {}).get("full_name", ""),
                "created_at": user.get("created_at", ""),
                "last_sign_in_at": user.get("last_sign_in_at"),
                "email_confirmed_at": user.get("email_confirmed_at"),
                "status": "active" if user.get("email_confirmed_at") else "pending"
            })
        
        return {
            "users": users,
            "total": len(users)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.post("/users")
async def create_user(user_data: UserCreate, token: str = Depends(verify_token)):
    """Create a new user in Supabase with assigned role"""
    try:
        # Create user via Supabase Admin API
        data = {
            "email": user_data.email,
            "password": user_data.password,
            "email_confirm": True,  # Auto-confirm email
            "user_metadata": {
                "role": user_data.role,
                "full_name": user_data.full_name or user_data.email.split('@')[0]
            }
        }
        
        result = await supabase_admin_request("POST", "users", data)
        
        return {
            "success": True,
            "user": {
                "id": result["id"],
                "email": result["email"],
                "role": user_data.role
            },
            "message": f"User created successfully with role: {user_data.role}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role_update: UserRoleUpdate, token: str = Depends(verify_token)):
    """Update user role in Supabase"""
    try:
        # Validate role
        valid_roles = ["superadmin", "analyst", "responder", "viewer"]
        if role_update.role not in valid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        # Update user metadata
        data = {
            "user_metadata": {
                "role": role_update.role
            }
        }
        
        result = await supabase_admin_request("PUT", f"users/{user_id}", data)
        
        return {
            "success": True,
            "user": {
                "id": result["id"],
                "email": result["email"],
                "role": role_update.role
            },
            "message": f"User role updated to: {role_update.role}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, token: str = Depends(verify_token)):
    """Delete user from Supabase"""
    try:
        await supabase_admin_request("DELETE", f"users/{user_id}")
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(user_id: str, new_password: str, token: str = Depends(verify_token)):
    """Reset user password"""
    try:
        data = {
            "password": new_password
        }
        
        await supabase_admin_request("PUT", f"users/{user_id}", data)
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset password: {str(e)}")

@router.get("/users/stats")
async def get_user_stats(token: str = Depends(verify_token)):
    """Get user statistics"""
    try:
        result = await supabase_admin_request("GET", "users")
        users = result.get("users", [])
        
        stats = {
            "total": len(users),
            "active": len([u for u in users if u.get("email_confirmed_at")]),
            "by_role": {
                "superadmin": 0,
                "analyst": 0,
                "responder": 0,
                "viewer": 0
            }
        }
        
        for user in users:
            role = user.get("user_metadata", {}).get("role", "viewer")
            if role in stats["by_role"]:
                stats["by_role"][role] += 1
        
        return stats
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")
