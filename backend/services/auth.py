"""
Authentication and Authorization Service
Handles user management, JWT tokens, and RBAC
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class Permission(Enum):
    # Alert permissions
    VIEW_ALERTS = "view_alerts"
    MANAGE_ALERTS = "manage_alerts"
    
    # Endpoint permissions
    VIEW_ENDPOINTS = "view_endpoints"
    ISOLATE_ENDPOINT = "isolate_endpoint"
    KILL_PROCESS = "kill_process"
    
    # User management
    MANAGE_USERS = "manage_users"
    
    # System settings
    MANAGE_SETTINGS = "manage_settings"
    
    # Reports
    VIEW_REPORTS = "view_reports"
    GENERATE_REPORTS = "generate_reports"
    
    # Logs
    VIEW_LOGS = "view_logs"
    EXPORT_LOGS = "export_logs"
    
    # Response actions
    TRIGGER_RESPONSE = "trigger_response"
    VIEW_RESPONSE_HISTORY = "view_response_history"

# Role-Permission mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [p for p in Permission],  # All permissions
    UserRole.ANALYST: [
        Permission.VIEW_ALERTS,
        Permission.MANAGE_ALERTS,
        Permission.VIEW_ENDPOINTS,
        Permission.ISOLATE_ENDPOINT,
        Permission.KILL_PROCESS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_LOGS,
        Permission.EXPORT_LOGS,
        Permission.TRIGGER_RESPONSE,
        Permission.VIEW_RESPONSE_HISTORY,
    ],
    UserRole.VIEWER: [
        Permission.VIEW_ALERTS,
        Permission.VIEW_ENDPOINTS,
        Permission.VIEW_REPORTS,
        Permission.VIEW_LOGS,
        Permission.VIEW_RESPONSE_HISTORY,
    ]
}

class AuthService:
    def __init__(self, secret_key: str = "arcs-secret-key-change-in-production"):
        self.secret_key = secret_key
        self.token_expiry = timedelta(hours=8)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_token(self, user_id: str, username: str, role: str) -> str:
        """Create JWT token"""
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def has_permission(self, role: str, permission: Permission) -> bool:
        """Check if role has specific permission"""
        try:
            user_role = UserRole(role)
            return permission in ROLE_PERMISSIONS.get(user_role, [])
        except ValueError:
            return False
    
    def get_role_permissions(self, role: str) -> List[str]:
        """Get all permissions for a role"""
        try:
            user_role = UserRole(role)
            return [p.value for p in ROLE_PERMISSIONS.get(user_role, [])]
        except ValueError:
            return []

class UserService:
    def __init__(self, db):
        self.db = db
        self.auth = AuthService()
        self.users_collection = db.db.users if db.client else None
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user if not exists"""
        if self.users_collection is None:
            return
        
        admin_exists = self.users_collection.find_one({"username": "admin"})
        if not admin_exists:
            self.create_user(
                username="admin",
                password="admin123",  # Change in production!
                email="admin@arcs.local",
                role=UserRole.ADMIN.value,
                full_name="System Administrator"
            )
            print("✅ Default admin user created (username: admin, password: admin123)")
    
    def create_user(self, username: str, password: str, email: str, 
                   role: str, full_name: str) -> Dict[str, Any]:
        """Create new user"""
        if self.users_collection is None:
            return {"error": "Database not available"}
        
        # Check if user exists
        if self.users_collection.find_one({"username": username}):
            return {"error": "Username already exists"}
        
        if self.users_collection.find_one({"email": email}):
            return {"error": "Email already exists"}
        
        user_data = {
            "username": username,
            "password": self.auth.hash_password(password),
            "email": email,
            "role": role,
            "full_name": full_name,
            "active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "login_history": []
        }
        
        result = self.users_collection.insert_one(user_data)
        return {
            "user_id": str(result.inserted_id),
            "username": username,
            "role": role
        }
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return token"""
        if self.users_collection is None:
            return None
        
        user = self.users_collection.find_one({"username": username})
        if not user or not user.get("active"):
            return None
        
        if not self.auth.verify_password(password, user["password"]):
            return None
        
        # Update last login
        self.users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {"last_login": datetime.utcnow()},
                "$push": {
                    "login_history": {
                        "timestamp": datetime.utcnow(),
                        "ip": "unknown"  # Add IP tracking in production
                    }
                }
            }
        )
        
        token = self.auth.create_token(
            str(user["_id"]),
            user["username"],
            user["role"]
        )
        
        return {
            "token": token,
            "user": {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "full_name": user["full_name"],
                "permissions": self.auth.get_role_permissions(user["role"])
            }
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if self.users_collection is None:
            return None
        
        from bson import ObjectId
        user = self.users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
            user.pop("password", None)  # Remove password from response
            return user
        return None
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users"""
        if self.users_collection is None:
            return []
        
        users = []
        for user in self.users_collection.find():
            user["_id"] = str(user["_id"])
            user.pop("password", None)
            users.append(user)
        return users
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user"""
        if self.users_collection is None:
            return False
        
        from bson import ObjectId
        # Don't allow password update through this method
        updates.pop("password", None)
        updates["updated_at"] = datetime.utcnow()
        
        result = self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete - deactivate)"""
        if self.users_collection is None:
            return False
        
        from bson import ObjectId
        result = self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"active": False, "deactivated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    def reset_password(self, user_id: str, new_password: str) -> bool:
        """Reset user password"""
        if self.users_collection is None:
            return False
        
        from bson import ObjectId
        hashed = self.auth.hash_password(new_password)
        result = self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": hashed, "password_reset_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
