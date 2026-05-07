"""
Quick SMS Alert Test - No user input required
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('backend/.env')

from services.sms_alerts import SMSAlertService

def main():
    print("\n🧪 QUICK SMS ALERT TEST")
    print("=" * 60)
    
    # Check configuration
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    admin_phone = os.getenv('ADMIN_PHONE_NUMBER')
    
    print(f"\n📱 Twilio Account SID: {'✅ Set' if account_sid and account_sid != 'your_twilio_account_sid_here' else '❌ Not set'}")
    print(f"📱 Admin Phone: {admin_phone}")
    
    if not account_sid or account_sid == 'your_twilio_account_sid_here':
        print("\n❌ Twilio not configured")
        return
    
    # Initialize service
    sms_service = SMSAlertService()
    
    # Create ultra-critical test alert
    test_alert = {
        'endpoint': 'TEST-MACHINE',
        'hostname': 'TEST-MACHINE',
        'attack_type': 'Test Ransomware',
        'risk_score': 0.95,
        'risk_level': 'CRITICAL',
        'anomaly_score': -0.9,
        'timestamp': datetime.now().isoformat(),
        'message': 'This is a test SMS alert from ARCS'
    }
    
    print(f"\n📱 Sending test SMS to {admin_phone}...")
    print(f"   Attack Type: {test_alert['attack_type']}")
    print(f"   Risk Score: {test_alert['risk_score']}")
    
    # Send SMS
    try:
        success = sms_service.send_critical_sms(test_alert)
        
        if success:
            print("\n✅ SMS SENT SUCCESSFULLY!")
            print(f"   Check your phone: {admin_phone}")
            print("   Message: 🚨 CRITICAL ALERT...")
        else:
            print("\n❌ FAILED TO SEND SMS")
            print("   Check backend logs for details")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
