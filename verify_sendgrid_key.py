"""
Verify SendGrid API Key Permissions
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

import requests

def main():
    print("\n🔍 SENDGRID API KEY VERIFICATION")
    print("=" * 60)
    
    api_key = os.getenv('SENDGRID_API_KEY')
    
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"\n🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Format: {'✅ Valid' if api_key.startswith('SG.') else '❌ Invalid'}")
    
    # Test API key by checking scopes
    print(f"\n🌐 Testing API Key with SendGrid...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Try to get API key info
    try:
        response = requests.get(
            'https://api.sendgrid.com/v3/scopes',
            headers=headers,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            scopes = response.json().get('scopes', [])
            print(f"   ✅ API Key is VALID!")
            print(f"   Permissions: {len(scopes)} scopes")
            
            # Check for mail.send permission
            if 'mail.send' in scopes or 'mail.send.full' in scopes:
                print(f"   ✅ Has 'mail.send' permission")
            else:
                print(f"   ❌ Missing 'mail.send' permission")
                print(f"   Available scopes: {', '.join(scopes[:5])}...")
                
        elif response.status_code == 401:
            print(f"   ❌ API Key is INVALID or EXPIRED")
            print(f"   Response: {response.text}")
            print(f"\n💡 This API key has been:")
            print(f"   - Deleted from SendGrid")
            print(f"   - Expired")
            print(f"   - Never properly created")
            print(f"\n   You MUST create a NEW API key:")
            print(f"   1. Go to: https://app.sendgrid.com/settings/api_keys")
            print(f"   2. Click 'Create API Key'")
            print(f"   3. Name: ARCS-Email-Alerts")
            print(f"   4. Permission: Full Access")
            print(f"   5. Copy the key (shown only once!)")
            print(f"   6. Update backend/.env")
            
        elif response.status_code == 403:
            print(f"   ❌ API Key lacks permissions")
            print(f"   Create new key with 'Mail Send' permission")
            
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
            print(f"   Body: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network error: {e}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    main()
