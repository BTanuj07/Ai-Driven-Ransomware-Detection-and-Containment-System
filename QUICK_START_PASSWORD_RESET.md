# Quick Start: Enable Password Reset (15 Minutes)

## ✅ Good News!
Your password reset feature is **already fully implemented** in the code! Users can already:
- Click "Forgot Password?" on login page
- Enter their email
- Receive a recovery link
- Set a new password

**You just need to configure SendGrid in Supabase to enable email sending.**

---

## 🚀 Quick Setup (Follow These Steps)

### Step 1: Create SendGrid Account (5 min)

1. Go to: https://sendgrid.com/
2. Click "Start for Free"
3. Sign up (Free tier = 100 emails/day forever)
4. Verify your email address

### Step 2: Get SendGrid API Key (2 min)

1. Log in to SendGrid Dashboard
2. Go to: **Settings** → **API Keys**
3. Click "Create API Key"
4. Name it: `ARCS-Password-Reset`
5. Permissions: **Restricted Access** → Enable only **Mail Send** → **Full Access**
6. Click "Create & View"
7. **COPY THE API KEY** (starts with `SG.`) - you won't see it again!

```
Example: SG.abc123xyz789...
```

### Step 3: Verify Your Sender Email (3 min)

1. In SendGrid, go to: **Settings** → **Sender Authentication**
2. Click "Verify a Single Sender"
3. Click "Create New Sender"
4. Fill in:
   - **From Name**: `ARCS Security System`
   - **From Email**: Your email (e.g., `tanuj077777@gmail.com`)
   - **Reply To**: Same email
   - Fill in address details (required by SendGrid)
5. Click "Create"
6. Check your email for verification link from SendGrid
7. Click the verification link ✅

### Step 4: Configure Supabase (3 min)

1. Go to: https://app.supabase.com
2. Select your project: `hsbcjonzbnwjnftfohyk`
3. Click **Settings** (gear icon, bottom left)
4. Click **Authentication**
5. Scroll to **SMTP Settings**
6. Toggle "Enable Custom SMTP" to **ON**
7. Fill in:

```
Sender Name: ARCS Security System
Sender Email: [Your verified email from Step 3]

Host: smtp.sendgrid.net
Port Number: 587
Username: apikey
Password: [Paste your SendGrid API Key from Step 2]
```

8. Click **Save**

### Step 5: Configure Redirect URLs (2 min)

1. Still in Supabase, go to: **Authentication** → **URL Configuration**
2. Set **Site URL**: `http://localhost:5173`
3. Add **Redirect URLs**:
   ```
   http://localhost:5173/**
   http://localhost:5173/reset-password
   ```
4. Click **Save**

---

## 🧪 Test It!

1. Start your frontend:
   ```bash
   cd frontend
   npm run dev
   ```

2. Go to: http://localhost:5173/login

3. Click "Forgot Password?"

4. Enter a test user's email

5. Click "Send Reset Email"

6. Check your email inbox (and spam folder)

7. Click the "Reset Password" link in the email

8. Enter new password (min 6 characters)

9. Click "Update Password"

10. Try logging in with new password ✅

---

## 🎯 What You Get

After setup, users can:
- ✅ Reset their own passwords without admin help
- ✅ Receive professional-looking reset emails
- ✅ Securely set new passwords
- ✅ Get clear error messages if something goes wrong

---

## 📋 Configuration Summary

**Your Supabase Project:**
- URL: `https://hsbcjonzbnwjnftfohyk.supabase.co`
- Project ID: `hsbcjonzbnwjnftfohyk`

**SendGrid SMTP Settings:**
```
Host: smtp.sendgrid.net
Port: 587
Username: apikey
Password: [Your SendGrid API Key]
```

**Redirect URLs:**
```
Development: http://localhost:5173/reset-password
Production: https://your-domain.com/reset-password
```

---

## ❓ Troubleshooting

### "Error sending recovery email"
- Check Supabase SMTP settings are saved
- Verify SendGrid API key is correct
- Ensure sender email is verified in SendGrid

### Email not received
- Check spam/junk folder
- Verify email address is correct
- Check SendGrid Dashboard → Activity for delivery status

### Reset link doesn't work
- Verify redirect URL is whitelisted in Supabase
- Make sure frontend is running on http://localhost:5173
- Link expires after 1 hour - request new one

---

## 📚 Detailed Guides

- **Full SendGrid Setup**: See `SENDGRID_SETUP_GUIDE.md`
- **Password Reset Details**: See `PASSWORD_RESET_SETUP.md`
- **All Login Changes**: See `LOGIN_PAGE_FIXES.md`

---

## ✨ Summary

**What's Already Done:**
- ✅ Password reset UI implemented
- ✅ Reset password page created
- ✅ Email validation added
- ✅ Routing configured
- ✅ Error handling improved
- ✅ Signup button removed

**What You Need to Do:**
1. Create SendGrid account
2. Get API key
3. Verify sender email
4. Configure Supabase SMTP
5. Test it!

**Time Required:** ~15 minutes

**Result:** Users can reset passwords independently! 🎉

---

**Questions?** Check the detailed guides or Supabase Auth Logs for error messages.
