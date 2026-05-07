# Email & SMS Alert Setup Guide

## Overview
ARCS supports two types of critical alert notifications:
- **Email Alerts** (via SendGrid) - For critical threats (risk score ≥ 85%)
- **SMS Alerts** (via Twilio) - For ultra-critical threats (risk score ≥ 90%)

## Prerequisites

### For Email Alerts
- SendGrid account (free tier available)
- Verified sender email address
- SendGrid API key

### For SMS Alerts
- Twilio account (trial available)
- Twilio phone number
- Account SID and Auth Token

## Setup Instructions

### 1. Email Alerts Setup (SendGrid)

#### Step 1: Create SendGrid Account
1. Go to https://sendgrid.com
2. Sign up for free account
3. Verify your email address

#### Step 2: Create API Key
1. Log in to SendGrid dashboard
2. Go to Settings → API Keys
3. Click "Create API Key"
4. Name: `ARCS-Alerts`
5. Permissions: Select "Full Access" or "Mail Send"
6. Click "Create & View"
7. **Copy the API key** (you won't see it again!)

#### Step 3: Verify Sender Email
1. Go to Settings → Sender Authentication
2. Click "Verify a Single Sender"
3. Fill in your details:
   - From Name: `ARCS Security`
   - From Email: `alerts@yourdomain.com` (or your email)
   - Reply To: Your email
4. Check your email and click verification link

#### Step 4: Update Configuration
Edit `backend/.env`:
```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ALERT_FROM_EMAIL=alerts@yourdomain.com
ADMIN_EMAIL=your_email@example.com
```

#### Step 5: Test Email Alerts
```bash
python test_email_alerts.py
```

### 2. SMS Alerts Setup (Twilio)

#### Step 1: Create Twilio Account
1. Go to https://www.twilio.com
2. Sign up for free trial
3. Verify your phone number

#### Step 2: Get Phone Number
1. Log in to Twilio console
2. Go to Phone Numbers → Manage → Buy a number
3. Select a number (trial gives you $15 credit)
4. Purchase the number

#### Step 3: Get Credentials
1. Go to Twilio Console Dashboard
2. Find "Account Info" section
3. Copy:
   - Account SID
   - Auth Token

#### Step 4: Verify Recipient Number (Trial Only)
If using trial account:
1. Go to Phone Numbers → Manage → Verified Caller IDs
2. Add your phone number
3. Enter verification code sent via SMS

#### Step 5: Update Configuration
Edit `backend/.env`:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
ADMIN_PHONE_NUMBER=+1234567890
```

**Important**: Phone numbers must be in E.164 format: `+[country code][number]`
- US: `+12025551234`
- India: `+919876543210`
- UK: `+447700900123`

#### Step 6: Test SMS Alerts
```bash
python test_sms_alerts.py
```

## Alert Thresholds

### Email Alerts
Triggered when:
- Risk score ≥ 85% (0.85)
- OR Risk level = "CRITICAL"
- OR Attack type contains: ransomware, encryption, mass_deletion, lateral_movement

**Cooldown**: 1 hour (same alert won't be sent again for 1 hour)

### SMS Alerts
Triggered when:
- Risk score ≥ 90% (0.90)
- OR Risk level = "CRITICAL" AND attack type is ultra-dangerous

**Cooldown**: 2 hours (longer than email to avoid SMS spam)

## Testing

### Test Email Alerts
```bash
# Run test suite
python test_email_alerts.py

# Expected output:
# ✅ Configuration check
# ✅ Send test email
# ✅ Deduplication test
```

### Test SMS Alerts
```bash
# Run test suite
python test_sms_alerts.py

# Expected output:
# ✅ Configuration check
# ✅ Send test SMS
# ✅ Threshold test
# ✅ Deduplication test
```

### Test with Real Simulation
```bash
# Run ransomware simulation
python trigger_docker_attack.py

# Expected:
# - Email alert sent (if risk ≥ 85%)
# - SMS alert sent (if risk ≥ 90%)
# - Check your email and phone
```

## Troubleshooting

### Email Alerts Not Working

#### Issue: "HTTP Error 401: Unauthorized"
**Solution**: Invalid SendGrid API key
```bash
# Check API key in backend/.env
# Make sure it starts with "SG."
# Create new API key if needed
```

#### Issue: Email not received
**Solutions**:
1. Check spam/junk folder
2. Verify sender email in SendGrid
3. Check SendGrid Activity Feed for delivery status
4. Verify ADMIN_EMAIL is correct

#### Issue: "Email service not configured"
**Solution**: Check backend/.env has all required fields:
```env
SENDGRID_API_KEY=SG.xxxxx (not placeholder)
ALERT_FROM_EMAIL=alerts@yourdomain.com
ADMIN_EMAIL=your_email@example.com
```

### SMS Alerts Not Working

#### Issue: "Unable to create record: 'From' +XXX is not a Twilio phone number"
**Solution**: 
1. Verify TWILIO_PHONE_NUMBER matches your Twilio number
2. Check phone number format: `+1234567890` (no spaces or dashes)
3. Make sure you purchased/activated the number in Twilio

#### Issue: "HTTP Error 401"
**Solution**: Invalid Twilio credentials
```bash
# Check Account SID and Auth Token
# They should match Twilio console exactly
```

#### Issue: SMS not received
**Solutions**:
1. Check phone number format (E.164: +[country][number])
2. For trial accounts: Verify recipient number in Twilio console
3. Check Twilio console logs for delivery status
4. Verify sufficient balance (trial gives $15)

#### Issue: "Twilio client not initialized"
**Solution**: Check backend/.env has all required fields:
```env
TWILIO_ACCOUNT_SID=ACxxxxx (not placeholder)
TWILIO_AUTH_TOKEN=your_token (not placeholder)
TWILIO_PHONE_NUMBER=+1234567890 (not placeholder)
ADMIN_PHONE_NUMBER=+1234567890 (your phone)
```

## Cost Considerations

### SendGrid (Email)
- **Free Tier**: 100 emails/day forever
- **Essentials**: $19.95/month for 50,000 emails
- **Pro**: $89.95/month for 100,000 emails

For ARCS: Free tier is usually sufficient (few critical alerts per day)

### Twilio (SMS)
- **Trial**: $15 credit (can send ~500 SMS)
- **Pay-as-you-go**: $0.0075 per SMS (US)
- **International**: Varies by country

For ARCS: Trial is good for testing, then pay-as-you-go for production

## Security Best Practices

### 1. Protect API Keys
```bash
# Never commit .env file to git
# Add to .gitignore
echo "backend/.env" >> .gitignore

# Use environment variables in production
export SENDGRID_API_KEY="SG.xxxxx"
export TWILIO_AUTH_TOKEN="xxxxx"
```

### 2. Rotate Keys Regularly
- Rotate SendGrid API key every 90 days
- Rotate Twilio Auth Token every 90 days
- Update backend/.env after rotation

### 3. Monitor Usage
- Check SendGrid Activity Feed daily
- Check Twilio console for unusual activity
- Set up usage alerts in both services

### 4. Rate Limiting
ARCS has built-in rate limiting:
- Email: Max 1 per hour per alert type
- SMS: Max 1 per 2 hours per alert type

## Advanced Configuration

### Custom Email Template
Edit `backend/services/email_alerts.py`:
```python
def _format_email_content(self, alert: Dict) -> str:
    # Customize HTML template here
    html_content = f"""
    <html>
    <!-- Your custom template -->
    </html>
    """
    return html_content
```

### Custom SMS Message
Edit `backend/services/sms_alerts.py`:
```python
def _format_sms_message(self, alert: Dict) -> str:
    # Customize SMS message (160 chars max)
    message = f"Your custom message"
    return message
```

### Adjust Thresholds
Edit service files:
```python
# Email threshold (default: 0.85)
self.critical_threshold = 0.80  # Lower = more emails

# SMS threshold (default: 0.90)
self.ultra_critical_threshold = 0.95  # Higher = fewer SMS
```

### Adjust Cooldown Periods
```python
# Email cooldown (default: 1 hour)
self.cooldown_period = timedelta(hours=2)

# SMS cooldown (default: 2 hours)
self.cooldown_period = timedelta(hours=4)
```

## Integration with Settings Module

Alerts can be enabled/disabled from the Settings module:

1. Navigate to Settings in dashboard
2. Find "Notification Settings" section
3. Toggle:
   - Email Alerts (ON/OFF)
   - SMS Alerts (ON/OFF)
   - Critical Escalation (ON/OFF)

These settings are stored in MongoDB and apply in real-time.

## Monitoring & Logs

### Check Backend Logs
```bash
# Backend terminal shows alert status
✅ Alert saved to database: 69ee14edf41b2a90b1ce1d9f
🚨 ALERT: HIGH risk on BEAST (score: 0.97)
📧 Critical alert email sent successfully: BEAST:Ransomware
📱 Critical SMS sent successfully: BEAST:Ransomware (SID: SMxxxxx)
```

### Check Service Dashboards
- **SendGrid**: https://app.sendgrid.com/activity
- **Twilio**: https://console.twilio.com/monitor/logs/sms

## Support

### SendGrid Support
- Docs: https://docs.sendgrid.com
- Support: https://support.sendgrid.com

### Twilio Support
- Docs: https://www.twilio.com/docs
- Support: https://support.twilio.com

## Quick Reference

### Test Commands
```bash
# Test email
python test_email_alerts.py

# Test SMS
python test_sms_alerts.py

# Test with simulation
python trigger_docker_attack.py
```

### Configuration Files
```
backend/.env          # Main configuration
backend/services/email_alerts.py   # Email service
backend/services/sms_alerts.py     # SMS service
```

### Environment Variables
```env
# Email
SENDGRID_API_KEY=SG.xxxxx
ALERT_FROM_EMAIL=alerts@domain.com
ADMIN_EMAIL=admin@domain.com

# SMS
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890
ADMIN_PHONE_NUMBER=+1234567890
```
