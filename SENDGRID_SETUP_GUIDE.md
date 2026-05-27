# SendGrid Setup Guide for Password Reset

## Overview
Your password reset is already implemented! Users can click "Forgot Password", enter their email, and receive a recovery link to set a new password. You just need to configure SendGrid in Supabase.

## Current Flow (Already Implemented ✅)

1. User clicks "Forgot Password?" on login page
2. User enters their email address
3. User clicks "Send Reset Email"
4. **SendGrid sends email with recovery link** (needs configuration)
5. User clicks link in email → redirected to `/reset-password` page
6. User enters new password (twice for confirmation)
7. User clicks "Update Password"
8. Password is updated, user redirected to login

## Step 1: Create SendGrid Account

1. Go to https://sendgrid.com/
2. Click "Start for Free" or "Sign Up"
3. Create account (Free tier: 100 emails/day forever)
4. Verify your email address
5. Complete the SendGrid onboarding

## Step 2: Create SendGrid API Key

1. Log in to SendGrid Dashboard
2. Go to **Settings** → **API Keys** (left sidebar)
3. Click "Create API Key" (top right)
4. Configure:
   - **API Key Name**: `ARCS-Password-Reset` (or any name)
   - **API Key Permissions**: Select "Restricted Access"
   - Enable only: **Mail Send** → **Full Access**
5. Click "Create & View"
6. **IMPORTANT**: Copy the API key immediately (you won't see it again!)
   ```
   Example: SG.xxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
   ```
7. Save it somewhere safe temporarily

## Step 3: Verify Sender Email (Required)

SendGrid requires you to verify the email address you'll send from.

### Option A: Single Sender Verification (Easiest - Free Tier)

1. In SendGrid Dashboard, go to **Settings** → **Sender Authentication**
2. Click "Verify a Single Sender"
3. Click "Create New Sender"
4. Fill in the form:
   ```
   From Name: ARCS Security System
   From Email Address: your-email@gmail.com (or your domain email)
   Reply To: your-email@gmail.com
   Company Address: Your address
   City: Your city
   Country: Your country
   ```
5. Click "Create"
6. Check your email inbox for verification email from SendGrid
7. Click the verification link
8. ✅ Your sender email is now verified!

### Option B: Domain Authentication (Recommended for Production)

1. Go to **Settings** → **Sender Authentication**
2. Click "Authenticate Your Domain"
3. Follow the wizard to add DNS records to your domain
4. This allows you to send from any email @yourdomain.com

## Step 4: Configure Supabase with SendGrid

1. Go to Supabase Dashboard: https://app.supabase.com
2. Select your project: `hsbcjonzbnwjnftfohyk`
3. Go to **Project Settings** (gear icon, bottom left)
4. Click **Authentication** in the left sidebar
5. Scroll down to **SMTP Settings**
6. Click "Enable Custom SMTP"
7. Fill in SendGrid SMTP details:

```
Enable Custom SMTP: ✅ ON

Sender Name: ARCS Security System
Sender Email: your-verified-email@gmail.com (must match verified sender)

Host: smtp.sendgrid.net
Port Number: 587
Username: apikey (literally type "apikey")
Password: [Paste your SendGrid API Key here]

Minimum Interval: 60 (seconds between emails to same address)
Rate Limit: 10 (max emails per hour per user)
```

8. Click "Save"

## Step 5: Configure Email Templates

1. In Supabase, go to **Authentication** → **Email Templates**
2. Select "Reset Password" template
3. Customize the email (optional):

```html
<h2>Reset Your ARCS Password</h2>

<p>Hello,</p>

<p>You requested to reset your password for ARCS (AI-Driven Ransomware Detection & Containment System).</p>

<p>Click the button below to reset your password:</p>

<p>
  <a href="{{ .ConfirmationURL }}" 
     style="background-color: #3b82f6; color: white; padding: 12px 24px; 
            text-decoration: none; border-radius: 6px; display: inline-block;">
    Reset Password
  </a>
</p>

<p>Or copy and paste this link into your browser:</p>
<p>{{ .ConfirmationURL }}</p>

<p><strong>This link will expire in 1 hour.</strong></p>

<p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>

<p>Best regards,<br>ARCS Security Team</p>
```

4. Click "Save"

## Step 6: Configure Redirect URLs

1. Still in Supabase, go to **Authentication** → **URL Configuration**
2. Add your Site URL:
   - Development: `http://localhost:5173`
   - Production: `https://your-domain.com`
3. Add Redirect URLs (whitelist):
   ```
   http://localhost:5173/**
   http://localhost:5173/reset-password
   ```
4. For production, also add:
   ```
   https://your-domain.com/**
   https://your-domain.com/reset-password
   ```
5. Click "Save"

## Step 7: Test Password Reset

1. Make sure your frontend is running:
   ```bash
   cd frontend
   npm run dev
   ```

2. Go to http://localhost:5173/login

3. Click "Forgot Password?"

4. Enter a test user's email (must be a real user in your system)

5. Click "Send Reset Email"

6. Check the email inbox (the one you entered)

7. You should receive an email from SendGrid with subject "Reset Your Password"

8. Click the "Reset Password" button in the email

9. You'll be redirected to: `http://localhost:5173/reset-password#access_token=...`

10. Enter your new password (min 6 characters)

11. Confirm the password

12. Click "Update Password"

13. You should see: "Password updated successfully! Redirecting to login..."

14. Try logging in with your new password ✅

## Troubleshooting

### Error: "Error sending recovery email"

**Check 1: Supabase SMTP Configuration**
- Verify SMTP settings are saved in Supabase
- Username must be exactly: `apikey`
- Password must be your SendGrid API Key (starts with `SG.`)

**Check 2: SendGrid API Key Permissions**
- API Key must have "Mail Send" → "Full Access"
- Create a new API key if unsure

**Check 3: Sender Email Verification**
- Sender email in Supabase must match verified sender in SendGrid
- Check SendGrid → Settings → Sender Authentication

**Check 4: Supabase Logs**
- Go to Supabase Dashboard → Logs → Auth Logs
- Look for error messages about email sending

### Email Not Received

**Check 1: Spam Folder**
- SendGrid emails sometimes go to spam initially
- Mark as "Not Spam" to train your email provider

**Check 2: Email Address**
- Verify the email address exists in your Supabase users
- Check for typos

**Check 3: SendGrid Activity**
- Go to SendGrid Dashboard → Activity
- Check if email was sent successfully
- Look for bounces or blocks

**Check 4: Rate Limiting**
- Supabase limits: 1 email per 60 seconds to same address
- Wait 1 minute between attempts

### Reset Link Doesn't Work

**Check 1: Redirect URL Whitelist**
- Verify `http://localhost:5173/reset-password` is in Supabase redirect URLs
- Check for typos in URL configuration

**Check 2: Link Expiry**
- Reset links expire after 1 hour
- Request a new reset email

**Check 3: Frontend Running**
- Make sure frontend is running on http://localhost:5173
- Check browser console for errors

### "Invalid or expired password reset link"

**Cause**: Link has expired or already been used

**Solution**: 
1. Go back to login page
2. Click "Forgot Password?" again
3. Request a new reset email

## SendGrid Free Tier Limits

- ✅ 100 emails per day (forever free)
- ✅ Perfect for small teams and development
- ✅ No credit card required
- ✅ No expiration

For production with more users, consider upgrading:
- Essentials: $19.95/month (50,000 emails)
- Pro: $89.95/month (100,000 emails)

## Security Best Practices

1. **API Key Security**
   - Never commit API keys to Git
   - Store only in Supabase settings
   - Rotate keys periodically

2. **Sender Verification**
   - Always verify sender email
   - Use domain authentication for production

3. **Rate Limiting**
   - Keep Supabase rate limits enabled
   - Prevents abuse and spam

4. **Email Content**
   - Don't include sensitive information in emails
   - Use HTTPS links only
   - Include expiry information

## Production Checklist

Before going live:

- [ ] SendGrid account created and verified
- [ ] Sender email verified (or domain authenticated)
- [ ] API key created with Mail Send permissions
- [ ] Supabase SMTP configured with SendGrid
- [ ] Email template customized
- [ ] Production redirect URLs whitelisted
- [ ] Password reset tested end-to-end
- [ ] Email deliverability tested (check spam)
- [ ] SendGrid activity monitoring set up

## Alternative: Use Supabase Default Email (Not Recommended)

If you don't want to use SendGrid, Supabase provides a default email service:

**Limitations:**
- Only 3 emails per hour (very limited!)
- Not reliable for production
- May have deliverability issues

**To use:**
1. Don't enable Custom SMTP in Supabase
2. Supabase will use their default service
3. Only suitable for testing

## Support Resources

- **SendGrid Docs**: https://docs.sendgrid.com/
- **Supabase Auth Docs**: https://supabase.com/docs/guides/auth
- **SendGrid Support**: https://support.sendgrid.com/

## Summary

✅ **Password reset is already implemented in your code!**

You just need to:
1. Create SendGrid account (5 minutes)
2. Get API key (2 minutes)
3. Verify sender email (3 minutes)
4. Configure Supabase SMTP (2 minutes)
5. Test it! (2 minutes)

**Total time: ~15 minutes**

After configuration, users can reset their passwords independently without admin intervention!

---

**Need Help?** Check the troubleshooting section or Supabase Auth Logs for detailed error messages.
