"""
MFA API Routes
Endpoints for TOTP Multi-Factor Authentication
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from services.totp_service import totp_service
from services.database import DatabaseService

router = APIRouter()


class MFASetupRequest(BaseModel):
    user_id: str


class MFAVerifyRequest(BaseModel):
    user_id: str
    token: str


class MFAEnableRequest(BaseModel):
    user_id: str
    token: str


class MFADisableRequest(BaseModel):
    user_id: str
    token: str


@router.post("/mfa/setup")
async def setup_mfa(request: Request, body: MFASetupRequest):
    """
    Generate TOTP secret and QR code for MFA setup
    
    Returns:
        - secret: TOTP secret (store securely)
        - qr_code: Base64 QR code image
        - backup_codes: Recovery codes
    """
    try:
        db: DatabaseService = request.app.state.db
        
        # Generate TOTP secret
        secret = totp_service.generate_secret()
        
        # Get user email from Supabase
        # For now, use user_id as email (you can fetch from Supabase)
        email = body.user_id
        
        # Generate provisioning URI
        provisioning_uri = totp_service.get_provisioning_uri(email, secret)
        
        # Generate QR code
        qr_code = totp_service.generate_qr_code(provisioning_uri)
        
        # Generate backup codes
        backup_codes = totp_service.generate_backup_codes()
        
        # Store in MongoDB (temporary, not enabled yet)
        db.db.mfa_setup.update_one(
            {"user_id": body.user_id},
            {
                "$set": {
                    "user_id": body.user_id,
                    "secret": secret,
                    "backup_codes": backup_codes,
                    "enabled": False,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {
            "status": "success",
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "message": "Scan QR code with Google Authenticator or Microsoft Authenticator"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MFA setup failed: {str(e)}")


@router.post("/mfa/enable")
async def enable_mfa(request: Request, body: MFAEnableRequest):
    """
    Enable MFA after verifying initial token
    
    Args:
        user_id: User ID
        token: 6-digit TOTP code
    """
    try:
        db: DatabaseService = request.app.state.db
        
        # Get MFA setup data
        mfa_data = db.db.mfa_setup.find_one({"user_id": body.user_id})
        
        if not mfa_data:
            raise HTTPException(status_code=404, detail="MFA not set up. Call /mfa/setup first")
        
        # Verify token
        is_valid = totp_service.verify_token(mfa_data["secret"], body.token)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid TOTP code")
        
        # Enable MFA
        db.db.mfa_setup.update_one(
            {"user_id": body.user_id},
            {
                "$set": {
                    "enabled": True,
                    "enabled_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "status": "success",
            "message": "MFA enabled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable MFA: {str(e)}")


@router.post("/mfa/verify")
async def verify_mfa(request: Request, body: MFAVerifyRequest):
    """
    Verify TOTP token during login
    
    Args:
        user_id: User ID
        token: 6-digit TOTP code
    """
    try:
        db: DatabaseService = request.app.state.db
        
        # Get MFA data
        mfa_data = db.db.mfa_setup.find_one({"user_id": body.user_id, "enabled": True})
        
        if not mfa_data:
            raise HTTPException(status_code=404, detail="MFA not enabled for this user")
        
        # Verify token
        is_valid = totp_service.verify_token(mfa_data["secret"], body.token)
        
        if not is_valid:
            # Check if it's a backup code
            if body.token in mfa_data.get("backup_codes", []):
                # Remove used backup code
                db.db.mfa_setup.update_one(
                    {"user_id": body.user_id},
                    {"$pull": {"backup_codes": body.token}}
                )
                is_valid = True
            else:
                raise HTTPException(status_code=400, detail="Invalid TOTP code or backup code")
        
        # Log successful verification
        db.db.mfa_logs.insert_one({
            "user_id": body.user_id,
            "action": "verify",
            "success": True,
            "timestamp": datetime.utcnow()
        })
        
        return {
            "status": "success",
            "message": "MFA verification successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MFA verification failed: {str(e)}")


@router.post("/mfa/disable")
async def disable_mfa(request: Request, body: MFADisableRequest):
    """
    Disable MFA (requires current TOTP code)
    
    Args:
        user_id: User ID
        token: 6-digit TOTP code
    """
    try:
        db: DatabaseService = request.app.state.db
        
        # Get MFA data
        mfa_data = db.db.mfa_setup.find_one({"user_id": body.user_id, "enabled": True})
        
        if not mfa_data:
            raise HTTPException(status_code=404, detail="MFA not enabled")
        
        # Verify token before disabling
        is_valid = totp_service.verify_token(mfa_data["secret"], body.token)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid TOTP code")
        
        # Disable MFA
        db.db.mfa_setup.update_one(
            {"user_id": body.user_id},
            {
                "$set": {
                    "enabled": False,
                    "disabled_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "status": "success",
            "message": "MFA disabled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable MFA: {str(e)}")


@router.get("/mfa/status/{user_id}")
async def get_mfa_status(request: Request, user_id: str):
    """
    Check if MFA is enabled for a user
    
    Args:
        user_id: User ID
    """
    try:
        db: DatabaseService = request.app.state.db
        
        mfa_data = db.db.mfa_setup.find_one({"user_id": user_id})
        
        if not mfa_data:
            return {
                "enabled": False,
                "message": "MFA not set up"
            }
        
        return {
            "enabled": mfa_data.get("enabled", False),
            "setup_date": mfa_data.get("enabled_at"),
            "backup_codes_remaining": len(mfa_data.get("backup_codes", []))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get MFA status: {str(e)}")


@router.post("/mfa/regenerate-backup-codes")
async def regenerate_backup_codes(request: Request, body: MFAVerifyRequest):
    """
    Regenerate backup codes (requires TOTP verification)
    
    Args:
        user_id: User ID
        token: 6-digit TOTP code
    """
    try:
        db: DatabaseService = request.app.state.db
        
        # Get MFA data
        mfa_data = db.db.mfa_setup.find_one({"user_id": body.user_id, "enabled": True})
        
        if not mfa_data:
            raise HTTPException(status_code=404, detail="MFA not enabled")
        
        # Verify token
        is_valid = totp_service.verify_token(mfa_data["secret"], body.token)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid TOTP code")
        
        # Generate new backup codes
        new_backup_codes = totp_service.generate_backup_codes()
        
        # Update in database
        db.db.mfa_setup.update_one(
            {"user_id": body.user_id},
            {
                "$set": {
                    "backup_codes": new_backup_codes,
                    "backup_codes_regenerated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "status": "success",
            "backup_codes": new_backup_codes,
            "message": "Backup codes regenerated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate backup codes: {str(e)}")
