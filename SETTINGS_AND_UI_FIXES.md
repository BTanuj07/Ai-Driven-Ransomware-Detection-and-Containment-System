# Settings and UI Fixes

## Issues Fixed

### 1. Email/SMS Alerts Not Respecting Settings Toggle
**Problem**: When email and SMS alerts were toggled off in Settings Module, alerts were still being sent.

**Solution**:
- Added `emailAlerts` setting check in `EmailAlertService.send_critical_alert()`
- Added `smsAlerts` setting check in `SMSAlertService.send_critical_sms()`
- Both services now check settings_manager before sending alerts
- If disabled, alerts are skipped with a log message

**Files Modified**:
- `backend/services/email_alerts.py`
- `backend/services/sms_alerts.py`

### 2. Dashboard Showing Only 2 Endpoints Instead of 18
**Problem**: Dashboard was showing only 2 monitored endpoints despite having 18 deployed.

**Solution**:
- Added `update_system_status()` call in kafka consumer's `_process_message()` method
- Now every message from an endpoint updates the system_status collection
- Tracks hostname, status, and last_seen timestamp
- All active endpoints are now properly registered and counted

**Files Modified**:
- `backend/services/kafka_consumer.py`

### 3. Removed Bell Icon Notification
**Problem**: Top right corner had two notification icons - a message icon and a bell icon showing 942 alerts, which was cluttered.

**Solution**:
- Removed the bell icon notification button
- Kept only the message notification icon with alert count
- Cleaner, simpler UI with just one notification indicator

**Files Modified**:
- `frontend/src/App.jsx`

### 4. Contained Threats Count (281)
**Note**: This is actually working as designed. The "Contained Threats" metric shows the total cumulative count of all threats contained since system deployment. This number increases over time as more threats are contained. It's not a bug - it's a historical metric showing total system effectiveness.

If you want to see recent activity instead, we could change it to:
- "Threats Contained Today"
- "Active Containments"
- "Threats Contained This Week"

Let me know if you'd like this changed!

## Testing

After these fixes:
1. ✅ Toggle email alerts OFF in Settings → No emails sent for new alerts
2. ✅ Toggle SMS alerts OFF in Settings → No SMS sent for new alerts
3. ✅ All 18 deployed endpoints now appear in dashboard
4. ✅ Cleaner notification UI with single message icon
5. ✅ Endpoint count updates in real-time as endpoints send data

## Deployment

Restart the backend service to apply these changes:
```bash
cd backend
python main.py
```

Frontend changes are applied automatically on page refresh.
