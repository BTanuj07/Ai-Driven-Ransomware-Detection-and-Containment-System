"""
Diagnose SendGrid Configuration
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

def main():
    print("\n🔍 SENDGRID CONFIGURATION DIAGNOSTIC")
    print("=" * 60)
    
    # Get configuration
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('ALERT_FROM_EMAIL', 'alerts@arcs-security.com')
    admin_email = os.getenv('ADMIN_EMAIL')
    
    print(f"\n📧 Configuration:")
    print(f"   API Key: {api_key[:20]}...{api_key[-10:] if api_key and len(api_key) > 30 else 'TOO SHORT'}")
    print(f"   From Email: {from_email}")
    print(f"   Admin Email: {admin_email}")
    
    # Check API key format
    print(f"\n🔑 API Key Validation:")
    if not api_key:
        print("   ❌ API key is empty")
        return
    
    if not api_key.startswith('SG.'):
        print(f"   ❌ API key should start with 'SG.' but starts with '{api_key[:3]}'")
        print("   This is likely an invalid API key")
        return
    else:
        print("   ✅ API key format looks correct (starts with 'SG.')")
    
    if len(api_key) < 50:
        print(f"   ⚠️  API key seems short ({len(api_key)} chars). SendGrid keys are usually 69+ chars")
    else:
        print(f"   ✅ API key length looks good ({len(api_key)} chars)")
    
    # Test API connection
    print(f"\n🌐 Testing SendGrid API Connection...")
    try:
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        
        # Try to send a test email
        message = Mail(
            from_email=Email(from_email),
            to_emails=To(admin_email),
            subject="ARCS Test Email",
            html_content=Content("text/html", "<p>This is a test email from ARCS</p>")
        )
        
        response = sg.send(message)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            print("   ✅ EMAIL SENT SUCCESSFULLY!")
            print(f"   Check your inbox: {admin_email}")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
            print(f"   Response: {response.body}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ ERROR: {error_msg}")
        
        if "401" in error_msg or "Unauthorized" in error_msg:
            print("\n💡 SOLUTION:")
            print("   Your API key is invalid or expired.")
            print("   Steps to fix:")
            print("   1. Go to https://app.sendgrid.com/settings/api_keys")
            print("   2. Create a NEW API key")
            print("   3. Give it 'Mail Send' permission (Full Access recommended)")
            print("   4. Copy the key (you'll only see it once!)")
            print("   5. Update backend/.env:")
            print("      SENDGRID_API_KEY=SG.your_new_key_here")
            print("   6. Restart backend and test again")
        elif "403" in error_msg or "Forbidden" in error_msg:
            print("\n💡 SOLUTION:")
            print("   Your API key doesn't have permission to send emails.")
            print("   Create a new API key with 'Mail Send' permission.")
        elif "from_email" in error_msg.lower() or "sender" in error_msg.lower():
            print("\n💡 SOLUTION:")
            print("   Your sender email is not verified.")
            print("   Steps to fix:")
            print("   1. Go to https://app.sendgrid.com/settings/sender_auth")
            print("   2. Verify a Single Sender")
            print("   3. Use that email as ALERT_FROM_EMAIL in backend/.env")

if __name__ == "__main__":
    main()
