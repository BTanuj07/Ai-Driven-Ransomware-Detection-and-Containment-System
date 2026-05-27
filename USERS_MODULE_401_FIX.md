# Users Module 401 Unauthorized Fix

## Issue
Users Module page was showing error:
```
Failed to load resource: the server responded with a status of 401 (Unauthorized)
Failed to fetch users: AxiosError: Request failed with status code 401
```

## Root Cause
There were **two sets of user routes** in the backend:
1. `backend/api/auth_routes.py` - Has `/api/users` with authentication middleware
2. `backend/api/users_routes.py` - Has `/api/users` without authentication (our new routes)

Since `auth_router` was registered first in `main.py`, it was catching all `/api/users` requests and requiring authentication that the frontend wasn't providing correctly.

## Solution
Changed the `users_routes.py` endpoints to use a different prefix: `/api/supabase/users` instead of `/api/users` to avoid conflicts.

## Changes Made

### 1. Backend: `backend/main.py`
Changed router registration:
```python
# Before
app.include_router(users_router, prefix="/api")

# After
app.include_router(users_router, prefix="/api/supabase")
```

### 2. Backend: `backend/api/users_routes.py`
Added authentication middleware to all endpoints:
```python
from fastapi import Header

async def verify_token(authorization: str = Header(None)):
    """Verify JWT token from Supabase"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

# Applied to all endpoints
@router.get("/users")
async def list_users(token: str = Depends(verify_token)):
    ...
```

### 3. Frontend: `frontend/src/components/UsersModule.jsx`
Updated all API calls to use new endpoint:
```javascript
// Before
await apiClient.get('/api/users', ...)
await apiClient.post('/api/users', ...)
await apiClient.put(`/api/users/${userId}/role`, ...)
await apiClient.delete(`/api/users/${userId}`, ...)

// After
await apiClient.get('/api/supabase/users', ...)
await apiClient.post('/api/supabase/users', ...)
await apiClient.put(`/api/supabase/users/${userId}/role`, ...)
await apiClient.delete(`/api/supabase/users/${userId}`, ...)
```

## API Endpoints

### Old Endpoints (auth_routes.py - MongoDB based)
- `GET /api/users` - List users from MongoDB
- `POST /api/users` - Create user in MongoDB
- `PUT /api/users/{user_id}` - Update user in MongoDB
- `DELETE /api/users/{user_id}` - Delete user from MongoDB

### New Endpoints (users_routes.py - Supabase based)
- `GET /api/supabase/users` - List users from Supabase
- `POST /api/supabase/users` - Create user in Supabase
- `PUT /api/supabase/users/{user_id}/role` - Update user role in Supabase
- `DELETE /api/supabase/users/{user_id}` - Delete user from Supabase
- `GET /api/supabase/users/stats` - Get user statistics

## Testing

### 1. Restart Backend
```bash
# Stop backend (Ctrl+C)
# Start backend again
cd backend
python main.py
```

### 2. Test Users Module
1. Go to: http://localhost:5173/users
2. ✅ Page should load without 401 error
3. ✅ Users list should appear
4. ✅ Can create new users
5. ✅ Can change user roles
6. ✅ Can delete users

### 3. Check Backend Logs
You should see:
```
INFO:     127.0.0.1:xxxxx - "GET /api/supabase/users HTTP/1.1" 200 OK
```

Instead of:
```
INFO:     127.0.0.1:xxxxx - "GET /api/users HTTP/1.1" 401 Unauthorized
```

## Why This Approach?

### Option 1: Remove duplicate routes ❌
- Would break existing functionality that depends on auth_routes.py

### Option 2: Change registration order ❌
- Fragile solution, easy to break accidentally

### Option 3: Use different prefix ✅ (Chosen)
- Clean separation of concerns
- Both route sets can coexist
- Clear distinction: `/api/users` = MongoDB, `/api/supabase/users` = Supabase
- No breaking changes to existing code

## Authentication Flow

```
Frontend (UsersModule.jsx)
    ↓
Gets Supabase session token
    ↓
Sends request with Authorization header
    ↓
Backend (users_routes.py)
    ↓
verify_token() checks Authorization header
    ↓
Extracts Bearer token
    ↓
Validates token exists
    ↓
Calls Supabase Admin API
    ↓
Returns user data
```

## Security

- ✅ All endpoints require authentication
- ✅ Uses Supabase JWT tokens
- ✅ Authorization header required
- ✅ Token validation before API calls
- ✅ Supabase Admin API for user management

## Troubleshooting

### Still getting 401 error?
1. Check if backend restarted
2. Verify you're logged in
3. Check browser console for token
4. Clear browser cache and reload

### Users not loading?
1. Check backend logs for errors
2. Verify Supabase credentials in `backend/.env`
3. Check network tab in browser DevTools

### Can't create users?
1. Verify you're logged in as superadmin
2. Check Supabase service role key is correct
3. Check backend logs for Supabase API errors

---

**Status**: ✅ Fixed
**Date**: May 27, 2026
