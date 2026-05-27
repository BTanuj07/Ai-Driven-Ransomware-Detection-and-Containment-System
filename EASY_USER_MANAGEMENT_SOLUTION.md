# ✅ Easy User Management Solution

## The Problem
Every time you create a new user in Supabase, they default to "viewer" role, and you have to manually run SQL queries to update their role. This is complicated and time-consuming.

## The Solution
I've created a **User Management API** that lets you manage user roles directly from the ARCS dashboard - no more SQL queries needed!

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Get Supabase Service Role Key

1. Go to https://supabase.com → Your Project
2. Click **Settings** → **API**
3. Copy these 3 values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **service_role** key (the long JWT token)
   - **JWT Secret** (under JWT Settings)

### Step 2: Add to Backend .env

Open `backend/.env` and add:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

### Step 3: Install New Dependency

```bash
cd backend
pip install httpx==0.25.2
```

### Step 4: Restart Backend

```bash
python main.py
```

You should see: `✅ Supabase user management enabled`

---

## 🎯 How to Use

### Create a New User with Role

1. Open ARCS Dashboard
2. Go to **Users** module (in the sidebar)
3. Fill in the form:
   - **Email**: user@example.com
   - **Password**: (temporary password)
   - **Role**: Select from dropdown (Incident Responder, SOC Analyst, etc.)
4. Click **Add User**
5. Done! The user can log in immediately with the correct role ✅

### Update Existing User Role

1. Go to **Users** module
2. Find the user in the list
3. Click **Change Role** button
4. Select new role from dropdown
5. Click **Update**
6. User must log out and log back in to see new role

### Delete User

1. Go to **Users** module
2. Find the user
3. Click **Delete** button
4. Confirm deletion

---

## 📊 Available Roles

| Role | Value | Permissions |
|------|-------|-------------|
| **Super Admin** | `superadmin` | Full system access |
| **Incident Responder** | `responder` | Action execution + containment + monitoring |
| **SOC Analyst** | `analyst` | Monitoring + investigation |
| **Viewer** | `viewer` | Read-only access |

---

## ✨ What's New

### Backend API (`backend/api/users_routes.py`)
- `GET /api/users` - List all users
- `POST /api/users` - Create user with role
- `PUT /api/users/{id}/role` - Update user role
- `DELETE /api/users/{id}` - Delete user
- `GET /api/users/stats` - User statistics

### Features
✅ Create users with roles directly from dashboard
✅ Update user roles with one click
✅ No more manual SQL queries
✅ Auto-confirm user emails
✅ View all users and their roles
✅ Delete users when needed

---

## 🔒 Security

- Service Role Key is stored in backend `.env` (never exposed to frontend)
- Only Super Admin can manage users
- All operations are logged
- Keys are never committed to Git

---

## 🐛 Troubleshooting

### Backend shows "Supabase not configured"
- Check that all 3 variables are in `backend/.env`
- Restart backend server
- Verify no typos in the keys

### Can't see Users module
- Make sure you're logged in as **superadmin**
- Check that `tanuj077777@gmail.com` is your email (hardcoded superadmin)

### "Unauthorized" error
- Make sure you copied the **service_role** key (not anon key)
- Check the key is complete (very long JWT token)

### Users not showing
- Verify users exist in Supabase Dashboard → Authentication → Users
- Check backend console for errors
- Try refreshing the page

---

## 📝 Example Workflow

**Before (Complicated):**
1. User signs up → Gets "viewer" role
2. Open Supabase Dashboard
3. Go to SQL Editor
4. Write SQL query to update role
5. Run query
6. Tell user to log out and log back in

**After (Easy):**
1. Open ARCS Dashboard → Users module
2. Click "Add User"
3. Enter email, password, select role
4. Click "Add User"
5. Done! User can log in with correct role immediately ✅

---

## 🎉 Benefits

- ⚡ **Faster** - Create users in seconds, not minutes
- 🎯 **Easier** - No SQL knowledge required
- 🔒 **Safer** - No direct database access needed
- 👥 **Better UX** - Manage everything from one dashboard
- 📊 **Visibility** - See all users and their roles at a glance

---

## 📚 Additional Resources

- `SUPABASE_SERVICE_KEY_SETUP.md` - Detailed setup guide
- `backend/api/users_routes.py` - API implementation
- `frontend/src/components/UsersModule.jsx` - UI component

---

## Need Help?

1. Check `SUPABASE_SERVICE_KEY_SETUP.md` for detailed setup
2. Verify backend logs for errors
3. Check browser console for frontend errors
4. Ensure you're logged in as superadmin

---

**That's it! No more complicated SQL queries for every new user.** 🎉
