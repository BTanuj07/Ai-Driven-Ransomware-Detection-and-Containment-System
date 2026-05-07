# Dynamic Alert Recipients Implementation

## Overview
Email and SMS alerts now use the email address and phone number configured in the **Settings Module** instead of hardcoded values from the `.env` file.

## Changes Made

### 1. Email Alert Service (`backend/services/email_alerts.py`)
- **Added `settings_manager` parameter** to `__init__()`
- **Added `_get_admin_email()` method** that:
  - First checks settings manager for `emailAddress`
  - Falls back to `.env` `ADMIN_EMAIL` if not configured
  - Ignores default placeholder value `admin@arcs.local`
- **Updated `send_critical_alert()`** to use `_get_admin_email()` dynamically
- **Updated `send_daily_summary()`** to use `_get_admin_email()` dynamically

### 2. SMS Alert Service (`backend/services/sms_alerts.py`)
- **Added `settings_manager` parameter** to `__init__()`
- **Added `_get_admin_phone()` method** that:
  - First checks settings manager for `phoneNumber`
  - Falls back to `.env` `ADMIN_PHONE_NUMBER` if not configured
  - Ignores default placeholder value `+1 (555) 123-4567`
- **Updated `send_critical_sms()`** to use `_get_admin_phone()` dynamically
- **Updated `send_test_sms()`** to use `_get_admin_phone()` as fallback

### 3. Kafka Consumer Service (`backend/services/kafka_consumer.py`)
- **Removed global imports** of `email_service` and `sms_service`
- **Created instances** of `EmailAlertService` and `SMSAlertService` in `__init__()`
- **Passed `settings_manager`** to both alert service constructors
- **Updated alert sending** to use `self.email_service` and `self.sms_service`

### 4. Settings Manager (`backend/services/settings_manager.py`)
- Already had `emailAddress` and `phoneNumber` in default settings
- These values are updated when user saves settings in the Settings Module

## How It Works

### Flow:
1. User opens **Settings Module** in the dashboard
2. User enters their email address and phone number
3. User clicks **Save Settings**
4. Settings are saved to MongoDB via `/api/settings` endpoint
5. `SettingsManager` singleton is updated with new values
6. When an alert is triggered:
   - `EmailAlertService._get_admin_email()` reads from settings manager
   - `SMSAlertService._get_admin_phone()` reads from settings manager
   - Alerts are sent to the configured recipients

### Fallback Behavior:
- If no email/phone is configured in Settings Module, falls back to `.env` values
- If `.env` values are also missing, uses safe defaults
- Placeholder values like `admin@arcs.local` are ignored

## Testing

### Test Script: `test_dynamic_alerts.py`
Run this script to verify dynamic recipients:

```bash
python test_dynamic_alerts.py
```

This will:
1. Create a settings manager
2. Set custom email and phone
3. Verify alert services read the correct values
4. Send test email and SMS to configured recipients

### Manual Testing:
1. Start the backend: `python backend/main.py`
2. Open dashboard: `http://localhost:3000`
3. Go to **Settings Module**
4. Enter your email and phone number
5. Click **Save Settings**
6. Run attack simulation: `python trigger_docker_attack.py`
7. Check that alerts arrive at the configured email/phone

## Configuration

### Settings Module Fields:
- **Email Address**: Where critical email alerts are sent (risk ≥ 85%)
- **Phone Number**: Where ultra-critical SMS alerts are sent (risk ≥ 90%)

### Alert Thresholds:
- **Email**: Risk score ≥ 0.85 (85%) or risk level = HIGH/CRITICAL
- **SMS**: Risk score ≥ 0.90 (90%) or CRITICAL + ransomware keywords

## Benefits

✅ **Real-time updates**: Change recipients without restarting backend  
✅ **User-friendly**: Configure via dashboard instead of editing `.env`  
✅ **Secure**: No need to expose `.env` file to users  
✅ **Flexible**: Different recipients for different deployments  
✅ **Fallback safe**: Always has a working default  

## Files Modified

1. `backend/services/email_alerts.py`
2. `backend/services/sms_alerts.py`
3. `backend/services/kafka_consumer.py`
4. `test_dynamic_alerts.py` (new)
5. `DYNAMIC_ALERT_RECIPIENTS.md` (new)

## Status

✅ **COMPLETE** - Email and SMS alerts now use Settings Module configuration
