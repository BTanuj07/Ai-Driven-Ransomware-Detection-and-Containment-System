# Users Module Error - Troubleshooting Guide

## Quick Diagnostics

### Step 1: Check Browser Console
1. Press **F12** to open Developer Tools
2. Go to **Console** tab
3. Navigate to Users page
4. Look for error messages (usually in red)

### Common Errors and Solutions:

#### Error: "Failed to load users"
**Cause**: Backend API not responding or CORS issue

**Solution**:
1. Make sure backend is running:
   ```bash
   cd backend
   python main.py
   ```
2. Check backend is on: http://localhost:8000
3. Test API directly: http://localhost:8000/api/users

#### Error: "Authentication required"
**Cause**: No auth token or expired session

**Solution**:
1. Log out and log back in
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try in incognito window

#### Error: "Supabase not configured"
**Cause**: Backend can't find Supabase credentials

**Solution**:
1. Verify `backend/.env` has:
   ```
   SUPABASE_URL=https://hsbcjonzbnwjnftfohyk.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
   ```
2. **Restart backend** (important!)
   ```bash
   # Stop backend (Ctrl+C)
   # Start again
   python main.py
   ```

#### Error: "Network Error" or "ERR_CONNECTION_REFUSED"
**Cause**: Backend not running

**Solution**:
```bash
cd backend
python main.py
```

#### Error: "CORS policy" or "Access-Control-Allow-Origin"
**Cause**: CORS not configured properly

**Solution**: Check `backend/main.py` has CORS middleware

---

## Step 2: Test Backend API Directly

### Test 1: Check Backend Health
Open in browser: http://localhost:8000/docs

You should see FastAPI Swagger documentation.

### Test 2: Test Users Endpoint
1. Go to: http://localhost:8000/docs
2. Find `/api/users` endpoint
3. Click "Try it out"
4. Click "Execute"
5. Check response

**Expected**: List of users
**If error**: Check backend logs

---

## Step 3: Check Backend Logs

Look at your backend terminal for errors:

### Good Output:
```
✅ Connected to MongoDB Atlas (Cloud)
✅ Settings reloaded from database
✅ Ensemble model loaded
ARCS Backend started successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Bad Output (Supabase issue):
```
⚠️  Warning: Supabase credentials not configured for user management
```

**Solution**: Restart backend after adding credentials to `.env`

---

## Step 4: Check Frontend API Client

The frontend calls: `http://localhost:8000/api/users`

### Verify API URL:
1. Open `frontend/src/lib/api.js`
2. Check `baseURL` is set to: `http://localhost:8000`

---

## Step 5: Restart Everything

Sometimes a clean restart fixes everything:

### Stop Everything:
```bash
# Stop backend (Ctrl+C in backend terminal)
# Stop frontend (Ctrl+C in frontend terminal)
```

### Start Backend:
```bash
cd backend
python main.py
```

Wait for: "ARCS Backend started successfully"

### Start Frontend:
```bash
cd frontend
npm run dev
```

Wait for: "Local: http://localhost:5173"

### Test Again:
1. Go to: http://localhost:5173/login
2. Log in
3. Go to Users page
4. Should load successfully ✅

---

## Step 6: Check Permissions

Make sure you're logged in as **superadmin**:

1. Check your role in top-right corner
2. Should say "superadmin"
3. If not, update your role in Supabase:
   - Go to Supabase Dashboard
   - Authentication → Users
   - Find your user
   - Edit user metadata
   - Add: `{"role": "superadmin"}`

---

## Step 7: Test with cURL

Test the API directly from command line:

```bash
# Get your auth token first (from browser console):
# localStorage.getItem('supabase.auth.token')

curl -X GET "http://localhost:8000/api/users" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected**: JSON with users list
**If error**: Check backend logs

---

## Common Issues Summary

| Error | Cause | Solution |
|-------|-------|----------|
| "Failed to load users" | Backend not running | Start backend |
| "Authentication required" | No token | Log out and log in |
| "Supabase not configured" | Missing .env | Add credentials, restart |
| "Network Error" | Backend down | Start backend |
| "CORS error" | CORS not configured | Check main.py |
| Blank page | JavaScript error | Check browser console |
| "Access Denied" | Wrong role | Update role to superadmin |

---

## Quick Fix Checklist

- [ ] Backend is running on http://localhost:8000
- [ ] Frontend is running on http://localhost:5173
- [ ] `backend/.env` has SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
- [ ] Backend was restarted after adding .env variables
- [ ] You're logged in as superadmin
- [ ] Browser console shows no errors
- [ ] http://localhost:8000/docs loads successfully

---

## Still Not Working?

### Get Detailed Error Info:

1. **Open Browser Console** (F12)
2. **Go to Network tab**
3. **Navigate to Users page**
4. **Look for failed requests** (red)
5. **Click on the failed request**
6. **Check Response tab**
7. **Copy the error message**

### Share This Info:
- Error message from console
- Error message from Network tab
- Backend terminal output
- Your role (from top-right corner)

---

## Expected Behavior

When working correctly:

1. Navigate to Users page
2. See "Loading users..." briefly
3. See user list with:
   - Total users count
   - Active accounts count
   - User table with emails and roles
4. If superadmin: See "Create User" form
5. If not superadmin: See "Super Admin access required" message

---

**Most Common Fix**: Restart backend after adding Supabase credentials to `.env`

```bash
cd backend
# Ctrl+C to stop
python main.py  # Start again
```
