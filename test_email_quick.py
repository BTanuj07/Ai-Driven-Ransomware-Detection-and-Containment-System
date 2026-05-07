"""
Quick Email Alert Test - No user input required
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

from services.email_alerts import EmailAlertService

def main():
    print("\n🧪 QUICK EMAIL ALERT TEST")
    print("=" * 60)
    
    # Check configuration
    api_key = os.getenv('SENDGRID_API_KEY')
    admin_email = os.getenv('ADMIN_EMAIL')
    
    print(f"\n📧 SendGrid API Key: {'✅ Set' if api_key and api_key != 'your_sendgrid_api_key_here' else '❌ Not set'}")
    print(f"📧 Admin Email: {admin_email}")
    
    if not api_key or api_key == 'your_sendgrid_api_key_here':
        print("\n❌ SendGrid not configured")
        return
    
    # Initialize service
    email_service = EmailAlertService()
    
    # Create test alert
    test_alert = {
        'endpoint': 'TEST-MACHINE',
        'hostname': 'TEST-MACHINE',
        'attack_type': 'Test Ransomware Simulation',
        'risk_score': 0.95,
        'risk_level': 'HIGH',
        'anomaly_score': -0.8,
        'timestamp': datetime.now().isoformat(),
        'message': 'This is a test alert from ARCS system',
        'details': 'Testing email alert functionality'
    }
    
    print(f"\n📧 Sending test email to {admin_email}...")
    print(f"   Attack Type: {test_alert['attack_type']}")
    print(f"   Risk Score: {test_alert['risk_score']}")
    
    # Send email
    try:
        success = email_service.send_critical_alert(test_alert)
        
        if success:
            print("\n✅ EMAIL SENT SUCCESSFULLY!")
            print(f"   Check your inbox: {admin_email}")
            print("   Subject: 🚨 CRITICAL ALERT: Test Ransomware Simulation on TEST-MACHINE")
        else:
            print("\n❌ FAILED TO SEND EMAIL")
            print("   Check backend logs for details")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
