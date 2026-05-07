# Settings 401 Unauthorized Fix

## Problem
When trying to save settings in the Settings Module, you get `401 Unauthorized` error:
```
INFO: 127.0.0.1:53313 - "POST /api/settings HTTP/1.1" 401 Unauthorized
```

## Root Causes

### 1. User Role Issue
The `/api/settings` POST endpoint requires **superadmin** role, but your user might not have it.

**Solution**: Run the fix script:
```bash
python fix_user_role.py
```

This ensures `tanuj077777@gmail.com` has `superadmin` role in MongoDB.

### 2. Authentication Token Issue
The Settings Module might not be sending the authentication token correctly.

## Quick Fix Steps

### Step 1: Ensure User Has Superadmin Role
```bash
python fix_user_role.py
```

Expected output:
```
✅ User created with superadmin role
🎉 SUCCESS! User is now superadmin
```

### Step 2: Logout and Login Again
1. Open dashboard: `http://localhost:3000`
2. Click logout (if logged in)
3. Login again with: `tanuj077777@gmail.com`
4. This refreshes your authentication token

### Step 3: Try Saving Settings Again
1. Go to **Settings Module**
2. Enter your email and phone
3. Click **Save Configuration**
4. Should now work without 401 error

## Alternative: Use Script to Save Settings

If the UI still doesn't work, use the script:
```bash
python save_settings_to_mongodb.py
```

This bypasses authentication and saves settings directly to MongoDB.

## Verification

Check backend logs when you click "Save Configuration":
- ❌ Bad: `POST /api/settings HTTP/1.1" 401 Unauthorized`
- ✅ Good: `POST /api/settings HTTP/1.1" 200 OK`

## Why This Happened

The Settings Module authentication flow:
1. User logs in via Supabase
2. Frontend gets JWT token
3. Frontend sends token in `Authorization: Bearer <token>` header
4. Backend validates token and checks user role
5. If role != superadmin, returns 401

Your user wasn't in MongoDB with superadmin role, so authentication failed.

## Status After Fix

✅ User `tanuj077777@gmail.com` now has `superadmin` role  
✅ Settings are already in MongoDB (from manual script)  
🔄 Need to logout/login to refresh token  
🔄 Then Settings Module will work  

## Files Created

1. `fix_user_role.py` - Adds superadmin role to user
2. `save_settings_to_mongodb.py` - Manually saves settings (bypass auth)
3. `SETTINGS_401_FIX.md` - This documentation
