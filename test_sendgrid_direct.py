"""
Test SendGrid directly with minimal code
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

import sendgrid
from sendgrid.helpers.mail import Mail

def main():
    print("\n🧪 DIRECT SENDGRID TEST")
    print("=" * 60)
    
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('ALERT_FROM_EMAIL', 'alerts@arcs-security.com')
    to_email = os.getenv('ADMIN_EMAIL')
    
    print(f"\n📧 Configuration:")
    print(f"   From: {from_email}")
    print(f"   To: {to_email}")
    
    try:
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject='ARCS Test Email',
            html_content='<p>This is a test email from ARCS system.</p>'
        )
        
        print(f"\n📤 Sending email...")
        response = sg.send(message)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201, 202]:
            print(f"\n✅ EMAIL SENT SUCCESSFULLY!")
            print(f"   Check your inbox: {to_email}")
            print(f"   Also check spam/junk folder")
        else:
            print(f"\n⚠️  Unexpected status: {response.status_code}")
            print(f"   Body: {response.body}")
            
    except Exception as e:
        error_str = str(e)
        print(f"\n❌ ERROR: {error_str}")
        
        if "The from email does not contain a valid address" in error_str:
            print(f"\n💡 SOLUTION:")
            print(f"   Your sender email '{from_email}' is not verified.")
            print(f"   Steps:")
            print(f"   1. Go to: https://app.sendgrid.com/settings/sender_auth")
            print(f"   2. Click 'Verify a Single Sender'")
            print(f"   3. Use email: {to_email}")
            print(f"   4. Check email and verify")
            print(f"   5. Update backend/.env:")
            print(f"      ALERT_FROM_EMAIL={to_email}")
        elif "401" in error_str:
            print(f"\n💡 API key issue (but we verified it works...)")
            print(f"   Try creating a fresh API key")

if __name__ == "__main__":
    main()
