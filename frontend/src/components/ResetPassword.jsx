import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const SignInIcon = ({ type }) => {
  const common = {
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round',
    strokeLinejoin: 'round'
  }

  const icons = {
    shield: <path d="M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6l-7-3Z" />,
    lock: <><rect x="5" y="10" width="14" height="10" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></>,
    eyeOff: <><path d="M3 3l18 18" /><path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" /><path d="M9.9 4.2A10.7 10.7 0 0 1 12 4c5 0 8.5 4.5 10 8a15.1 15.1 0 0 1-3.1 4.5" /><path d="M6.5 6.5A15.4 15.4 0 0 0 2 12c1.5 3.5 5 8 10 8 1.5 0 2.9-.4 4.1-1" /></>,
    arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>
  }

  return <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>{icons[type]}</svg>
}

const ResetPassword = () => {
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [message, setMessage] = useState(null)
  const navigate = useNavigate()
  const { updatePassword } = useAuth()

  useEffect(() => {
    // Check if we have a valid recovery token in the URL
    const hashParams = new URLSearchParams(window.location.hash.substring(1))
    const accessToken = hashParams.get('access_token')
    const type = hashParams.get('type')

    if (!accessToken || type !== 'recovery') {
      setError('Invalid or expired password reset link. Please request a new one.')
    }
  }, [])

  const handleResetPassword = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    setMessage(null)

    // Validation
    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters long')
      setLoading(false)
      return
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    try {
      const { error } = await updatePassword(newPassword)

      if (error) {
        setError(error.message || 'Failed to update password')
      } else {
        setMessage('Password updated successfully! Redirecting to login...')
        setTimeout(() => {
          navigate('/login')
        }, 2000)
      }
    } catch (err) {
      setError('An error occurred. Please try again.')
      console.error('Password update error:', err)
    }

    setLoading(false)
  }

  return (
    <main className="signin-page">
      <section className="signin-shell">
        <div className="signin-visual">
          <div className="signin-brand">
            <div className="signin-brand-mark">
              <img 
                src="/arcs-brand.png" 
                alt="ARCS Logo" 
                style={{ width: '80px', height: '80px', objectFit: 'contain', borderRadius: '50%' }}
                onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'block'; }}
              />
              <div style={{ display: 'none' }}><SignInIcon type="shield" /></div>
            </div>
            <div>
              <h1>ARCS</h1>
              <p>AI-Driven Ransomware Detection & Containment System</p>
            </div>
          </div>

          <div className="signin-copy">
            <h2>
              Reset Your Password
              <span>Secure Your Account</span>
            </h2>
            <p>Choose a strong password to protect your account.</p>
          </div>

          <div className="security-illustration" aria-hidden="true">
            <div className="grid-plane" />
            <div className="central-platform">
              <span className="ring ring-one" />
              <span className="ring ring-two" />
              <div className="glow-shield">
                <SignInIcon type="shield" />
                <span />
              </div>
            </div>
          </div>
        </div>

        <form className="signin-card" onSubmit={handleResetPassword}>
          <div className="signin-heading">
            <h2>Set New Password</h2>
            <p>Enter your new password below</p>
          </div>

          {error && <div className="signin-alert error">{error}</div>}
          {message && <div className="signin-alert success">{message}</div>}

          <label className="signin-field">
            <span>New Password</span>
            <div>
              <SignInIcon type="lock" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={newPassword}
                onChange={(event) => setNewPassword(event.target.value)}
                required
                placeholder="Enter new password (min 6 characters)"
                minLength={6}
              />
              <button 
                type="button" 
                className="password-toggle" 
                onClick={() => setShowPassword(!showPassword)} 
                aria-label="Toggle password visibility"
              >
                <SignInIcon type="eyeOff" />
              </button>
            </div>
          </label>

          <label className="signin-field">
            <span>Confirm Password</span>
            <div>
              <SignInIcon type="lock" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
                placeholder="Confirm new password"
                minLength={6}
              />
            </div>
          </label>

          <button className="signin-submit" type="submit" disabled={loading}>
            <span>{loading ? 'Updating...' : 'Update Password'}</span>
            <SignInIcon type="arrow" />
          </button>

          <p className="signin-switch">
            <button type="button" onClick={() => navigate('/login')}>
              Back to sign in
            </button>
          </p>
        </form>
      </section>

      <footer className="signin-footer">
        <p><SignInIcon type="shield" />Secure. Intelligent. Autonomous.</p>
        <span>© 2026 ARCS Security System. All rights reserved.</span>
      </footer>
    </main>
  )
}

export default ResetPassword
