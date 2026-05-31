"""
TOTP MFA Service
Handles Time-based One-Time Password authentication
"""

import pyotp
import qrcode
import io
import base64
from typing import Tuple, Optional
from datetime import datetime


class TOTPService:
    """Service for TOTP-based Multi-Factor Authentication"""
    
    def __init__(self):
        self.issuer_name = "ARCS Security"
    
    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret for a user
        
        Returns:
            Base32-encoded secret string
        """
        return pyotp.random_base32()
    
    def get_provisioning_uri(self, email: str, secret: str) -> str:
        """
        Generate provisioning URI for QR code
        
        Args:
            email: User's email address
            secret: TOTP secret
            
        Returns:
            otpauth:// URI for authenticator apps
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=self.issuer_name
        )
    
    def generate_qr_code(self, provisioning_uri: str) -> str:
        """
        Generate QR code image as base64 string
        
        Args:
            provisioning_uri: otpauth:// URI
            
        Returns:
            Base64-encoded PNG image
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_token(self, secret: str, token: str) -> bool:
        """
        Verify TOTP token
        
        Args:
            secret: User's TOTP secret
            token: 6-digit code from authenticator app
            
        Returns:
            True if token is valid, False otherwise
        """
        if not token or len(token) != 6:
            return False
        
        try:
            totp = pyotp.TOTP(secret)
            # Verify with 1-step window (30 seconds before/after)
            return totp.verify(token, valid_window=1)
        except Exception as e:
            print(f"TOTP verification error: {e}")
            return False
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """
        Generate backup codes for account recovery
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            List of backup codes
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = pyotp.random_base32()[:8]
            codes.append(code)
        return codes
    
    def get_current_token(self, secret: str) -> str:
        """
        Get current TOTP token (for testing)
        
        Args:
            secret: TOTP secret
            
        Returns:
            Current 6-digit token
        """
        totp = pyotp.TOTP(secret)
        return totp.now()


# Singleton instance
totp_service = TOTPService()
