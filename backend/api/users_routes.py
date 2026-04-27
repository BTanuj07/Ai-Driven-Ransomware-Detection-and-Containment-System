"""
Users API Routes - MongoDB User Management
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from middleware.auth import require_auth, require_superadmin

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    role: str
    status: str = "active"

class UserUpdate(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None

@router.get("/users")
async def get_users(request: Request, user: dict = Depends(require_auth)):
    """Get all users"""
    db = request.app.state.db
    
    # Get users from database
    users_collection = db.db['users']
    users = list(users_collection.find({}, {'password': 0}))  # Exclude passwords
    
    # Serialize
    for user_doc in users:
        user_doc['_id'] = str(user_doc['_id'])
        user_doc['id'] = user_doc['_id']
    
    return {
        "users": users,
        "count": len(users)
    }

@router.post("/users")
async def create_user(
    request: Request,
    user_data: UserCreate,
    current_user: dict = Depends(require_superadmin)
):
    """Create new user (superadmin only)"""
    db = request.app.state.db
    users_collection = db.db['users']
    
    # Check if user already exists
    existing = users_collection.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user document
    new_user = {
        "email": user_data.email,
        "role": user_data.role,
        "status": user_data.status,
        "created_at": datetime.utcnow(),
        "created_by": current_user.get('email'),
        "last_login": None,
        "active_sessions": 0
    }
    
    result = users_collection.insert_one(new_user)
    
    # Log the action
    db.insert_audit_log(
        action="CREATE_USER",
        user=current_user.get('email'),
        details={"new_user_email": user_data.email, "role": user_data.role}
    )
    
    new_user['_id'] = str(result.inserted_id)
    new_user['id'] = new_user['_id']
    
    return {
        "status": "success",
        "message": "User created successfully",
        "user": new_user
    }

@router.put("/users/{user_id}")
async def update_user(
    request: Request,
    user_id: str,
    user_data: UserUpdate,
    current_user: dict = Depends(require_superadmin)
):
    """Update user (superadmin only)"""
    db = request.app.state.db
    users_collection = db.db['users']
    
    from bson import ObjectId
    
    # Build update dict
    update_dict = {k: v for k, v in user_data.dict().items() if v is not None}
    update_dict['updated_at'] = datetime.utcnow()
    update_dict['updated_by'] = current_user.get('email')
    
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log the action
    db.insert_audit_log(
        action="UPDATE_USER",
        user=current_user.get('email'),
        details={"user_id": user_id, "changes": update_dict}
    )
    
    return {
        "status": "success",
        "message": "User updated successfully"
    }

@router.delete("/users/{user_id}")
async def delete_user(
    request: Request,
    user_id: str,
    current_user: dict = Depends(require_superadmin)
):
    """Delete user (superadmin only)"""
    db = request.app.state.db
    users_collection = db.db['users']
    
    from bson import ObjectId
    
    # Get user before deleting
    user_to_delete = users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting superadmin
    if user_to_delete.get('role') == 'superadmin':
        raise HTTPException(status_code=403, detail="Cannot delete superadmin user")
    
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    
    # Log the action
    db.insert_audit_log(
        action="DELETE_USER",
        user=current_user.get('email'),
        details={"deleted_user_email": user_to_delete.get('email')}
    )
    
    return {
        "status": "success",
        "message": "User deleted successfully"
    }

@router.post("/users/{user_id}/suspend")
async def suspend_user(
    request: Request,
    user_id: str,
    current_user: dict = Depends(require_superadmin)
):
    """Suspend user account"""
    db = request.app.state.db
    users_collection = db.db['users']
    
    from bson import ObjectId
    
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "status": "suspended",
            "suspended_at": datetime.utcnow(),
            "suspended_by": current_user.get('email'),
            "active_sessions": 0
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "success",
        "message": "User suspended successfully"
    }
