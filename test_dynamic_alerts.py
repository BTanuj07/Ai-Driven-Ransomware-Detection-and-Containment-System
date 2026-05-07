"""
Test script to verify dynamic email and SMS alerts from Settings module
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Add backend to path
sys.path.insert(0, 'backend')

from services.settings_manager import SettingsManager
from services.email_alerts import EmailAlertService
from services.sms_alerts import SMSAlertService

def test_dynamic_alerts():
    """Test that alerts use email/phone from settings manager"""
    
    print("=" * 60)
    print("TESTING DYNAMIC EMAIL AND SMS ALERTS")
    print("=" * 60)
    
    # Create settings manager
    settings_manager = SettingsManager()
    
    # Simulate settings from Settings module
    test_email = "tanuj077777@gmail.com"
    test_phone = "+919353938326"
    
    print(f"\n1. Setting custom email: {test_email}")
    print(f"2. Setting custom phone: {test_phone}")
    
    settings_manager.update({
        'emailAddress': test_email,
        'phoneNumber': test_phone
    })
    
    # Create alert services with settings manager
    email_service = EmailAlertService(settings_manager)
    sms_service = SMSAlertService(settings_manager)
    
    # Verify email service is using settings
    admin_email = email_service._get_admin_email()
    print(f"\n✓ Email service will send to: {admin_email}")
    
    if admin_email == test_email:
        print("  ✅ Email service correctly using Settings module email")
    else:
        print(f"  ❌ Email service using wrong email: {admin_email}")
    
    # Verify SMS service is using settings
    admin_phone = sms_service._get_admin_phone()
    print(f"\n✓ SMS service will send to: {admin_phone}")
    
    if admin_phone == test_phone:
        print("  ✅ SMS service correctly using Settings module phone")
    else:
        print(f"  ❌ SMS service using wrong phone: {admin_phone}")
    
    # Create test alert
    test_alert = {
        "hostname": "TEST-ENDPOINT-01",
        "endpoint": "TEST-ENDPOINT-01",
        "attack_type": "Ransomware Encryption",
        "risk_level": "CRITICAL",
        "risk_score": 0.95,
        "anomaly_score": 0.88,
        "message": "Test alert for dynamic recipient verification",
        "details": "This is a test alert to verify dynamic email/SMS recipients"
    }
    
    print("\n" + "=" * 60)
    print("SENDING TEST ALERTS")
    print("=" * 60)
    
    # Test email
    print(f"\n📧 Sending test email to: {admin_email}")
    email_sent = email_service.send_critical_alert(test_alert)
    
    if email_sent:
        print("  ✅ Email sent successfully!")
    else:
        print("  ❌ Email failed to send")
    
    # Test SMS
    print(f"\n📱 Sending test SMS to: {admin_phone}")
    sms_sent = sms_service.send_critical_sms(test_alert)
    
    if sms_sent:
        print("  ✅ SMS sent successfully!")
    else:
        print("  ❌ SMS failed to send")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nCheck your email and phone for test alerts!")
    print(f"Email: {admin_email}")
    print(f"Phone: {admin_phone}")

if __name__ == "__main__":
    test_dynamic_alerts()
