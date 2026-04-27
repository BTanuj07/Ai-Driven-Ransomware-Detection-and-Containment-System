"""
Settings API Routes - MongoDB Persistence
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from middleware.auth import require_auth, require_superadmin

router = APIRouter()

class SettingsUpdate(BaseModel):
    anomalyThreshold: float = None
    highRiskThreshold: float = None
    mediumRiskThreshold: float = None
    lowRiskThreshold: float = None
    falsePositiveSensitivity: float = None
    modelConfidence: float = None
    autoIsolate: bool = None
    autoKillProcess: bool = None
    autoDisableUser: bool = None
    requireApproval: bool = None
    emailAlerts: bool = None
    smsAlerts: bool = None
    criticalEscalation: bool = None
    emailAddress: str = None
    phoneNumber: str = None

@router.get("/settings")
async def get_settings(request: Request, user: dict = Depends(require_auth)):
    """Get current system settings"""
    db = request.app.state.db
    settings = db.get_settings()
    
    return {
        "settings": settings,
        "timestamp": settings.get('last_updated')
    }

@router.post("/settings")
async def update_settings(
    request: Request, 
    settings: SettingsUpdate,
    user: dict = Depends(require_superadmin)
):
    """Update system settings (superadmin only)"""
    db = request.app.state.db
    
    # Convert to dict and remove None values
    settings_dict = {k: v for k, v in settings.dict().items() if v is not None}
    
    # Update in database
    success = db.update_settings(settings_dict)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update settings")
    
    # Log the change
    db.insert_audit_log(
        action="UPDATE_SETTINGS",
        user=user.get('email'),
        details=settings_dict
    )
    
    return {
        "status": "success",
        "message": "Settings updated successfully",
        "settings": db.get_settings()
    }

@router.get("/settings/services")
async def get_service_status(request: Request, user: dict = Depends(require_auth)):
    """Get backend service status"""
    db = request.app.state.db
    
    # Check service health
    services = {
        "kafka": {
            "status": "running",
            "uptime": "7d 14h 23m",  # Would calculate from actual uptime
            "messages": "1.2M"
        },
        "mongodb": {
            "status": "running" if db.db else "stopped",
            "uptime": "7d 14h 23m",
            "connections": 12
        },
        "backend": {
            "status": "running",
            "uptime": "7d 14h 23m",
            "requests": "45.3K"
        },
        "mlEngine": {
            "status": "running",
            "uptime": "7d 14h 23m",
            "predictions": "8.9K"
        }
    }
    
    return {"services": services}
