import { useState, useEffect } from 'react'
import { apiClient } from '../lib/api'
import { supabase } from '../lib/supabase'
import { useAuth } from '../contexts/AuthContext'
import MFASetup from './MFASetup'

const Icon = ({ type }) => {
  const common = { fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round', width: '20px', height: '20px' }
  const paths = {
    shield: <path d="M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6l-7-3Z" />,
    bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 6-3 9h18c0-3-3-2-3-9" /><path d="M10 21h4" /></>,
    bolt: <path d="m13 2-8 12h7l-1 8 8-12h-7l1-8Z" />,
    database: <><ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" /><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" /></>,
    server: <><rect x="2" y="2" width="20" height="8" rx="2" ry="2" /><rect x="2" y="14" width="20" height="8" rx="2" ry="2" /><line x1="6" y1="6" x2="6.01" y2="6" /><line x1="6" y1="18" x2="6.01" y2="18" /></>,
    check: <polyline points="20 6 9 17 4 12" />,
    x: <><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></>,
    save: <><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" /><polyline points="17 21 17 13 7 13 7 21" /><polyline points="7 3 7 8 15 8" /></>,
    mail: <><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" /><polyline points="22,6 12,13 2,6" /></>,
    phone: <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
  }
  return <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>{paths[type]}</svg>
}

const SettingsModule = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [showMFASetup, setShowMFASetup] = useState(false)
  const [mfaEnabled, setMfaEnabled] = useState(false)
  const [mfaLoading, setMfaLoading] = useState(false)
  
  // Detection Threshold Settings
  const [anomalyThreshold, setAnomalyThreshold] = useState(0.75)
  const [highRiskThreshold, setHighRiskThreshold] = useState(0.8)
  const [mediumRiskThreshold, setMediumRiskThreshold] = useState(0.6)
  const [lowRiskThreshold, setLowRiskThreshold] = useState(0.4)
  const [falsePositiveSensitivity, setFalsePositiveSensitivity] = useState(0.65)
  const [modelConfidence, setModelConfidence] = useState(0.85)

  // Automated Response Policy
  const [autoIsolate, setAutoIsolate] = useState(true)
  const [autoKillProcess, setAutoKillProcess] = useState(true)
  const [autoDisableUser, setAutoDisableUser] = useState(false)
  const [requireApproval, setRequireApproval] = useState(true)

  // Notification Settings
  const [emailAlerts, setEmailAlerts] = useState(true)
  const [smsAlerts, setSmsAlerts] = useState(false)
  const [criticalEscalation, setCriticalEscalation] = useState(true)
  const [emailAddress, setEmailAddress] = useState('admin@arcs.local')
  const [phoneNumber, setPhoneNumber] = useState('+1 (555) 123-4567')

  // Service Status from backend
  const [services, setServices] = useState({})

  const [saveStatus, setSaveStatus] = useState(null)

  // Fetch settings from backend
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true)
        
        // Get token from Supabase session
        const { data: { session } } = await supabase.auth.getSession()
        const token = session?.access_token
        const headers = token ? { Authorization: `Bearer ${token}` } : {}

        const [settingsRes, servicesRes] = await Promise.all([
          apiClient.get('/api/settings', { headers }),
          apiClient.get('/api/settings/services', { headers })
        ])

        const settings = settingsRes.data.settings || {}
        
        // Update state with backend data
        if (settings.anomalyThreshold !== undefined) setAnomalyThreshold(settings.anomalyThreshold)
        if (settings.highRiskThreshold !== undefined) setHighRiskThreshold(settings.highRiskThreshold)
        if (settings.mediumRiskThreshold !== undefined) setMediumRiskThreshold(settings.mediumRiskThreshold)
        if (settings.lowRiskThreshold !== undefined) setLowRiskThreshold(settings.lowRiskThreshold)
        if (settings.falsePositiveSensitivity !== undefined) setFalsePositiveSensitivity(settings.falsePositiveSensitivity)
        if (settings.modelConfidence !== undefined) setModelConfidence(settings.modelConfidence)
        if (settings.autoIsolate !== undefined) setAutoIsolate(settings.autoIsolate)
        if (settings.autoKillProcess !== undefined) setAutoKillProcess(settings.autoKillProcess)
        if (settings.autoDisableUser !== undefined) setAutoDisableUser(settings.autoDisableUser)
        if (settings.requireApproval !== undefined) setRequireApproval(settings.requireApproval)
        if (settings.emailAlerts !== undefined) setEmailAlerts(settings.emailAlerts)
        if (settings.smsAlerts !== undefined) setSmsAlerts(settings.smsAlerts)
        if (settings.criticalEscalation !== undefined) setCriticalEscalation(settings.criticalEscalation)
        if (settings.emailAddress) setEmailAddress(settings.emailAddress)
        if (settings.phoneNumber) setPhoneNumber(settings.phoneNumber)

        setServices(servicesRes.data.services || {})
        
        // Check MFA status
        if (user?.id) {
          try {
            const mfaRes = await apiClient.get(`/api/mfa/status/${user.id}`, { headers })
            setMfaEnabled(mfaRes.data.enabled || false)
          } catch (err) {
            console.error('Failed to fetch MFA status:', err)
          }
        }
      } catch (error) {
        console.error('Failed to fetch settings:', error)
        // Set default services on error
        setServices({
          kafka: { status: 'unknown', uptime: 'N/A', messages: 'N/A' },
          mongodb: { status: 'unknown', uptime: 'N/A', connections: 0 },
          backend: { status: 'unknown', uptime: 'N/A', requests: 'N/A' },
          mlEngine: { status: 'unknown', uptime: 'N/A', predictions: 'N/A' }
        })
      } finally {
        setLoading(false)
      }
    }

    fetchSettings()
  }, [user])

  const handleSave = async () => {
    setSaveStatus('saving')
    
    try {
      // Get token from Supabase session
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token
      const headers = token ? { Authorization: `Bearer ${token}` } : {}

      const settingsData = {
        anomalyThreshold,
        highRiskThreshold,
        mediumRiskThreshold,
        lowRiskThreshold,
        falsePositiveSensitivity,
        modelConfidence,
        autoIsolate,
        autoKillProcess,
        autoDisableUser,
        requireApproval,
        emailAlerts,
        smsAlerts,
        criticalEscalation,
        emailAddress,
        phoneNumber
      }

      await apiClient.post('/api/settings', settingsData, { headers })
      
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus(null), 3000)
    } catch (error) {
      console.error('Failed to save settings:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus(null), 3000)
    }
  }

  const handleMFASetupComplete = () => {
    setShowMFASetup(false)
    setMfaEnabled(true)
  }

  const handleDisableMFA = async () => {
    if (!window.confirm('Are you sure you want to disable Two-Factor Authentication? This will make your account less secure.')) {
      return
    }

    const code = window.prompt('Enter your current 6-digit TOTP code to disable MFA:')
    if (!code) return

    try {
      setMfaLoading(true)
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token
      const headers = token ? { Authorization: `Bearer ${token}` } : {}

      await apiClient.post('/api/mfa/disable', {
        user_id: user?.id,
        token: code
      }, { headers })

      setMfaEnabled(false)
      alert('Two-Factor Authentication has been disabled.')
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to disable MFA. Please check your code.')
    } finally {
      setMfaLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="settings-module" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚙️</div>
          <p style={{ color: '#8fa0b6' }}>Loading settings...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      {showMFASetup && (
        <MFASetup 
          onClose={() => setShowMFASetup(false)}
          onSuccess={handleMFASetupComplete}
        />
      )}
      
      <div className="settings-module">
      {/* Header */}
      <div className="module-header">
        <div>
          <h1>System Settings</h1>
          <p>Configure detection thresholds, automated responses, and system parameters</p>
        </div>
        <button 
          className={`btn-save ${saveStatus === 'saved' ? 'saved' : ''}`}
          onClick={handleSave}
          disabled={saveStatus === 'saving'}
        >
          <Icon type="save" />
          {saveStatus === 'saving' ? 'Saving...' : saveStatus === 'saved' ? 'Saved!' : 'Save Configuration'}
        </button>
      </div>

      <div className="settings-grid">
        {/* Detection Threshold Settings */}
        <section className="settings-card">
          <div className="card-header">
            <Icon type="shield" />
            <h2>Detection Threshold Settings</h2>
          </div>
          <div className="settings-content">
            <div className="setting-item">
              <div className="setting-label">
                <span>Anomaly Score Threshold</span>
                <span className="setting-value">{(anomalyThreshold * 100).toFixed(0)}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01" 
                value={anomalyThreshold}
                onChange={(e) => setAnomalyThreshold(parseFloat(e.target.value))}
                className="slider"
              />
              <p className="setting-help">Minimum score to trigger anomaly detection</p>
            </div>

            <div className="setting-item">
              <div className="setting-label">
                <span>HIGH Risk Threshold</span>
                <span className="setting-value danger">{(highRiskThreshold * 100).toFixed(0)}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01" 
                value={highRiskThreshold}
                onChange={(e) => setHighRiskThreshold(parseFloat(e.target.value))}
                className="slider danger"
              />
              <p className="setting-help">Score above this triggers HIGH risk classification</p>
            </div>

            <div className="setting-item">
              <div className="setting-label">
                <span>MEDIUM Risk Threshold</span>
                <span className="setting-value warning">{(mediumRiskThreshold * 100).toFixed(0)}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01" 
                value={mediumRiskThreshold}
                onChange={(e) => setMediumRiskThreshold(parseFloat(e.target.value))}
                className="slider warning"
              />
              <p className="setting-help">Score above this triggers MEDIUM risk classification</p>
            </div>

            <div className="setting-item">
              <div className="setting-label">
                <span>LOW Risk Threshold</span>
                <span className="setting-value success">{(lowRiskThreshold * 100).toFixed(0)}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01" 
                value={lowRiskThreshold}
                onChange={(e) => setLowRiskThreshold(parseFloat(e.target.value))}
                className="slider success"
              />
              <p className="setting-help">Score above this triggers LOW risk classification</p>
            </div>

            <div className="setting-item">
              <div className="setting-label">
                <span>False Positive Sensitivity</span>
                <span className="setting-value">{(falsePositiveSensitivity * 100).toFixed(0)}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01" 
                value={falsePositiveSensitivity}
                onChange={(e) => setFalsePositiveSensitivity(parseFloat(e.target.value))}
                className="slider"
              />
              <p className="setting-help">Higher values reduce false positives but may miss threats</p>
            </div>

            <div className="setting-item">
              <div className="setting-label">
                <span>Model Confidence Threshold</span>
                <span className="setting-value">{(modelConfidence * 100).toFixed(0)}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01" 
                value={modelConfidence}
                onChange={(e) => setModelConfidence(parseFloat(e.target.value))}
                className="slider"
              />
              <p className="setting-help">Minimum ML model confidence to trigger alerts</p>
            </div>
          </div>
        </section>

        {/* Automated Response Policy */}
        <section className="settings-card">
          <div className="card-header">
            <Icon type="bolt" />
            <h2>Automated Response Policy</h2>
          </div>
          <div className="settings-content">
            <div className="toggle-item">
              <div className="toggle-info">
                <strong>Auto-Isolate Endpoint</strong>
                <p>Automatically isolate infected endpoints from network</p>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={autoIsolate}
                  onChange={(e) => setAutoIsolate(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="toggle-item">
              <div className="toggle-info">
                <strong>Auto-Kill Suspicious Process</strong>
                <p>Terminate processes identified as malicious</p>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={autoKillProcess}
                  onChange={(e) => setAutoKillProcess(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="toggle-item">
              <div className="toggle-info">
                <strong>Auto-Disable User Account</strong>
                <p>Disable compromised user accounts automatically</p>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={autoDisableUser}
                  onChange={(e) => setAutoDisableUser(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="toggle-item">
              <div className="toggle-info">
                <strong>Require Admin Approval</strong>
                <p>Require manual approval before executing response actions</p>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={requireApproval}
                  onChange={(e) => setRequireApproval(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="policy-preview">
              <h4>Current Policy Preview</h4>
              <ul className="policy-list">
                <li className={autoIsolate ? 'enabled' : 'disabled'}>
                  <Icon type={autoIsolate ? 'check' : 'x'} />
                  Endpoint Isolation: {autoIsolate ? 'Enabled' : 'Disabled'}
                </li>
                <li className={autoKillProcess ? 'enabled' : 'disabled'}>
                  <Icon type={autoKillProcess ? 'check' : 'x'} />
                  Process Termination: {autoKillProcess ? 'Enabled' : 'Disabled'}
                </li>
                <li className={autoDisableUser ? 'enabled' : 'disabled'}>
                  <Icon type={autoDisableUser ? 'check' : 'x'} />
                  User Account Disable: {autoDisableUser ? 'Enabled' : 'Disabled'}
                </li>
                <li className={requireApproval ? 'enabled' : 'disabled'}>
                  <Icon type={requireApproval ? 'check' : 'x'} />
                  Admin Approval: {requireApproval ? 'Required' : 'Not Required'}
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Service Status */}
        <section className="settings-card">
          <div className="card-header">
            <Icon type="server" />
            <h2>Backend Service Status</h2>
          </div>
          <div className="settings-content">
            <div className="service-item">
              <div className="service-info">
                <div className="service-name">
                  <span className="status-dot running"></span>
                  <strong>Kafka Message Broker</strong>
                </div>
                <div className="service-stats">
                  <span>Uptime: {services.kafka.uptime}</span>
                  <span>Messages: {services.kafka.messages}</span>
                </div>
              </div>
              <span className="service-status running">Running</span>
            </div>

            <div className="service-item">
              <div className="service-info">
                <div className="service-name">
                  <span className="status-dot running"></span>
                  <strong>MongoDB Database</strong>
                </div>
                <div className="service-stats">
                  <span>Uptime: {services.mongodb.uptime}</span>
                  <span>Connections: {services.mongodb.connections}</span>
                </div>
              </div>
              <span className="service-status running">Running</span>
            </div>

            <div className="service-item">
              <div className="service-info">
                <div className="service-name">
                  <span className="status-dot running"></span>
                  <strong>FastAPI Backend</strong>
                </div>
                <div className="service-stats">
                  <span>Uptime: {services.backend.uptime}</span>
                  <span>Requests: {services.backend.requests}</span>
                </div>
              </div>
              <span className="service-status running">Running</span>
            </div>

            <div className="service-item">
              <div className="service-info">
                <div className="service-name">
                  <span className="status-dot running"></span>
                  <strong>ML Detection Engine</strong>
                </div>
                <div className="service-stats">
                  <span>Uptime: {services.mlEngine.uptime}</span>
                  <span>Predictions: {services.mlEngine.predictions}</span>
                </div>
              </div>
              <span className="service-status running">Running</span>
            </div>
          </div>
        </section>

        {/* Notification Settings */}
        <section className="settings-card">
          <div className="card-header">
            <Icon type="bell" />
            <h2>Notification Settings</h2>
          </div>
          <div className="settings-content">
            <div className="toggle-item">
              <div className="toggle-info">
                <strong>Email Alerts</strong>
                <p>Receive email notifications for security events</p>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={emailAlerts}
                  onChange={(e) => setEmailAlerts(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            {emailAlerts && (
              <div className="input-group">
                <label>Email Address</label>
                <div className="input-with-icon">
                  <Icon type="mail" />
                  <input 
                    type="email" 
                    value={emailAddress}
                    onChange={(e) => setEmailAddress(e.target.value)}
                    placeholder="admin@arcs.local"
                  />
                </div>
              </div>
            )}

            <div className="toggle-item">
              <div className="toggle-info">
                <strong>SMS Alerts</strong>
                <p>Receive SMS notifications for critical threats</p>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={smsAlerts}
                  onChange={(e) => setSmsAlerts(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            {smsAlerts && (
              <div className="input-group">
                <label>Phone Number</label>
                <div className="input-with-icon">
                  <Icon type="phone" />
                  <input 
                    type="tel" 
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
              </div>
            )}

            <div className="toggle-item">
              <div className="toggle-info">
                <strong>Critical Alert Escalation</strong>
                <p>Escalate HIGH risk alerts to security team immediately</p>
              </div>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={criticalEscalation}
                  onChange={(e) => setCriticalEscalation(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        </section>

        {/* MFA Security Settings */}
        <section className="settings-card">
          <div className="card-header">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px' }}>
              <rect x="5" y="11" width="14" height="10" rx="2" ry="2" />
              <circle cx="12" cy="16" r="1" />
              <path d="M8 11V7a4 4 0 0 1 8 0v4" />
            </svg>
            <h2>Two-Factor Authentication (MFA)</h2>
          </div>
          <div className="settings-content">
            <div style={{ 
              padding: '20px', 
              background: mfaEnabled ? '#10b98122' : '#f59e0b22',
              border: `1px solid ${mfaEnabled ? '#10b981' : '#f59e0b'}`,
              borderRadius: '8px',
              marginBottom: '20px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <div style={{ fontSize: '32px' }}>{mfaEnabled ? '🔐' : '⚠️'}</div>
                <div>
                  <strong style={{ color: '#fff', fontSize: '16px' }}>
                    {mfaEnabled ? 'MFA is Enabled' : 'MFA is Disabled'}
                  </strong>
                  <p style={{ margin: '4px 0 0 0', color: '#8fa0b6', fontSize: '14px' }}>
                    {mfaEnabled 
                      ? 'Your account is protected with Two-Factor Authentication'
                      : 'Enable MFA to add an extra layer of security to your account'
                    }
                  </p>
                </div>
              </div>
            </div>

            {!mfaEnabled ? (
              <div>
                <h4 style={{ color: '#fff', marginBottom: '12px' }}>Why enable MFA?</h4>
                <ul style={{ color: '#8fa0b6', fontSize: '14px', lineHeight: '1.8', marginBottom: '20px' }}>
                  <li>Adds an extra layer of security beyond passwords</li>
                  <li>Protects against unauthorized access even if password is compromised</li>
                  <li>Uses time-based codes from Google Authenticator or Microsoft Authenticator</li>
                  <li>Includes backup codes for account recovery</li>
                </ul>
                <button
                  onClick={() => setShowMFASetup(true)}
                  style={{
                    padding: '12px 24px',
                    background: '#10b981',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                >
                  Enable Two-Factor Authentication
                </button>
              </div>
            ) : (
              <div>
                <h4 style={{ color: '#fff', marginBottom: '12px' }}>MFA Status</h4>
                <div style={{ 
                  display: 'flex', 
                  gap: '12px',
                  marginBottom: '20px'
                }}>
                  <div style={{
                    flex: 1,
                    padding: '16px',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}>
                    <div style={{ color: '#8fa0b6', fontSize: '12px', marginBottom: '4px' }}>Status</div>
                    <div style={{ color: '#10b981', fontSize: '16px', fontWeight: 'bold' }}>Active</div>
                  </div>
                  <div style={{
                    flex: 1,
                    padding: '16px',
                    background: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}>
                    <div style={{ color: '#8fa0b6', fontSize: '12px', marginBottom: '4px' }}>Method</div>
                    <div style={{ color: '#fff', fontSize: '16px', fontWeight: 'bold' }}>TOTP</div>
                  </div>
                </div>
                <button
                  onClick={handleDisableMFA}
                  disabled={mfaLoading}
                  style={{
                    padding: '12px 24px',
                    background: '#ef4444',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    cursor: mfaLoading ? 'not-allowed' : 'pointer',
                    opacity: mfaLoading ? 0.5 : 1
                  }}
                >
                  {mfaLoading ? 'Disabling...' : 'Disable MFA'}
                </button>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
    </>
  )
}

export default SettingsModule
