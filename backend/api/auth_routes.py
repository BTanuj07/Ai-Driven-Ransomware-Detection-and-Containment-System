"""
Authentication and User Management API Routes
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel
from services.auth import AuthService, UserService, Permission

router = APIRouter()

# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str
    role: str
    full_name: str

class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    full_name: Optional[str] = None
    active: Optional[bool] = None

class ResetPasswordRequest(BaseModel):
    new_password: str

# Dependency to get current user from token
async def get_current_user(authorization: Optional[str] = Header(None), request: Request = None):
    """Extract and validate user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    auth_service = AuthService()
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload

# Dependency to check permissions
def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        auth_service = AuthService()
        if not auth_service.has_permission(current_user["role"], permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return permission_checker

@router.post("/auth/login")
async def login(request: Request, login_data: LoginRequest):
    """User login"""
    db = request.app.state.db
    user_service = UserService(db)
    
    result = user_service.authenticate(login_data.username, login_data.password)
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Log audit
    db.insert_audit_log(
        action="USER_LOGIN",
        user=login_data.username,
        details={"success": True}
    )
    
    return result

@router.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user), request: Request = None):
    """User logout"""
    db = request.app.state.db
    
    # Log audit
    db.insert_audit_log(
        action="USER_LOGOUT",
        user=current_user["username"],
        details={}
    )
    
    return {"message": "Logged out successfully"}

@router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user), request: Request = None):
    """Get current user information"""
    db = request.app.state.db
    user_service = UserService(db)
    
    user = user_service.get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user": user,
        "permissions": AuthService().get_role_permissions(user["role"])
    }

# User Management Routes (Admin only)
@router.get("/users")
async def list_users(
    current_user: dict = Depends(require_permission(Permission.MANAGE_USERS)),
    request: Request = None
):
    """List all users (Admin only)"""
    db = request.app.state.db
    user_service = UserService(db)
    
    users = user_service.list_users()
    return {"users": users, "count": len(users)}

@router.post("/users")
async def create_user(
    user_data: CreateUserRequest,
    current_user: dict = Depends(require_permission(Permission.MANAGE_USERS)),
    request: Request = None
):
    """Create new user (Admin only)"""
    db = request.app.state.db
    user_service = UserService(db)
    
    result = user_service.create_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email,
        role=user_data.role,
        full_name=user_data.full_name
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Log audit
    db.insert_audit_log(
        action="USER_CREATED",
        user=current_user["username"],
        details={"new_user": user_data.username, "role": user_data.role}
    )
    
    return result

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: dict = Depends(require_permission(Permission.MANAGE_USERS)),
    request: Request = None
):
    """Get user details (Admin only)"""
    db = request.app.state.db
    user_service = UserService(db)
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user": user}

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    updates: UpdateUserRequest,
    current_user: dict = Depends(require_permission(Permission.MANAGE_USERS)),
    request: Request = None
):
    """Update user (Admin only)"""
    db = request.app.state.db
    user_service = UserService(db)
    
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    success = user_service.update_user(user_id, update_dict)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update user")
    
    # Log audit
    db.insert_audit_log(
        action="USER_UPDATED",
        user=current_user["username"],
        details={"target_user_id": user_id, "updates": update_dict}
    )
    
    return {"message": "User updated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_permission(Permission.MANAGE_USERS)),
    request: Request = None
):
    """Delete user (Admin only)"""
    db = request.app.state.db
    user_service = UserService(db)
    
    # Prevent self-deletion
    if user_id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    success = user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete user")
    
    # Log audit
    db.insert_audit_log(
        action="USER_DELETED",
        user=current_user["username"],
        details={"target_user_id": user_id}
    )
    
    return {"message": "User deleted successfully"}

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    password_data: ResetPasswordRequest,
    current_user: dict = Depends(require_permission(Permission.MANAGE_USERS)),
    request: Request = None
):
    """Reset user password (Admin only)"""
    db = request.app.state.db
    user_service = UserService(db)
    
    success = user_service.reset_password(user_id, password_data.new_password)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to reset password")
    
    # Log audit
    db.insert_audit_log(
        action="PASSWORD_RESET",
        user=current_user["username"],
        details={"target_user_id": user_id}
    )
    
    return {"message": "Password reset successfully"}

@router.get("/users/{user_id}/login-history")
async def get_login_history(
    user_id: str,
    current_user: dict = Depends(require_permission(Permission.MANAGE_USERS)),
    request: Request = None
):
    """Get user login history (Admin only)"""
    db = request.app.state.db
    user_service = UserService(db)
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "username": user["username"],
        "login_history": user.get("login_history", [])
    }
