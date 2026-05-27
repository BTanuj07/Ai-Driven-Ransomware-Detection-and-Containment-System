# Password Reset Setup Guide

## Overview
The password reset functionality has been implemented and requires Supabase email configuration to work properly.

## What Was Fixed

### 1. Removed Signup Option
- Removed the "Sign up" button from the login page
- Added message: "Need access? Contact your administrator"
- Only superadmin can create users through the Users Module

### 2. Implemented Password Reset Flow
- Added redirect URL configuration to password reset request
- Created new `/reset-password` page for users to set their new password
- Improved error handling with user-friendly messages
- Added password validation (minimum 6 characters, must match confirmation)

## Files Modified

1. **frontend/src/components/Login.jsx**
   - Removed signup button
   - Added "Contact your administrator" message
   - Improved password reset error handling

2. **frontend/src/contexts/AuthContext.jsx**
   - Added `redirectTo` parameter to `resetPasswordForEmail()`
   - Redirect URL: `${window.location.origin}/reset-password`

3. **frontend/src/components/ResetPassword.jsx** (NEW)
   - New component for password reset page
   - Validates password length and confirmation match
   - Redirects to login after successful password update

4. **frontend/src/App.jsx**
   - Added routing for `/reset-password` page
   - Separated public routes (login, reset-password) from protected routes

5. **frontend/src/components/ProtectedRoute.jsx**
   - Updated to redirect to `/login` instead of rendering Login component inline

## How Password Reset Works

### User Flow:
1. User clicks "Forgot Password?" on login page
2. User enters their email address
3. User clicks "Send Reset Email"
4. Supabase sends email with reset link (if configured)
5. User clicks link in email → redirected to `/reset-password`
6. User enters new password (twice for confirmation)
7. User clicks "Update Password"
8. User is redirected to login page with new password

### Technical Flow:
```
Login Page → resetPassword(email) 
  ↓
Supabase sends email with token
  ↓
Email link: https://your-app.com/reset-password#access_token=...&type=recovery
  ↓
Reset Password Page → updatePassword(newPassword)
  ↓
Redirect to Login
```

## Supabase Email Configuration Required

⚠️ **IMPORTANT**: Password reset will NOT work until you configure email settings in Supabase.

### Option 1: Use Supabase's Default Email Service (Easiest)

1. Go to your Supabase Dashboard: https://app.supabase.com
2. Select your project: `hsbcjonzbnwjnftfohyk`
3. Navigate to: **Authentication** → **Email Templates**
4. Supabase provides a default email service (limited to 3 emails per hour in free tier)
5. Verify the "Reset Password" template is enabled

### Option 2: Configure Custom SMTP (Recommended for Production)

1. Go to: **Project Settings** → **Authentication** → **SMTP Settings**
2. Enable "Enable Custom SMTP"
3. Configure your SMTP provider:
   ```
   Host: smtp.gmail.com (for Gmail)
   Port: 587
   Username: your-email@gmail.com
   Password: your-app-password
   Sender Email: your-email@gmail.com
   Sender Name: ARCS Security System
   ```

#### Popular SMTP Providers:
- **Gmail**: smtp.gmail.com:587 (requires App Password)
- **SendGrid**: smtp.sendgrid.net:587
- **Mailgun**: smtp.mailgun.org:587
- **AWS SES**: email-smtp.region.amazonaws.com:587

### Configure Email Templates

1. Go to: **Authentication** → **Email Templates**
2. Select "Reset Password" template
3. Customize the email (optional):
   ```html
   <h2>Reset Your Password</h2>
   <p>Click the link below to reset your password for ARCS:</p>
   <p><a href="{{ .ConfirmationURL }}">Reset Password</a></p>
   <p>If you didn't request this, please ignore this email.</p>
   ```

### Configure Redirect URLs

1. Go to: **Authentication** → **URL Configuration**
2. Add your site URL:
   - Development: `http://localhost:5173`
   - Production: `https://your-domain.com`
3. Add redirect URLs (whitelist):
   - `http://localhost:5173/reset-password`
   - `https://your-domain.com/reset-password`

## Testing Password Reset

### Test Locally:

1. Start your frontend: `npm run dev` (in frontend folder)
2. Go to: http://localhost:5173/login
3. Click "Forgot Password?"
4. Enter a test user's email
5. Click "Send Reset Email"
6. Check the email inbox (or Supabase logs if using default service)
7. Click the reset link in the email
8. Enter new password (min 6 characters)
9. Confirm password matches
10. Click "Update Password"
11. You should be redirected to login with success message

### Troubleshooting:

**Error: "Error sending recovery email"**
- Check Supabase email configuration
- Verify SMTP credentials are correct
- Check Supabase logs: Dashboard → Logs → Auth Logs
- Ensure redirect URL is whitelisted

**Email not received:**
- Check spam/junk folder
- Verify email address is correct
- Check Supabase email quota (3/hour for free tier)
- Review Supabase Auth Logs for delivery status

**Reset link doesn't work:**
- Verify redirect URL is whitelisted in Supabase
- Check that link hasn't expired (default: 1 hour)
- Ensure frontend is running on the correct URL

**"Invalid or expired password reset link":**
- Link may have expired (request new one)
- Link may have already been used
- URL parameters may be corrupted

## Security Notes

1. **Password Requirements:**
   - Minimum 6 characters (Supabase default)
   - Can be increased in Supabase settings

2. **Reset Link Expiry:**
   - Default: 1 hour
   - Configurable in Supabase Auth settings

3. **Rate Limiting:**
   - Supabase limits password reset requests
   - Prevents abuse and spam

4. **Email Verification:**
   - Only registered users can request password reset
   - Invalid emails are silently ignored (security best practice)

## Production Deployment

Before deploying to production:

1. ✅ Configure production SMTP provider
2. ✅ Update site URL in Supabase
3. ✅ Whitelist production redirect URLs
4. ✅ Test password reset flow end-to-end
5. ✅ Monitor email delivery rates
6. ✅ Set up email delivery monitoring/alerts

## Support

If users report password reset issues:

1. Check Supabase Auth Logs
2. Verify email configuration
3. Check email delivery status
4. Verify user email is correct in database
5. Test with your own account first

## Alternative: Manual Password Reset by Admin

If email is not configured, superadmin can reset passwords manually:

1. Go to Users Module in ARCS dashboard
2. Find the user
3. Click "Change Role" (or add a "Reset Password" button)
4. Use Supabase Dashboard → Authentication → Users
5. Click on user → "Send Password Recovery Email"
6. Or manually update password in Supabase

---

**Status**: ✅ Password reset implemented, requires Supabase email configuration
**Last Updated**: May 26, 2026
