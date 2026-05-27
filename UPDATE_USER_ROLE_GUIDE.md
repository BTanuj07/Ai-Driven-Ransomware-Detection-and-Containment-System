# Update User Role in ARCS

When a new user signs up, they default to "viewer" role. Follow these steps to update their role.

## 🔍 Important: Authentication Architecture

Your ARCS system uses:
- **Supabase** for authentication (frontend login/signup)
- **MongoDB** for backend data storage (alerts, logs, etc.)

**User roles are stored in Supabase**, so you only need to update Supabase. MongoDB sync is optional for consistency.

## Method 1: Using Supabase Dashboard (Easiest)

### Step 1: Open Supabase Dashboard
1. Go to https://supabase.com
2. Sign in to your account
3. Select your ARCS project

### Step 2: Navigate to SQL Editor
1. Click on **SQL Editor** in the left sidebar
2. Click **New Query**

### Step 3: Run the Update Query

Copy and paste this SQL, **replacing the email address**:

```sql
-- Check current users first
SELECT 
    id,
    email,
    raw_user_meta_data->>'role' as current_role
FROM auth.users
ORDER BY created_at DESC;

-- Update user role to INCIDENT RESPONDER
UPDATE auth.users
SET raw_user_meta_data = jsonb_set(
    COALESCE(raw_user_meta_data, '{}'::jsonb),
    '{role}',
    '"responder"'
)
WHERE email = 'YOUR_USER_EMAIL@example.com';  -- ⚠️ CHANGE THIS!

-- Verify the update
SELECT 
    email,
    raw_user_meta_data->>'role' as updated_role
FROM auth.users
WHERE email = 'YOUR_USER_EMAIL@example.com';  -- ⚠️ CHANGE THIS!
```

### Step 4: User Must Re-login
The user needs to:
1. **Log out** of the ARCS dashboard
2. **Log back in** to see the new role

---

## Method 2: Using Python Script

If you have the Supabase Service Role Key:

```bash
# Install supabase client
pip install supabase

# Run the script
python update_user_role.py
```

Follow the prompts to update the user role.

---

## Method 3: Using SQL File

1. Open `update_user_role.sql` in a text editor
2. Replace `'user@example.com'` with the actual email
3. Copy the SQL
4. Paste in Supabase SQL Editor
5. Click **Run**

---

## Available Roles

| Role | Value | Permissions |
|------|-------|-------------|
| **Super Admin** | `superadmin` | Full system access with all permissions |
| **Incident Responder** | `responder` | Action execution + containment control + monitoring |
| **SOC Analyst** | `analyst` | Monitoring and investigation capabilities |
| **Viewer** | `viewer` | Read-only access for auditing |

---

## Quick Reference: Update to Different Roles

### Set as Incident Responder (Recommended for your case):
```sql
UPDATE auth.users
SET raw_user_meta_data = jsonb_set(
    COALESCE(raw_user_meta_data, '{}'::jsonb),
    '{role}',
    '"responder"'
)
WHERE email = 'user@example.com';
```

### Set as SOC Analyst:
```sql
UPDATE auth.users
SET raw_user_meta_data = jsonb_set(
    COALESCE(raw_user_meta_data, '{}'::jsonb),
    '{role}',
    '"analyst"'
)
WHERE email = 'user@example.com';
```

### Set as Super Admin:
```sql
UPDATE auth.users
SET raw_user_meta_data = jsonb_set(
    COALESCE(raw_user_meta_data, '{}'::jsonb),
    '{role}',
    '"superadmin"'
)
WHERE email = 'user@example.com';
```

---

## Troubleshooting

### Role not updating after SQL execution?
- Make sure the user **logs out and logs back in**
- Check if the email address is correct (case-sensitive)
- Verify the update with the SELECT query

### Can't access Supabase Dashboard?
- Check your Supabase account credentials
- Ensure you're in the correct project

### Python script not working?
- Make sure you have `SUPABASE_SERVICE_ROLE_KEY` in your `.env` file
- Install required package: `pip install supabase`
- Use the SQL method instead if you don't have the service role key

---

## Important Notes

1. **Users must re-login** after role changes
2. **Email addresses are case-sensitive** in the WHERE clause
3. **Only use `superadmin`** for trusted administrators
4. **Default role is `viewer`** for all new signups
5. The superadmin email `tanuj077777@gmail.com` is hardcoded in the frontend

---

## Need Help?

If you're still having issues:
1. Check the browser console for errors
2. Verify the user exists in Supabase → Authentication → Users
3. Ensure the SQL query executed successfully (check for error messages)
4. Try clearing browser cache and cookies before logging in again


---

## 🔄 Optional: Sync to MongoDB

Your system uses **Supabase for authentication** (where roles are stored) and **MongoDB for data storage**. 

**You only need to update Supabase** - that's where the frontend checks user roles.

However, if you want to keep MongoDB in sync for consistency:

```bash
# Install dependencies
pip install pymongo python-dotenv

# Run sync script
python sync_user_role_to_mongodb.py
```

This script will:
1. Connect to your MongoDB
2. Create or update a user record with the role
3. Map Supabase roles to MongoDB roles:
   - `superadmin` → `admin`
   - `responder` → `analyst`
   - `analyst` → `analyst`
   - `viewer` → `viewer`

**Important:** Run this AFTER updating the role in Supabase.

---

## 📊 Role Comparison

| Supabase Role | MongoDB Role | Used By |
|---------------|--------------|---------|
| `superadmin` | `admin` | Frontend authentication |
| `responder` | `analyst` | Frontend authentication |
| `analyst` | `analyst` | Frontend authentication |
| `viewer` | `viewer` | Frontend authentication |

The **frontend only checks Supabase** for roles. MongoDB sync is optional for backend consistency.
