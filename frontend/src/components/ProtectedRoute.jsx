import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const ProtectedRoute = ({ children, requiredPermission = null }) => {
  const { user, loading, checkPermission } = useAuth()
  const navigate = useNavigate()

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#020817'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            margin: '0 auto 16px',
            border: '4px solid rgba(59, 130, 246, 0.2)',
            borderTopColor: '#3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <p style={{ color: '#94a3b8', fontSize: '14px' }}>Loading...</p>
          <style>{`
            @keyframes spin {
              to { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      </div>
    )
  }

  if (!user) {
    navigate('/login')
    return null
  }

  // Check permission if required
  if (requiredPermission && !checkPermission(requiredPermission)) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#020817',
        padding: '20px'
      }}>
        <div style={{
          maxWidth: '500px',
          padding: '40px',
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '12px',
          textAlign: 'center'
        }}>
          <div style={{
            width: '64px',
            height: '64px',
            margin: '0 auto 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(239, 68, 68, 0.1)',
            borderRadius: '50%',
            color: '#ef4444',
            fontSize: '32px'
          }}>
            🚫
          </div>
          <h2 style={{ margin: '0 0 12px', color: '#f8fafc', fontSize: '24px' }}>
            Access Denied
          </h2>
          <p style={{ margin: 0, color: '#94a3b8', fontSize: '14px', lineHeight: '1.6' }}>
            You don't have permission to access this feature.<br />
            Contact your administrator if you need access.
          </p>
        </div>
      </div>
    )
  }

  return children
}

export default ProtectedRoute
