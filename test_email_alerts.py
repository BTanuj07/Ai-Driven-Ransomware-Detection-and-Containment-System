"""
Test Email Alerts - SendGrid Integration
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Load environment variables from backend/.env
from dotenv import load_dotenv
load_dotenv('backend/.env')

from services.email_alerts import EmailAlertService

def test_email_configuration():
    """Test if email service is properly configured"""
    print("=" * 60)
    print("EMAIL ALERT CONFIGURATION TEST")
    print("=" * 60)
    
    # Check environment variables
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('ALERT_FROM_EMAIL', 'alerts@arcs-security.com')
    admin_email = os.getenv('ADMIN_EMAIL')
    
    print(f"\n📧 SendGrid API Key: {'✅ Set' if api_key and api_key != 'your_sendgrid_api_key_here' else '❌ Not set or placeholder'}")
    print(f"📧 From Email: {from_email}")
    print(f"📧 Admin Email: {'✅ ' + admin_email if admin_email and admin_email != 'your_admin_email@example.com' else '❌ Not set or placeholder'}")
    
    if not api_key or api_key == 'your_sendgrid_api_key_here':
        print("\n⚠️  WARNING: SendGrid API key not configured!")
        print("   To configure:")
        print("   1. Sign up at https://sendgrid.com")
        print("   2. Create an API key")
        print("   3. Update backend/.env:")
        print("      SENDGRID_API_KEY=your_actual_api_key")
        print("      ADMIN_EMAIL=your_email@example.com")
        return False
    
    return True

def test_send_email():
    """Test sending an actual email alert"""
    print("\n" + "=" * 60)
    print("SENDING TEST EMAIL ALERT")
    print("=" * 60)
    
    # Initialize email service
    email_service = EmailAlertService()
    
    # Create test alert
    test_alert = {
        'endpoint': 'TEST-MACHINE',
        'hostname': 'TEST-MACHINE',
        'attack_type': 'Test Ransomware Simulation',
        'risk_score': 0.95,  # High enough to trigger email
        'risk_level': 'HIGH',
        'anomaly_score': -0.8,
        'timestamp': datetime.now().isoformat(),
        'message': 'This is a test alert from ARCS system',
        'details': 'Testing email alert functionality. If you receive this, email alerts are working correctly!'
    }
    
    print(f"\n📧 Sending test alert...")
    print(f"   Endpoint: {test_alert['endpoint']}")
    print(f"   Attack Type: {test_alert['attack_type']}")
    print(f"   Risk Score: {test_alert['risk_score']}")
    print(f"   Risk Level: {test_alert['risk_level']}")
    
    # Send email
    success = email_service.send_critical_alert(test_alert)
    
    if success:
        print("\n✅ EMAIL SENT SUCCESSFULLY!")
        print(f"   Check your inbox: {os.getenv('ADMIN_EMAIL')}")
        print("   Subject: 🚨 CRITICAL ALERT: Test Ransomware Simulation on TEST-MACHINE")
        print("\n   If you don't see it:")
        print("   - Check spam/junk folder")
        print("   - Verify email address in backend/.env")
        print("   - Check SendGrid dashboard for delivery status")
    else:
        print("\n❌ FAILED TO SEND EMAIL")
        print("   Possible reasons:")
        print("   - Invalid SendGrid API key")
        print("   - Email address not verified")
        print("   - SendGrid account not activated")
        print("   - Network connectivity issues")
    
    return success

def test_email_deduplication():
    """Test that duplicate emails are not sent"""
    print("\n" + "=" * 60)
    print("TESTING EMAIL DEDUPLICATION")
    print("=" * 60)
    
    email_service = EmailAlertService()
    
    test_alert = {
        'endpoint': 'DEDUP-TEST',
        'attack_type': 'Deduplication Test',
        'risk_score': 0.90,
        'risk_level': 'HIGH',
        'timestamp': datetime.now().isoformat(),
        'message': 'Testing deduplication'
    }
    
    print("\n📧 Sending first email...")
    first_send = email_service.send_critical_alert(test_alert)
    print(f"   Result: {'✅ Sent' if first_send else '❌ Not sent'}")
    
    print("\n📧 Sending duplicate email (should be blocked)...")
    second_send = email_service.send_critical_alert(test_alert)
    print(f"   Result: {'❌ Sent (dedup failed!)' if second_send else '✅ Blocked (dedup working)'}")
    
    if not second_send:
        print("\n✅ DEDUPLICATION WORKING CORRECTLY")
        print("   Same alert won't be sent again for 1 hour")
    else:
        print("\n⚠️  DEDUPLICATION NOT WORKING")
    
    return not second_send

def main():
    print("\n🧪 ARCS EMAIL ALERT TESTING SUITE")
    print("=" * 60)
    
    # Test 1: Configuration
    config_ok = test_email_configuration()
    
    if not config_ok:
        print("\n❌ Email service not configured. Please set up SendGrid credentials.")
        return
    
    # Test 2: Send email
    input("\n⏸️  Press Enter to send test email...")
    send_ok = test_send_email()
    
    if not send_ok:
        print("\n❌ Email sending failed. Check configuration and try again.")
        return
    
    # Test 3: Deduplication
    input("\n⏸️  Press Enter to test deduplication...")
    dedup_ok = test_email_deduplication()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Configuration: {'✅ Pass' if config_ok else '❌ Fail'}")
    print(f"Email Sending: {'✅ Pass' if send_ok else '❌ Fail'}")
    print(f"Deduplication: {'✅ Pass' if dedup_ok else '❌ Fail'}")
    
    if config_ok and send_ok and dedup_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Email alerts are working correctly.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("   Review the output above for details.")

if __name__ == "__main__":
    main()
