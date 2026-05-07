# Fix 401 Unauthorized Errors - Quick Guide

## Problem
Reports and Risk Overview modules showing 401 (Unauthorized) errors after code changes.

## Root Cause
Frontend needs to be restarted after we updated the authentication code. The old JavaScript bundle is still running in the browser.

## Solution (3 Steps)

### Step 1: Restart Frontend
```bash
# In your frontend terminal, press Ctrl+C to stop
# Then restart:
cd frontend
npm run dev
```

**Wait for**: `➜  Local:   http://localhost:3000/`

### Step 2: Hard Refresh Browser
```
Press: Ctrl + Shift + R
(Or Cmd + Shift + R on Mac)
```

This clears the cached JavaScript and loads the new code.

### Step 3: Log Out and Log In
1. Click your profile icon (top right)
2. Click "Sign Out"
3. Log in again with your credentials

## Why This Happens

### Before Restart
```
Browser → Old JavaScript (window.supabase not set)
         → No auth token
         → 401 Unauthorized
```

### After Restart
```
Browser → New JavaScript (window.supabase exposed)
         → Gets auth token from Supabase
         → Passes token to backend
         → ✅ Success
```

## Verify It's Fixed

### Test 1: Check Browser Console
1. Press F12
2. Go to Console tab
3. Should see NO 401 errors
4. Should see successful API calls

### Test 2: Check Reports Module
1. Navigate to Reports
2. Should see data (not zeros)
3. Should see charts and tables
4. No error messages

### Test 3: Check Risk Overview
1. Navigate to Risk Overview
2. Should see risk scores
3. Should see endpoint list
4. Should see trend charts

## Still Getting 401 Errors?

### Check 1: Supabase Session
Open browser console and run:
```javascript
window.supabase.auth.getSession().then(({data}) => console.log(data.session))
```

**Expected**: Should show session object with `access_token`  
**If null**: Log out and log in again

### Check 2: Frontend Code Loaded
Open browser console and run:
```javascript
console.log(window.supabase)
```

**Expected**: Should show Supabase client object  
**If undefined**: Frontend not restarted properly

### Check 3: Backend Running
```powershell
curl http://localhost:8000/
```

**Expected**: `{"service":"ARCS Backend","status":"running","version":"1.0.0"}`  
**If error**: Backend not running

## 500 Internal Server Errors

If you see 500 errors instead of 401:

### Check Backend Terminal
Look for error messages like:
- Database connection errors
- Missing collections
- Python exceptions

### Common 500 Causes
1. **MongoDB not connected**: Check backend logs for connection errors
2. **Missing data**: Run simulation to generate alerts
3. **Code errors**: Check backend terminal for Python tracebacks

### Fix MongoDB Issues
```bash
# Test MongoDB connection
python check_mongodb.py

# If connection fails, check backend/.env
# Verify MONGODB_URL is correct
```

## Reports Showing Zero

If authentication works but reports show zero:

### Cause
No data in MongoDB yet - you need to generate some alerts first.

### Solution
```bash
# Run ransomware simulation
cd simulation
python ransomware_simulator.py

# Wait for alerts to be generated
# Then refresh Reports module
```

### Verify Data Exists
```powershell
curl http://localhost:8000/api/alerts?limit=5
```

Should return alerts in JSON format.

## Complete Restart Procedure

If nothing works, do a complete restart:

### 1. Stop Everything
- Press Ctrl+C in backend terminal
- Press Ctrl+C in frontend terminal

### 2. Start Backend
```bash
cd backend
python main.py
```

Wait for: `ARCS Backend started successfully`

### 3. Start Frontend
```bash
cd frontend
npm run dev
```

Wait for: `Local: http://localhost:3000/`

### 4. Clear Browser
- Close all browser tabs with ARCS
- Clear browser cache (Ctrl+Shift+Delete)
- Open new tab to http://localhost:3000

### 5. Fresh Login
- Log in with your credentials
- Navigate to Reports
- Should work now

## Prevention

### Always Restart After Code Changes
When you modify:
- Authentication code
- API client configuration
- Supabase integration
- Any frontend JavaScript

You MUST restart the frontend dev server.

### Use the Diagnostic Script
```powershell
.\diagnose_auth_issue.ps1
```

This will check:
- Backend status
- Frontend status
- API endpoints
- Supabase configuration
- Common issues

## Quick Reference

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | No auth token | Restart frontend, log in again |
| 500 Internal Server | Backend error | Check backend logs |
| Reports show zero | No data | Run simulation |
| Undefined values | Old code cached | Hard refresh (Ctrl+Shift+R) |
| window.supabase undefined | Frontend not restarted | Restart frontend |

## Need More Help?

1. Run diagnostic script: `.\diagnose_auth_issue.ps1`
2. Check browser console (F12)
3. Check backend terminal for errors
4. Check frontend terminal for errors
5. Verify MongoDB connection
6. Test API endpoints directly with curl
