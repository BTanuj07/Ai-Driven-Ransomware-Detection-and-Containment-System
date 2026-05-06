# Real-Time Settings Implementation

## Overview
All settings in the Settings Module now work in real-time. Changes apply immediately without requiring a backend restart.

## What Was Implemented

### 1. Settings Manager Service (`backend/services/settings_manager.py`)
- **Singleton pattern** - ensures all components use the same settings instance
- **Real-time updates** - settings changes apply immediately across all services
- **Database integration** - loads settings from MongoDB on startup
- **Thread-safe** - uses locks to prevent race conditions

### 2. Updated Components

#### Risk Scorer (`backend/services/risk_scorer.py`)
- Now uses `settings_manager` instead of static `config`
- Risk thresholds (HIGH, MEDIUM, LOW) are read dynamically
- Changes to thresholds apply to next alert immediately

#### Response Engine (`backend/services/response_engine.py`)
- Checks settings before executing containment actions
- Respects toggle states:
  - `autoIsolate` - controls network isolation
  - `autoKillProcess` - controls process termination
  - `autoDisableUser` - controls user account disabling
  - `requireApproval` - blocks automatic actions if enabled

#### Settings API (`backend/api/settings_routes.py`)
- Updates settings manager when settings are saved
- Changes propagate immediately to all services
- Logs all setting changes for audit trail

#### Main Application (`backend/main.py`)
- Initializes settings manager on startup
- Loads settings from database into memory

## Settings That Work in Real-Time

### Detection Thresholds
1. **Anomaly Score Threshold** (0-100%)
   - Minimum score to trigger anomaly detection
   - Default: 75%

2. **HIGH Risk Threshold** (0-100%)
   - Score above this = HIGH risk classification
   - Default: 80%
   - Affects: Alert severity, containment actions

3. **MEDIUM Risk Threshold** (0-100%)
   - Score above this = MEDIUM risk classification
   - Default: 60%
   - Affects: Alert severity, response actions

4. **LOW Risk Threshold** (0-100%)
   - Score above this = LOW risk classification
   - Default: 40%
   - Affects: Alert filtering

5. **False Positive Sensitivity** (0-100%)
   - Higher values reduce false positives
   - Default: 65%

6. **Model Confidence Threshold** (0-100%)
   - Minimum ML model confidence to trigger alerts
   - Default: 85%

### Automated Response Policy
1. **Auto-Isolate Endpoint** (Toggle)
   - Automatically isolate infected endpoints from network
   - Default: ON
   - Effect: Immediate - next HIGH risk alert will/won't isolate

2. **Auto-Kill Suspicious Process** (Toggle)
   - Terminate processes identified as malicious
   - Default: ON
   - Effect: Immediate - next alert will/won't kill process

3. **Auto-Disable User Account** (Toggle)
   - Disable compromised user accounts automatically
   - Default: OFF
   - Effect: Immediate - next HIGH risk alert will/won't disable user

4. **Require Admin Approval** (Toggle)
   - Require manual approval before executing response actions
   - Default: ON
   - Effect: Immediate - next containment will wait for approval

### Notification Settings
1. **Email Alerts** (Toggle)
   - Send email notifications for critical alerts
   - Default: ON

2. **SMS Alerts** (Toggle)
   - Send SMS notifications for critical alerts
   - Default: OFF

3. **Critical Escalation** (Toggle)
   - Escalate critical alerts to management
   - Default: ON

## How It Works

### Flow Diagram
```
User Changes Setting in UI
         ↓
Frontend sends POST /api/settings
         ↓
Backend updates MongoDB
         ↓
Backend updates settings_manager (in-memory)
         ↓
Next alert/detection uses new settings
         ↓
Immediate effect - no restart needed
```

### Example: Changing HIGH Risk Threshold

1. **Before**: HIGH threshold = 80%
   - Alert with score 0.75 = MEDIUM risk
   
2. **User changes** HIGH threshold to 70%

3. **After**: HIGH threshold = 70%
   - Alert with score 0.75 = HIGH risk
   - Triggers more aggressive containment

4. **No restart required** - change applies immediately

### Example: Disabling Auto-Isolation

1. **Before**: Auto-Isolate = ON
   - HIGH risk alert → Network isolation executed
   
2. **User toggles** Auto-Isolate to OFF

3. **After**: Auto-Isolate = OFF
   - HIGH risk alert → Network isolation skipped
   - Other actions (kill process) still execute

4. **Immediate effect** - next alert respects new setting

## Testing Real-Time Settings

### Test 1: Change Risk Threshold
```bash
# 1. Set HIGH threshold to 90% in Settings UI
# 2. Run ransomware simulation
python simulation/ransomware_simulator.py
# 3. Check alerts - should see fewer HIGH risk alerts
# 4. Set HIGH threshold to 50%
# 5. Run simulation again
# 6. Check alerts - should see more HIGH risk alerts
```

### Test 2: Toggle Auto-Isolation
```bash
# 1. Enable Auto-Isolate in Settings UI
# 2. Run simulation
# 3. Check backend logs - should see "ISOLATE: Network isolation enabled"
# 4. Disable Auto-Isolate
# 5. Run simulation again
# 6. Check backend logs - should NOT see isolation message
```

### Test 3: Require Approval
```bash
# 1. Enable "Require Admin Approval" in Settings UI
# 2. Run simulation
# 3. Check backend logs - should see "PENDING_APPROVAL: Awaiting admin authorization"
# 4. Disable "Require Admin Approval"
# 5. Run simulation again
# 6. Check backend logs - should see containment actions executed
```

## Technical Details

### Settings Manager Singleton
```python
# All components use the same instance
from services.settings_manager import settings_manager

# Get current threshold
threshold = settings_manager.high_risk_threshold

# Check if auto-isolation is enabled
if settings_manager.auto_isolate:
    isolate_endpoint()
```

### Thread Safety
- Uses `threading.Lock()` to prevent race conditions
- Safe for concurrent access from multiple threads
- Kafka consumer and API handlers can access simultaneously

### Database Persistence
- Settings stored in MongoDB `settings` collection
- Loaded on backend startup
- Updated on every settings change
- Survives backend restarts

## Benefits

1. **No Downtime** - Change settings without restarting backend
2. **Immediate Effect** - Changes apply to next alert/detection
3. **Audit Trail** - All changes logged with user and timestamp
4. **Consistent** - All services use same settings instance
5. **Persistent** - Settings survive restarts

## Future Enhancements

1. **WebSocket Notifications** - Notify frontend when settings change
2. **Setting Profiles** - Save/load different setting configurations
3. **Scheduled Settings** - Auto-adjust thresholds based on time of day
4. **A/B Testing** - Compare effectiveness of different thresholds
5. **ML-Based Tuning** - Auto-adjust thresholds based on false positive rate

## Troubleshooting

### Settings Not Applying
1. Check backend logs for "Settings manager initialized"
2. Verify MongoDB connection is working
3. Check audit logs to confirm settings were saved
4. Restart backend if settings manager didn't initialize

### Inconsistent Behavior
1. Ensure only one backend instance is running
2. Check MongoDB for conflicting settings documents
3. Verify settings_manager is imported correctly in all services

### Settings Reset on Restart
1. Check MongoDB connection - settings must be persisted
2. Verify `update_settings()` is saving to database
3. Check for errors in database service logs
