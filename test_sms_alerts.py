"""
Test SMS Alerts - Twilio Integration
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

from services.sms_alerts import SMSAlertService

def test_sms_configuration():
    """Test if SMS service is properly configured"""
    print("=" * 60)
    print("SMS ALERT CONFIGURATION TEST")
    print("=" * 60)
    
    # Check environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_phone = os.getenv('TWILIO_PHONE_NUMBER')
    admin_phone = os.getenv('ADMIN_PHONE_NUMBER')
    
    print(f"\n📱 Twilio Account SID: {'✅ Set' if account_sid and account_sid != 'your_twilio_account_sid_here' else '❌ Not set or placeholder'}")
    print(f"📱 Twilio Auth Token: {'✅ Set' if auth_token and auth_token != 'your_twilio_auth_token_here' else '❌ Not set or placeholder'}")
    print(f"📱 From Phone: {from_phone if from_phone != '+1234567890' else '❌ Placeholder'}")
    print(f"📱 Admin Phone: {admin_phone if admin_phone != '+1234567890' else '❌ Placeholder'}")
    
    if not account_sid or account_sid == 'your_twilio_account_sid_here':
        print("\n⚠️  WARNING: Twilio credentials not configured!")
        print("   To configure:")
        print("   1. Sign up at https://www.twilio.com")
        print("   2. Get a phone number")
        print("   3. Get Account SID and Auth Token from console")
        print("   4. Update backend/.env:")
        print("      TWILIO_ACCOUNT_SID=your_account_sid")
        print("      TWILIO_AUTH_TOKEN=your_auth_token")
        print("      TWILIO_PHONE_NUMBER=+1234567890")
        print("      ADMIN_PHONE_NUMBER=+1234567890")
        return False
    
    return True

def test_send_sms():
    """Test sending an actual SMS alert"""
    print("\n" + "=" * 60)
    print("SENDING TEST SMS ALERT")
    print("=" * 60)
    
    # Initialize SMS service
    sms_service = SMSAlertService()
    
    # Create ultra-critical test alert (SMS requires higher threshold)
    test_alert = {
        'endpoint': 'TEST-MACHINE',
        'hostname': 'TEST-MACHINE',
        'attack_type': 'Test Ransomware',
        'risk_score': 0.95,  # Must be 90%+ for SMS
        'risk_level': 'CRITICAL',
        'anomaly_score': -0.9,
        'timestamp': datetime.now().isoformat(),
        'message': 'This is a test SMS alert from ARCS system'
    }
    
    print(f"\n📱 Sending test SMS...")
    print(f"   Endpoint: {test_alert['endpoint']}")
    print(f"   Attack Type: {test_alert['attack_type']}")
    print(f"   Risk Score: {test_alert['risk_score']}")
    print(f"   Risk Level: {test_alert['risk_level']}")
    print(f"   To: {os.getenv('ADMIN_PHONE_NUMBER')}")
    
    # Send SMS
    success = sms_service.send_critical_sms(test_alert)
    
    if success:
        print("\n✅ SMS SENT SUCCESSFULLY!")
        print(f"   Check your phone: {os.getenv('ADMIN_PHONE_NUMBER')}")
        print("   Message preview:")
        print("   🚨 CRITICAL ALERT")
        print("   Endpoint: TEST-MACHINE")
        print("   Threat: Test Ransomware")
        print("   Risk: 95%")
        print("   Action: Containment initiated")
        print("   Check dashboard immediately")
        print("\n   If you don't receive it:")
        print("   - Verify phone number format (+1234567890)")
        print("   - Check Twilio phone number is verified")
        print("   - Check Twilio console for delivery status")
    else:
        print("\n❌ FAILED TO SEND SMS")
        print("   Possible reasons:")
        print("   - Invalid Twilio credentials")
        print("   - Phone number not verified")
        print("   - Insufficient Twilio balance")
        print("   - Phone number format incorrect")
        print("   - Network connectivity issues")
    
    return success

def test_sms_threshold():
    """Test that low-risk alerts don't trigger SMS"""
    print("\n" + "=" * 60)
    print("TESTING SMS THRESHOLD")
    print("=" * 60)
    
    sms_service = SMSAlertService()
    
    # Low risk alert (should NOT send SMS)
    low_risk_alert = {
        'endpoint': 'THRESHOLD-TEST',
        'attack_type': 'Low Risk Test',
        'risk_score': 0.70,  # Below 90% threshold
        'risk_level': 'MEDIUM',
        'timestamp': datetime.now().isoformat()
    }
    
    print("\n📱 Testing low-risk alert (should NOT send SMS)...")
    print(f"   Risk Score: {low_risk_alert['risk_score']} (below 90% threshold)")
    
    low_risk_sent = sms_service.send_critical_sms(low_risk_alert)
    
    if not low_risk_sent:
        print("   ✅ Correctly blocked (not ultra-critical)")
    else:
        print("   ❌ SMS sent (threshold not working!)")
    
    # High risk alert (should send SMS)
    high_risk_alert = {
        'endpoint': 'THRESHOLD-TEST',
        'attack_type': 'High Risk Test',
        'risk_score': 0.95,  # Above 90% threshold
        'risk_level': 'CRITICAL',
        'timestamp': datetime.now().isoformat()
    }
    
    print("\n📱 Testing high-risk alert (should send SMS)...")
    print(f"   Risk Score: {high_risk_alert['risk_score']} (above 90% threshold)")
    
    high_risk_sent = sms_service.send_critical_sms(high_risk_alert)
    
    if high_risk_sent:
        print("   ✅ SMS sent (ultra-critical)")
    else:
        print("   ❌ SMS not sent (threshold not working!)")
    
    return not low_risk_sent and high_risk_sent

def test_sms_deduplication():
    """Test that duplicate SMS are not sent"""
    print("\n" + "=" * 60)
    print("TESTING SMS DEDUPLICATION")
    print("=" * 60)
    
    sms_service = SMSAlertService()
    
    test_alert = {
        'endpoint': 'DEDUP-TEST-SMS',
        'attack_type': 'Deduplication Test',
        'risk_score': 0.95,
        'risk_level': 'CRITICAL',
        'timestamp': datetime.now().isoformat()
    }
    
    print("\n📱 Sending first SMS...")
    first_send = sms_service.send_critical_sms(test_alert)
    print(f"   Result: {'✅ Sent' if first_send else '❌ Not sent'}")
    
    print("\n📱 Sending duplicate SMS (should be blocked)...")
    second_send = sms_service.send_critical_sms(test_alert)
    print(f"   Result: {'❌ Sent (dedup failed!)' if second_send else '✅ Blocked (dedup working)'}")
    
    if not second_send:
        print("\n✅ DEDUPLICATION WORKING CORRECTLY")
        print("   Same alert won't be sent again for 2 hours")
    else:
        print("\n⚠️  DEDUPLICATION NOT WORKING")
    
    return not second_send

def main():
    print("\n🧪 ARCS SMS ALERT TESTING SUITE")
    print("=" * 60)
    
    # Test 1: Configuration
    config_ok = test_sms_configuration()
    
    if not config_ok:
        print("\n❌ SMS service not configured. Please set up Twilio credentials.")
        return
    
    # Test 2: Send SMS
    input("\n⏸️  Press Enter to send test SMS...")
    send_ok = test_send_sms()
    
    if not send_ok:
        print("\n❌ SMS sending failed. Check configuration and try again.")
        return
    
    # Test 3: Threshold
    input("\n⏸️  Press Enter to test SMS threshold...")
    threshold_ok = test_sms_threshold()
    
    # Test 4: Deduplication
    input("\n⏸️  Press Enter to test deduplication...")
    dedup_ok = test_sms_deduplication()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Configuration: {'✅ Pass' if config_ok else '❌ Fail'}")
    print(f"SMS Sending: {'✅ Pass' if send_ok else '❌ Fail'}")
    print(f"Threshold: {'✅ Pass' if threshold_ok else '❌ Fail'}")
    print(f"Deduplication: {'✅ Pass' if dedup_ok else '❌ Fail'}")
    
    if config_ok and send_ok and threshold_ok and dedup_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("   SMS alerts are working correctly.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("   Review the output above for details.")

if __name__ == "__main__":
    main()
