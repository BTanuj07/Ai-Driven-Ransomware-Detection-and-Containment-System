import { useState, useEffect } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { apiClient } from '../lib/api'
import { useAuth } from '../contexts/AuthContext'

const MFASetup = ({ onClose, onSuccess }) => {
  const { user } = useAuth()
  const [step, setStep] = useState(1) // 1: QR Code, 2: Verify, 3: Backup Codes
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [mfaData, setMfaData] = useState(null)
  const [verificationCode, setVerificationCode] = useState('')

  useEffect(() => {
    setupMFA()
  }, [])

  const setupMFA = async () => {
    try {
      setLoading(true)
      setError('')
      
      const response = await apiClient.post('/api/mfa/setup', {
        user_id: user?.id || user?.email
      })
      
      setMfaData(response.data)
      setLoading(false)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to setup MFA')
      setLoading(false)
    }
  }

  const verifyAndEnable = async () => {
    if (verificationCode.length !== 6) {
      setError('Please enter a 6-digit code')
      return
    }

    try {
      setLoading(true)
      setError('')
      
      await apiClient.post('/api/mfa/enable', {
        user_id: user?.id || user?.email,
        token: verificationCode
      })
      
      setStep(3) // Show backup codes
      setLoading(false)
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid verification code')
      setLoading(false)
    }
  }

  const handleFinish = () => {
    if (onSuccess) onSuccess()
    if (onClose) onClose()
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  if (loading && !mfaData) {
    return (
      <div className="mfa-setup-modal">
        <div className="mfa-setup-content">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔐</div>
            <p>Setting up MFA...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="mfa-setup-modal" onClick={onClose}>
      <div className="mfa-setup-content" onClick={(e) => e.stopPropagation()}>
        <div className="mfa-setup-header">
          <h2>🔐 Enable Two-Factor Authentication</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {error && (
          <div className="error-message" style={{
            padding: '12px',
            background: '#ef444422',
            border: '1px solid #ef4444',
            borderRadius: '8px',
            color: '#ef4444',
            marginBottom: '20px'
          }}>
            {error}
          </div>
        )}

        {/* Step 1: Scan QR Code */}
        {step === 1 && mfaData && (
          <div className="mfa-step">
            <div className="step-indicator">Step 1 of 3</div>
            <h3>Scan QR Code</h3>
            <p style={{ marginBottom: '20px', color: '#8fa0b6' }}>
              Scan this QR code with Google Authenticator or Microsoft Authenticator
            </p>

            <div style={{
              display: 'flex',
              justifyContent: 'center',
              padding: '20px',
              background: '#fff',
              borderRadius: '12px',
              marginBottom: '20px'
            }}>
              <QRCodeSVG 
                value={mfaData.provisioning_uri} 
                size={200}
                level="H"
              />
            </div>

            <div style={{
              padding: '16px',
              background: '#0f172a',
              borderRadius: '8px',
              marginBottom: '20px'
            }}>
              <p style={{ fontSize: '12px', color: '#8fa0b6', marginBottom: '8px' }}>
                Can't scan? Enter this code manually:
              </p>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                <code style={{
                  flex: 1,
                  padding: '8px 12px',
                  background: '#1e293b',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontFamily: 'monospace',
                  color: '#fff'
                }}>
                  {mfaData.secret}
                </code>
                <button
                  onClick={() => copyToClipboard(mfaData.secret)}
                  style={{
                    padding: '8px 16px',
                    background: '#3b82f6',
                    border: 'none',
                    borderRadius: '6px',
                    color: '#fff',
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  Copy
                </button>
              </div>
            </div>

            <button
              onClick={() => setStep(2)}
              style={{
                width: '100%',
                padding: '12px',
                background: '#10b981',
                border: 'none',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              Next: Verify Code
            </button>
          </div>
        )}

        {/* Step 2: Verify Code */}
        {step === 2 && (
          <div className="mfa-step">
            <div className="step-indicator">Step 2 of 3</div>
            <h3>Verify Authentication Code</h3>
            <p style={{ marginBottom: '20px', color: '#8fa0b6' }}>
              Enter the 6-digit code from your authenticator app
            </p>

            <input
              type="text"
              maxLength="6"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
              placeholder="000000"
              style={{
                width: '100%',
                padding: '16px',
                fontSize: '24px',
                textAlign: 'center',
                letterSpacing: '8px',
                fontFamily: 'monospace',
                background: '#0f172a',
                border: '2px solid #334155',
                borderRadius: '8px',
                color: '#fff',
                marginBottom: '20px'
              }}
              autoFocus
            />

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => setStep(1)}
                style={{
                  flex: 1,
                  padding: '12px',
                  background: '#334155',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '16px',
                  cursor: 'pointer'
                }}
              >
                Back
              </button>
              <button
                onClick={verifyAndEnable}
                disabled={loading || verificationCode.length !== 6}
                style={{
                  flex: 2,
                  padding: '12px',
                  background: verificationCode.length === 6 ? '#10b981' : '#334155',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  cursor: verificationCode.length === 6 ? 'pointer' : 'not-allowed',
                  opacity: verificationCode.length === 6 ? 1 : 0.5
                }}
              >
                {loading ? 'Verifying...' : 'Verify & Enable'}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Backup Codes */}
        {step === 3 && mfaData && (
          <div className="mfa-step">
            <div className="step-indicator">Step 3 of 3</div>
            <h3>✅ MFA Enabled Successfully!</h3>
            <p style={{ marginBottom: '20px', color: '#8fa0b6' }}>
              Save these backup codes in a secure location. You can use them to access your account if you lose your authenticator device.
            </p>

            <div style={{
              padding: '20px',
              background: '#0f172a',
              borderRadius: '8px',
              marginBottom: '20px'
            }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '12px'
              }}>
                {mfaData.backup_codes.map((code, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '12px',
                      background: '#1e293b',
                      borderRadius: '6px',
                      textAlign: 'center',
                      fontFamily: 'monospace',
                      fontSize: '14px',
                      color: '#fff'
                    }}
                  >
                    {code}
                  </div>
                ))}
              </div>
            </div>

            <div style={{
              padding: '16px',
              background: '#f59e0b22',
              border: '1px solid #f59e0b',
              borderRadius: '8px',
              marginBottom: '20px'
            }}>
              <p style={{ fontSize: '14px', color: '#f59e0b', margin: 0 }}>
                ⚠️ <strong>Important:</strong> Each backup code can only be used once. Store them securely!
              </p>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => copyToClipboard(mfaData.backup_codes.join('\n'))}
                style={{
                  flex: 1,
                  padding: '12px',
                  background: '#3b82f6',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '16px',
                  cursor: 'pointer'
                }}
              >
                Copy Codes
              </button>
              <button
                onClick={handleFinish}
                style={{
                  flex: 1,
                  padding: '12px',
                  background: '#10b981',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                Finish
              </button>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .mfa-setup-modal {
          position: fixed;
          inset: 0;
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(0, 0, 0, 0.7);
          backdrop-filter: blur(4px);
        }

        .mfa-setup-content {
          width: 90%;
          max-width: 500px;
          max-height: 90vh;
          overflow-y: auto;
          padding: 32px;
          background: #0a1628;
          border: 1px solid rgba(99, 121, 150, 0.24);
          border-radius: 12px;
        }

        .mfa-setup-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
        }

        .mfa-setup-header h2 {
          margin: 0;
          font-size: 24px;
          color: #fff;
        }

        .close-button {
          width: 32px;
          height: 32px;
          background: #334155;
          border: none;
          border-radius: 6px;
          color: #fff;
          font-size: 24px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .close-button:hover {
          background: #475569;
        }

        .step-indicator {
          padding: 6px 12px;
          background: #3b82f622;
          border: 1px solid #3b82f6;
          border-radius: 6px;
          color: #3b82f6;
          font-size: 12px;
          font-weight: 600;
          display: inline-block;
          margin-bottom: 16px;
        }

        .mfa-step h3 {
          margin: 0 0 8px 0;
          font-size: 20px;
          color: #fff;
        }
      `}</style>
    </div>
  )
}

export default MFASetup
