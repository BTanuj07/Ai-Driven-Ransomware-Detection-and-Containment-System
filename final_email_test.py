"""
Final comprehensive email test
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

import requests

def main():
    print("\n🔍 FINAL EMAIL DIAGNOSTIC")
    print("=" * 60)
    
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('ALERT_FROM_EMAIL', 'alerts@arcs-security.com')
    to_email = os.getenv('ADMIN_EMAIL')
    
    print(f"\n📧 Configuration:")
    print(f"   API Key: {api_key[:15]}...{api_key[-10:]}")
    print(f"   From: {from_email}")
    print(f"   To: {to_email}")
    
    # Use requests library directly
    print(f"\n📤 Sending email via REST API...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'personalizations': [
            {
                'to': [{'email': to_email}],
                'subject': 'ARCS Test Email'
            }
        ],
        'from': {'email': from_email},
        'content': [
            {
                'type': 'text/html',
                'value': '<p>This is a test email from ARCS system.</p>'
            }
        ]
    }
    
    try:
        response = requests.post(
            'https://api.sendgrid.com/v3/mail/send',
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 202:
            print(f"\n✅ EMAIL SENT SUCCESSFULLY!")
            print(f"   SendGrid accepted the email")
            print(f"   Check your inbox: {to_email}")
            print(f"   Also check spam/junk folder")
            print(f"\n   If you don't receive it:")
            print(f"   - Check SendGrid Activity: https://app.sendgrid.com/activity")
            print(f"   - Verify sender: https://app.sendgrid.com/settings/sender_auth")
            
        elif response.status_code == 401:
            print(f"\n❌ 401 UNAUTHORIZED")
            print(f"   Response: {response.text}")
            
            # Check if it's a permission issue
            if 'permission' in response.text.lower():
                print(f"\n💡 SOLUTION: API Key Permission Issue")
                print(f"   Your API key doesn't have 'Mail Send' permission")
                print(f"   Steps:")
                print(f"   1. Go to: https://app.sendgrid.com/settings/api_keys")
                print(f"   2. Delete the current key")
                print(f"   3. Create NEW key with these settings:")
                print(f"      - Name: ARCS-Mail-Send")
                print(f"      - Permission: Full Access (or Mail Send)")
                print(f"   4. Copy the key")
                print(f"   5. Update backend/.env")
            else:
                print(f"\n💡 SOLUTION: Invalid API Key")
                print(f"   The API key is not recognized by SendGrid")
                print(f"   Create a completely new API key")
                
        elif response.status_code == 403:
            print(f"\n❌ 403 FORBIDDEN")
            print(f"   Response: {response.text}")
            print(f"\n💡 SOLUTION: Sender Not Verified")
            print(f"   1. Go to: https://app.sendgrid.com/settings/sender_auth")
            print(f"   2. Verify sender: {from_email}")
            
        else:
            print(f"\n⚠️  Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
