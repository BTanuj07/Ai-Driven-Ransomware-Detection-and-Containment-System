# Password Reset Flow - Visual Guide

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    PASSWORD RESET FLOW                          │
└─────────────────────────────────────────────────────────────────┘

Step 1: User Forgets Password
┌──────────────────┐
│  Login Page      │
│  localhost:5173  │
│                  │
│  [Email]         │
│  [Password]      │
│                  │
│  ❌ User forgot  │
│     password     │
│                  │
│  👆 Click:       │
│  "Forgot         │
│   Password?"     │
└────────┬─────────┘
         │
         ▼
Step 2: Enter Email
┌──────────────────┐
│  Reset Password  │
│  Modal/Form      │
│                  │
│  Enter email:    │
│  ┌────────────┐  │
│  │user@email  │  │
│  └────────────┘  │
│                  │
│  [Send Reset     │
│   Email]         │
└────────┬─────────┘
         │
         ▼
Step 3: Backend Processing
┌──────────────────────────────────────┐
│  Supabase Auth                       │
│  ✓ Validates email exists            │
│  ✓ Generates secure token            │
│  ✓ Creates reset link with token     │
│  ✓ Sends to SendGrid SMTP            │
└────────┬─────────────────────────────┘
         │
         ▼
Step 4: SendGrid Sends Email
┌──────────────────────────────────────┐
│  SendGrid Email Service              │
│  📧 From: ARCS Security System       │
│  📧 To: user@email.com               │
│  📧 Subject: Reset Your Password     │
│                                      │
│  Email Content:                      │
│  ┌────────────────────────────────┐ │
│  │ Reset Your ARCS Password       │ │
│  │                                │ │
│  │ Click to reset:                │ │
│  │ [Reset Password Button]        │ │
│  │                                │ │
│  │ Link expires in 1 hour         │ │
│  └────────────────────────────────┘ │
└────────┬─────────────────────────────┘
         │
         ▼
Step 5: User Clicks Link in Email
┌──────────────────────────────────────┐
│  Email Link:                         │
│  http://localhost:5173/reset-password│
│  #access_token=abc123...             │
│  &type=recovery                      │
└────────┬─────────────────────────────┘
         │
         ▼
Step 6: Reset Password Page
┌──────────────────┐
│  Reset Password  │
│  Page            │
│                  │
│  New Password:   │
│  ┌────────────┐  │
│  │••••••••••  │  │
│  └────────────┘  │
│                  │
│  Confirm:        │
│  ┌────────────┐  │
│  │••••••••••  │  │
│  └────────────┘  │
│                  │
│  [Update         │
│   Password]      │
└────────┬─────────┘
         │
         ▼
Step 7: Password Updated
┌──────────────────┐
│  Success!        │
│  ✅ Password     │
│     updated      │
│                  │
│  Redirecting to  │
│  login...        │
└────────┬─────────┘
         │
         ▼
Step 8: Login with New Password
┌──────────────────┐
│  Login Page      │
│                  │
│  [Email]         │
│  [New Password]  │
│                  │
│  [Sign In] ✅    │
└──────────────────┘
```

---

## 🔧 Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM COMPONENTS                            │
└─────────────────────────────────────────────────────────────────┘

Frontend (React)
├── Login.jsx
│   └── "Forgot Password?" button
│   └── Calls: resetPassword(email)
│
├── ResetPassword.jsx
│   └── New password form
│   └── Calls: updatePassword(newPassword)
│
└── AuthContext.jsx
    └── resetPassword(email)
        └── supabase.auth.resetPasswordForEmail(email, {
            redirectTo: 'http://localhost:5173/reset-password'
        })

Backend (Supabase)
├── Authentication Service
│   ├── Validates email exists
│   ├── Generates secure token (JWT)
│   ├── Creates reset URL with token
│   └── Sends to SMTP service
│
└── SMTP Configuration
    ├── Host: smtp.sendgrid.net
    ├── Port: 587
    ├── Username: apikey
    └── Password: [SendGrid API Key]

Email Service (SendGrid)
├── Receives email from Supabase
├── Delivers to user's inbox
└── Tracks delivery status

Security
├── Token expires in 1 hour
├── Token can only be used once
├── HTTPS only for reset links
└── Rate limiting: 1 email per 60 seconds
```

---

## 📝 Code Flow

### 1. User Clicks "Forgot Password"
```javascript
// Login.jsx
const handleResetPassword = async (event) => {
  event.preventDefault()
  const { error } = await resetPassword(email)
  
  if (error) {
    setError('Error sending recovery email')
  } else {
    setMessage('Password reset email sent!')
  }
}
```

### 2. AuthContext Calls Supabase
```javascript
// AuthContext.jsx
const resetPassword = async (email) => {
  const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/reset-password`,
  })
  return { data, error }
}
```

### 3. Supabase Sends Email via SendGrid
```
Supabase → SendGrid SMTP → User's Email Inbox
```

### 4. User Clicks Link → Redirected to Reset Page
```
Email Link: http://localhost:5173/reset-password#access_token=...&type=recovery
                                                    ↓
                                        ResetPassword.jsx loads
```

### 5. User Enters New Password
```javascript
// ResetPassword.jsx
const handleResetPassword = async (event) => {
  event.preventDefault()
  
  // Validate passwords match
  if (newPassword !== confirmPassword) {
    setError('Passwords do not match')
    return
  }
  
  // Update password
  const { error } = await updatePassword(newPassword)
  
  if (!error) {
    setMessage('Password updated successfully!')
    navigate('/login')
  }
}
```

### 6. AuthContext Updates Password
```javascript
// AuthContext.jsx
const updatePassword = async (newPassword) => {
  const { data, error } = await supabase.auth.updateUser({
    password: newPassword
  })
  return { data, error }
}
```

---

## 🔐 Security Features

### Token Security
- ✅ Cryptographically secure random token
- ✅ Expires after 1 hour
- ✅ Single-use only (can't be reused)
- ✅ Tied to specific user account

### Email Security
- ✅ Only sent to registered email addresses
- ✅ Invalid emails fail silently (prevents enumeration)
- ✅ Rate limited (1 per 60 seconds per user)
- ✅ HTTPS links only

### Password Security
- ✅ Minimum 6 characters (configurable)
- ✅ Confirmation required (must match)
- ✅ Hashed before storage (bcrypt)
- ✅ Never sent in plain text

### Network Security
- ✅ SMTP over TLS (port 587)
- ✅ API keys never exposed to frontend
- ✅ Secure token transmission
- ✅ CORS protection

---

## 📊 Configuration Checklist

### SendGrid Setup
- [ ] Account created
- [ ] API key generated (Mail Send permission)
- [ ] Sender email verified
- [ ] Activity monitoring enabled

### Supabase Setup
- [ ] SMTP settings configured
- [ ] Email templates customized
- [ ] Redirect URLs whitelisted
- [ ] Rate limits configured

### Testing
- [ ] Password reset email received
- [ ] Reset link works
- [ ] New password accepted
- [ ] Login works with new password
- [ ] Error handling tested

---

## 🎯 User Experience

### Success Path
```
1. User: "I forgot my password"
   ↓
2. User: Clicks "Forgot Password?"
   ↓
3. User: Enters email → Clicks "Send"
   ↓
4. System: "Password reset email sent! Check your inbox"
   ↓
5. User: Checks email → Clicks reset link
   ↓
6. User: Enters new password (twice)
   ↓
7. System: "Password updated successfully!"
   ↓
8. User: Logs in with new password ✅
```

### Error Handling
```
Invalid Email:
→ "Error sending recovery email. Please contact your administrator."

Passwords Don't Match:
→ "Passwords do not match"

Password Too Short:
→ "Password must be at least 6 characters long"

Expired Link:
→ "Invalid or expired password reset link. Please request a new one."

Rate Limited:
→ "Please wait 60 seconds before requesting another reset email"
```

---

## 🚀 Quick Reference

### SendGrid SMTP Settings
```
Host: smtp.sendgrid.net
Port: 587
Username: apikey
Password: SG.your_api_key_here
```

### Supabase URLs
```
Project: https://hsbcjonzbnwjnftfohyk.supabase.co
Dashboard: https://app.supabase.com
```

### Local Development
```
Frontend: http://localhost:5173
Reset Page: http://localhost:5173/reset-password
Login Page: http://localhost:5173/login
```

### Important Files
```
frontend/src/components/Login.jsx          - Forgot password button
frontend/src/components/ResetPassword.jsx  - Reset password page
frontend/src/contexts/AuthContext.jsx      - Auth functions
frontend/src/App.jsx                       - Routing
```

---

## 📞 Support

**Supabase Auth Logs:**
Dashboard → Logs → Auth Logs

**SendGrid Activity:**
Dashboard → Activity → Email Activity

**Browser Console:**
F12 → Console tab (for frontend errors)

---

**Status**: ✅ Fully implemented - Just needs SendGrid configuration!
