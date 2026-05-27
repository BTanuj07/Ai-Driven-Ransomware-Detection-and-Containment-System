# Supabase Service Key Setup for User Management

To enable user role management from the ARCS dashboard, you need to add your Supabase Service Role Key to the backend.

## 🔑 Get Your Supabase Service Role Key

### Step 1: Open Supabase Dashboard
1. Go to https://supabase.com
2. Sign in to your account
3. Select your ARCS project

### Step 2: Navigate to API Settings
1. Click on **Settings** (gear icon) in the left sidebar
2. Click on **API**

### Step 3: Copy the Service Role Key
1. Scroll down to **Project API keys**
2. Find **service_role** key (NOT the anon key!)
3. Click the **Copy** button
4. ⚠️ **Keep this key secret!** It has admin privileges

### Step 4: Copy the Project URL
1. At the top of the same page, find **Project URL**
2. Copy the URL (e.g., `https://xxxxx.supabase.co`)

### Step 5: Copy the JWT Secret
1. Scroll down to **JWT Settings**
2. Copy the **JWT Secret**

## 📝 Add to Backend .env File

Open `backend/.env` and add these lines:

```env
# Supabase Configuration (Required for User Management)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

Replace with your actual values from Step 2-5.

## 🔄 Restart Backend

After adding the keys, restart your backend server:

```bash
cd backend
python main.py
```

You should see:
```
✅ Supabase user management enabled
```

## ✅ Test User Management

1. Open ARCS Dashboard
2. Go to **Users** module
3. You should now see:
   - List of all Supabase users
   - Ability to create new users with roles
   - Ability to update user roles
   - Ability to delete users

## 🎯 Features Enabled

With the Service Role Key configured, you can:

✅ **Create Users** - Add new users directly from the dashboard
✅ **Assign Roles** - Set role during user creation (no more manual SQL!)
✅ **Update Roles** - Change user roles with one click
✅ **Delete Users** - Remove users when needed
✅ **View All Users** - See all registered users and their roles
✅ **Auto-confirm Emails** - New users are automatically verified

## 🔒 Security Notes

1. **Never commit** the service role key to Git
2. **Keep it secret** - it has full admin access to your Supabase project
3. **Use environment variables** - always load from `.env` file
4. **Rotate regularly** - change the key periodically for security
5. **Backend only** - never expose this key to the frontend

## 🐛 Troubleshooting

### "Supabase not configured" error
- Check that all three variables are set in `backend/.env`
- Restart the backend server
- Verify the keys are correct (no extra spaces)

### "Unauthorized" error
- Make sure you copied the **service_role** key, not the **anon** key
- Check that the key hasn't expired or been revoked
- Verify the SUPABASE_URL matches your project

### Users not showing up
- Check that users exist in Supabase → Authentication → Users
- Verify the backend is connected (check console logs)
- Try refreshing the dashboard

### Can't create users
- Ensure you're logged in as **superadmin**
- Check browser console for errors
- Verify backend logs for API errors

## 📚 API Endpoints

Once configured, these endpoints are available:

- `GET /api/users` - List all users
- `POST /api/users` - Create new user with role
- `PUT /api/users/{id}/role` - Update user role
- `DELETE /api/users/{id}` - Delete user
- `GET /api/users/stats` - Get user statistics

## 🎓 Next Steps

1. Add the Supabase keys to `backend/.env`
2. Restart the backend
3. Open the Users module in the dashboard
4. Create a test user with "responder" role
5. Have them log in - they'll have the correct role immediately!

No more manual SQL queries needed! 🎉
