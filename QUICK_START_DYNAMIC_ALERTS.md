# Quick Start: Dynamic Email & SMS Alerts

## What Changed?
Email and SMS alerts now use the email/phone you configure in the **Settings Module** instead of hardcoded values.

## Setup (3 Steps)

### 1. Start the System
```bash
# Start backend
python backend/main.py

# In another terminal, start frontend
cd frontend
npm run dev
```

### 2. Configure Recipients
1. Open dashboard: `http://localhost:3000`
2. Login with your credentials
3. Click **Settings** in sidebar
4. Scroll to **Notification Settings**
5. Enter your email: `tanuj077777@gmail.com`
6. Enter your phone: `+919353938326`
7. Click **Save Configuration**

### 3. Test It
```bash
# Test with script
python test_dynamic_alerts.py

# Or trigger real attack
python trigger_docker_attack.py
```

## Expected Behavior

### Email Alerts
- **When**: Risk ≥ 85% or HIGH/CRITICAL level
- **To**: Email from Settings Module
- **Fallback**: `.env` ADMIN_EMAIL if not configured

### SMS Alerts
- **When**: Risk ≥ 90% or CRITICAL ransomware
- **To**: Phone from Settings Module
- **Fallback**: `.env` ADMIN_PHONE_NUMBER if not configured

## Verify It's Working

Run test script:
```bash
python test_dynamic_alerts.py
```

Look for:
```
✅ Email service correctly using Settings module email
✅ SMS service correctly using Settings module phone
✅ Email sent successfully!
✅ SMS sent successfully!
```

## Troubleshooting

### Alerts still going to old email?
1. Check Settings Module shows your email
2. Click **Save Configuration** again
3. Wait 5 seconds for settings to sync
4. Try again

### No email received?
1. Check SendGrid API key in `backend/.env`
2. Verify SendGrid account has credits
3. Check spam folder
4. Run: `python diagnose_sendgrid.py`

### No SMS received?
1. Check Twilio credentials in `backend/.env`
2. Verify phone number format: `+919353938326`
3. Check Twilio account balance
4. Run: `python test_sms_quick.py`

## Files to Check

- **Settings UI**: `frontend/src/components/SettingsModule.jsx`
- **Email Service**: `backend/services/email_alerts.py`
- **SMS Service**: `backend/services/sms_alerts.py`
- **Settings Manager**: `backend/services/settings_manager.py`

## Key Features

✅ Real-time updates (no restart needed)  
✅ Configure via dashboard (no file editing)  
✅ Fallback to .env if not configured  
✅ Persistent in MongoDB  
✅ Audit logging of changes  

## Status
🎉 **WORKING** - Tested and verified!
