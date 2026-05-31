import { useState } from 'react'
import { apiClient } from '../lib/api'

const MFAVerify = ({ userId, onSuccess, onCancel }) => {
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [useBackupCode, setUseBackupCode] = useState(false)

  const handleVerify = async () => {
    if (code.length < 6) {
      setError('Please enter a valid code')
      return
    }

    try {
      setLoading(true)
      setError('')
      
      await apiClient.post('/api/mfa/verify', {
        user_id: userId,
        token: code
      })
      
      // MFA verification successful
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid code. Please try again.')
      setLoading(false)
      setCode('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && code.length >= 6) {
      handleVerify()
    }
  }

  return (
    <div className="mfa-verify-container">
      <div className="mfa-verify-content">
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔐</div>
          <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', color: '#fff' }}>
            Two-Factor Authentication
          </h2>
          <p style={{ margin: 0, color: '#8fa0b6', fontSize: '14px' }}>
            {useBackupCode 
              ? 'Enter one of your backup codes'
              : 'Enter the 6-digit code from your authenticator app'
            }
          </p>
        </div>

        {error && (
          <div style={{
            padding: '12px',
            background: '#ef444422',
            border: '1px solid #ef4444',
            borderRadius: '8px',
            color: '#ef4444',
            marginBottom: '20px',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        <input
          type="text"
          maxLength={useBackupCode ? 8 : 6}
          value={code}
          onChange={(e) => setCode(e.target.value.replace(/\s/g, '').toUpperCase())}
          onKeyPress={handleKeyPress}
          placeholder={useBackupCode ? 'XXXXXXXX' : '000000'}
          style={{
            width: '100%',
            padding: '16px',
            fontSize: '24px',
            textAlign: 'center',
            letterSpacing: useBackupCode ? '4px' : '8px',
            fontFamily: 'monospace',
            background: '#0f172a',
            border: '2px solid #334155',
            borderRadius: '8px',
            color: '#fff',
            marginBottom: '20px'
          }}
          autoFocus
          disabled={loading}
        />

        <button
          onClick={handleVerify}
          disabled={loading || code.length < 6}
          style={{
            width: '100%',
            padding: '14px',
            background: code.length >= 6 ? '#10b981' : '#334155',
            border: 'none',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: code.length >= 6 ? 'pointer' : 'not-allowed',
            opacity: code.length >= 6 ? 1 : 0.5,
            marginBottom: '16px'
          }}
        >
          {loading ? 'Verifying...' : 'Verify'}
        </button>

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingTop: '16px',
          borderTop: '1px solid #334155'
        }}>
          <button
            onClick={() => setUseBackupCode(!useBackupCode)}
            style={{
              background: 'none',
              border: 'none',
              color: '#3b82f6',
              fontSize: '14px',
              cursor: 'pointer',
              textDecoration: 'underline'
            }}
          >
            {useBackupCode ? 'Use authenticator code' : 'Use backup code'}
          </button>
          
          <button
            onClick={onCancel}
            style={{
              background: 'none',
              border: 'none',
              color: '#8fa0b6',
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            Cancel
          </button>
        </div>
      </div>

      <style>{`
        .mfa-verify-container {
          position: fixed;
          inset: 0;
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(0, 0, 0, 0.8);
          backdrop-filter: blur(4px);
        }

        .mfa-verify-content {
          width: 90%;
          max-width: 400px;
          padding: 32px;
          background: #0a1628;
          border: 1px solid rgba(99, 121, 150, 0.24);
          border-radius: 12px;
        }
      `}</style>
    </div>
  )
}

export default MFAVerify
