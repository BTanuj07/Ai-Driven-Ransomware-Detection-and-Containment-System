# Check Email Template Status

## Current Issue
Email template not updating in Supabase despite changes.

## Possible Causes

### 1. Template Cache
Supabase caches email templates for performance. Changes may take 5-10 minutes to propagate.

**Solution:**
- Wait 10 minutes after saving
- Or pause/resume project to clear cache

### 2. Wrong Template Selected
Make sure you're editing the correct template.

**Check:**
- Go to Authentication → Email Templates
- Select "Reset Password" (not "Confirm signup" or "Magic Link")
- Verify the template name at the top

### 3. Template Syntax Error
If template has syntax errors, Supabase falls back to default.

**Check:**
- Look for any red error messages in template editor
- Verify `{{ .ConfirmationURL }}` is spelled correctly (case-sensitive)
- No extra spaces in variable names

### 4. SMTP Override
Some SMTP providers override email templates.

**Check:**
- SendGrid should NOT override templates
- Verify you're using Supabase SMTP settings, not SendGrid templates

### 5. Browser Cache
Your browser might be caching the old email.

**Solution:**
- Clear browser cache (Ctrl+Shift+Delete)
- Try in incognito/private window
- Or use a different email address

## Verification Steps

### Step 1: Check Supabase Template
1. Go to: https://app.supabase.com
2. Project: `hsbcjonzbnwjnftfohyk`
3. Authentication → Email Templates → Reset Password
4. Verify the template shows your new HTML

### Step 2: Check SendGrid Activity
1. Go to: https://app.sendgrid.com
2. Activity → Email Activity
3. Find the most recent password reset email
4. Click to view the actual email content sent
5. Compare with your template

### Step 3: Test Email Content
1. Request password reset
2. Check email source (View → Show Original in Gmail)
3. Look for your custom HTML
4. If you see plain text, template isn't being used

## Quick Fix: Minimal Template

If fancy template doesn't work, try this minimal version:

```html
<h2>Reset Your Password</h2>

<p>Click here to reset your password:</p>

<p><a href="{{ .ConfirmationURL }}" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Reset Password</a></p>

<p>Link: {{ .ConfirmationURL }}</p>

<p>This link expires in 1 hour.</p>
```

This removes all complex styling and should work immediately.

## Debug: Check What's Being Sent

### Method 1: View Email Source
1. Open the password reset email
2. In Gmail: Click ⋮ → Show original
3. In Outlook: File → Properties → Internet headers
4. Look for the HTML content
5. See if it matches your template

### Method 2: SendGrid Event Webhook
1. In SendGrid, go to Settings → Mail Settings
2. Enable Event Webhook
3. Set URL to: https://webhook.site (get a free URL)
4. Send test email
5. Check webhook.site to see actual email content

### Method 3: Test Email Address
1. Use a test email service: https://temp-mail.org
2. Request password reset to that address
3. Check if template is applied
4. This rules out email client issues

## Common Template Variables

Make sure you're using the correct variable:

✅ Correct:
- `{{ .ConfirmationURL }}` - Full reset link
- `{{ .Token }}` - Just the token
- `{{ .Email }}` - User's email
- `{{ .SiteURL }}` - Your site URL

❌ Wrong:
- `{{ .ResetURL }}` - Doesn't exist
- `{{ .PasswordResetURL }}` - Doesn't exist
- `{{.ConfirmationURL}}` - Missing spaces
- `{{ ConfirmationURL }}` - Missing dot

## Still Not Working?

### Last Resort: Contact Supabase Support
1. Go to Supabase Dashboard
2. Click Support (bottom left)
3. Describe issue: "Email template not updating for password reset"
4. Include:
   - Project ID: `hsbcjonzbnwjnftfohyk`
   - Template name: Reset Password
   - Issue: Template changes not reflected in emails

### Alternative: Use Custom Backend
If Supabase templates don't work, you can:
1. Create custom password reset endpoint in your backend
2. Use SendGrid directly (you already have it configured)
3. Send custom emails with your own template
4. More control but more code

## Expected Timeline

- Template save: Instant
- Cache clear: 5-10 minutes
- Email delivery: 10-30 seconds
- Total: ~10 minutes for changes to appear

**Recommendation:** Wait 10 minutes after saving template, then test again.
