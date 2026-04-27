import { useState } from 'react'
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
    user: <><circle cx="12" cy="8" r="4" /><path d="M4 21c1.4-4 14.6-4 16 0" /></>,
    lock: <><rect x="5" y="10" width="14" height="10" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></>,
    eyeOff: <><path d="M3 3l18 18" /><path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" /><path d="M9.9 4.2A10.7 10.7 0 0 1 12 4c5 0 8.5 4.5 10 8a15.1 15.1 0 0 1-3.1 4.5" /><path d="M6.5 6.5A15.4 15.4 0 0 0 2 12c1.5 3.5 5 8 10 8 1.5 0 2.9-.4 4.1-1" /></>,
    arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
    brain: <><path d="M9 4a3 3 0 0 0-3 3v.5A3.5 3.5 0 0 0 4 14a3 3 0 0 0 3 3h2" /><path d="M15 4a3 3 0 0 1 3 3v.5A3.5 3.5 0 0 1 20 14a3 3 0 0 1-3 3h-2" /><path d="M9 4v16M15 4v16M9 9H7M15 9h2M9 14H7M15 14h2" /></>,
    bolt: <path d="m13 2-8 12h7l-1 8 8-12h-7l1-8Z" />,
    chart: <><path d="M5 19V9" /><path d="M12 19V5" /><path d="M19 19v-7" /></>
  }

  return <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>{icons[type]}</svg>
}

const FeatureTile = ({ icon, title, body }) => (
  <div className="signin-feature">
    <div><SignInIcon type={icon} /></div>
    <strong>{title}</strong>
    <span>{body}</span>
  </div>
)

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [message, setMessage] = useState(null)
  const [isResetMode, setIsResetMode] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const { signIn, resetPassword } = useAuth()

  const handleLogin = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    setMessage(null)

    const { error } = await signIn(email, password)

    if (error) {
      setError(error.message)
    }

    setLoading(false)
  }

  const handleResetPassword = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    setMessage(null)

    const { error } = await resetPassword(email)

    if (error) {
      setError(error.message)
    } else {
      setMessage('Password reset email sent. Check your inbox.')
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
              Intelligent Protection.
              <span>Autonomous Security.</span>
            </h2>
            <p>Detect, analyze, and respond to ransomware threats in real-time with AI-powered precision.</p>
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
            <div className="device device-one"><span /></div>
            <div className="device device-two"><span /></div>
            <div className="device device-three"><span /></div>
            <div className="device device-four"><span /></div>
            <div className="network-line line-one" />
            <div className="network-line line-two" />
            <div className="network-line line-three" />
            <div className="network-line line-four" />
          </div>

          <div className="signin-features">
            <FeatureTile icon="brain" title="AI-Powered" body="Detection" />
            <FeatureTile icon="shield" title="Real-time" body="Monitoring" />
            <FeatureTile icon="bolt" title="Automated" body="Response" />
            <FeatureTile icon="chart" title="Advanced" body="Analytics" />
          </div>
        </div>

        <form className="signin-card" onSubmit={isResetMode ? handleResetPassword : handleLogin}>
          <div className="signin-heading">
            <h2>{isResetMode ? 'Reset Password' : 'Welcome Back!'}</h2>
            <p>{isResetMode ? 'Enter your email to receive a reset link' : 'Sign in to continue to your dashboard'}</p>
          </div>

          {error && <div className="signin-alert error">{error}</div>}
          {message && <div className="signin-alert success">{message}</div>}

          <label className="signin-field">
            <span>Email Address</span>
            <div>
              <SignInIcon type="user" />
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                placeholder="Enter your email"
              />
            </div>
          </label>

          {!isResetMode && (
            <label className="signin-field">
              <span>Password</span>
              <div>
                <SignInIcon type="lock" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  placeholder="Enter your password"
                />
                <button type="button" className="password-toggle" onClick={() => setShowPassword(!showPassword)} aria-label="Toggle password visibility">
                  <SignInIcon type="eyeOff" />
                </button>
              </div>
            </label>
          )}

          {!isResetMode && (
            <div className="signin-row">
              <label className="remember-control">
                <input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} />
                <span />
                remember me
              </label>
              <button type="button" onClick={() => {
                setIsResetMode(true)
                setError(null)
                setMessage(null)
              }}>
                Forgot Password?
              </button>
            </div>
          )}

          <button className="signin-submit" type="submit" disabled={loading}>
            <span>{loading ? 'Please wait...' : isResetMode ? 'Send Reset Email' : 'Sign In'}</span>
            <SignInIcon type="arrow" />
          </button>

          <p className="signin-switch">
            {isResetMode ? (
              <>
                Remembered your password?
                <button type="button" onClick={() => {
                  setIsResetMode(false)
                  setError(null)
                  setMessage(null)
                }}>
                  Back to sign in
                </button>
              </>
            ) : (
              <>
                Don't have an account?
                <button type="button">Sign up</button>
              </>
            )}
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

export default Login
