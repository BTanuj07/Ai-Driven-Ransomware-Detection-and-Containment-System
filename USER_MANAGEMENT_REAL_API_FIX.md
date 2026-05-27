# User Management - Real API Integration Fix

## Issues Fixed

### ✅ Issue 1: Users Created with Wrong Role
**Problem:** When creating a user with "Incident Responder" role, they logged in as "Viewer"

**Root Cause:** The Users Module was using localStorage (fake data) instead of the real Supabase API

**Solution:**
- Completely rewrote Users Module to use real backend API
- Now creates users directly in Supabase with correct role in `user_metadata`
- Users get the correct role immediately upon first login

### ✅ Issue 2: Deleted Users Can Still Login
**Problem:** Deleting a user from dashboard only removed them from localStorage, but they could still login via Supabase

**Root Cause:** Delete function wasn't calling the Supabase API to actually delete the user

**Solution:**
- Updated delete function to call backend API: `DELETE /api/users/{id}`
- Backend uses Supabase Admin API to permanently delete user
- User is removed from Supabase authentication and cannot login anymore

---

## What Changed

### Frontend (`frontend/src/components/UsersModule.jsx`)

**Before (Fake Data):**
```javascript
// Used localStorage
const [users, setUsers] = useState(() => {
  const saved = window.localStorage.getItem(STORAGE_KEY)
  return saved ? JSON.parse(saved) : defaultUsers
})

// Fake add user
const handleAddUser = (event) => {
  setUsers((current) => [...current, newUser])
}

// Fake delete
const handleDeleteUser = (id) => {
  setUsers((current) => current.filter((user) => user.id !== id))
}
```

**After (Real API):**
```javascript
// Fetch from backend
const fetchUsers = async () => {
  const response = await apiClient.get('/api/users')
  setUsers(response.data.users)
}

// Real add user to Supabase
const handleAddUser = async (event) => {
  await apiClient.post('/api/users', {
    email, password, role, full_name
  })
  fetchUsers() // Refresh from Supabase
}

// Real delete from Supabase
const handleDeleteUser = async (userId) => {
  await apiClient.delete(`/api/users/${userId}`)
  fetchUsers() // Refresh from Supabase
}
```

### New Features Added

1. **Password Field**
   - Required when creating users
   - Minimum 6 characters
   - User can change after first login

2. **Full Name Field**
   - Optional field for user's full name
   - Stored in Supabase user_metadata

3. **Change Role Button**
   - Update existing user roles
   - Opens modal with role selector
   - Updates role in Supabase immediately

4. **Real User Data**
   - Shows actual users from Supabase
   - Displays real last login time
   - Shows email confirmation status

5. **Proper Delete Confirmation**
   - Warns that deletion is permanent
   - Confirms user will not be able to login
   - Actually removes from Supabase

---

## How It Works Now

### Creating a User

1. **Super Admin fills form:**
   - Email: user@example.com
   - Password: temp123
   - Role: responder
   - Full Name: John Doe

2. **Frontend calls backend:**
   ```
   POST /api/users
   {
     "email": "user@example.com",
     "password": "temp123",
     "role": "responder",
     "full_name": "John Doe"
   }
   ```

3. **Backend creates user in Supabase:**
   ```python
   supabase.auth.admin.create_user({
     "email": "user@example.com",
     "password": "temp123",
     "email_confirm": True,
     "user_metadata": {
       "role": "responder",
       "full_name": "John Doe"
     }
   })
   ```

4. **User can login immediately:**
   - Email: user@example.com
   - Password: temp123
   - Role: responder ✅ (correct!)

### Updating a Role

1. **Super Admin clicks "Change Role"**
2. **Selects new role from dropdown**
3. **Frontend calls backend:**
   ```
   PUT /api/users/{id}/role
   {
     "email": "user@example.com",
     "role": "analyst"
   }
   ```

4. **Backend updates Supabase:**
   ```python
   supabase.auth.admin.update_user_by_id(user_id, {
     "user_metadata": {"role": "analyst"}
   })
   ```

5. **User logs out and back in → sees new role** ✅

### Deleting a User

1. **Super Admin clicks "Delete"**
2. **Confirms deletion**
3. **Frontend calls backend:**
   ```
   DELETE /api/users/{id}
   ```

4. **Backend deletes from Supabase:**
   ```python
   supabase.auth.admin.delete_user(user_id)
   ```

5. **User is permanently removed** ✅
6. **User cannot login anymore** ✅

---

## Testing

### Test User Creation with Correct Role

1. Go to Users module
2. Fill in form:
   - Email: test@example.com
   - Password: test123
   - Role: responder
3. Click "Create User in Supabase"
4. Open new incognito window
5. Login with test@example.com / test123
6. Check role in top-right corner → Should show "responder" ✅

### Test Role Update

1. Go to Users module
2. Find a user
3. Click "Change Role"
4. Select new role
5. Click "Update Role"
6. User logs out and back in
7. Role should be updated ✅

### Test User Deletion

1. Go to Users module
2. Find a user
3. Click "Delete"
4. Confirm deletion
5. User disappears from list ✅
6. Try to login with that user → Should fail ✅
7. Check Supabase Dashboard → User should be gone ✅

---

## Important Notes

### User Must Re-login After Role Change
When you update a user's role, they must:
1. Log out of the dashboard
2. Log back in
3. Then they'll see the new role and permissions

This is because the role is stored in the JWT token, which is only refreshed on login.

### Deletion is Permanent
When you delete a user:
- They are removed from Supabase authentication
- They cannot login anymore
- This action cannot be undone
- All their data is deleted

### Password Requirements
- Minimum 6 characters
- User can change it after first login
- Stored securely in Supabase

---

## Troubleshooting

### Users still showing old role after update
- User needs to log out and log back in
- Clear browser cache
- Check Supabase Dashboard to verify role was updated

### Can't create users
- Check backend logs for errors
- Verify SUPABASE_SERVICE_ROLE_KEY is set in backend/.env
- Ensure backend is running
- Check browser console for errors

### Deleted user can still login
- Check backend logs to see if delete API was called
- Verify user is removed from Supabase Dashboard → Authentication → Users
- If user still exists in Supabase, manually delete them there

### "Authentication required" error
- User needs to be logged in as superadmin
- Check that JWT token is valid
- Try logging out and back in

---

## Benefits

✅ **Real Data** - No more fake localStorage data
✅ **Correct Roles** - Users get assigned role immediately
✅ **Proper Deletion** - Users are actually removed from Supabase
✅ **Role Updates** - Change roles without SQL queries
✅ **Better UX** - Clear feedback and error messages
✅ **Secure** - Uses Supabase Admin API with service role key

---

All user management issues are now fixed! The module uses real Supabase API for all operations. 🎉
