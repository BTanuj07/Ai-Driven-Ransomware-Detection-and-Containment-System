import { useEffect, useMemo, useState } from 'react'
import { apiClient } from '../lib/api'
import { supabase } from '../lib/supabase'

const roleOptions = [
  { value: 'superadmin', label: 'Super Admin', description: 'Full control over settings, users, reports, and containment.' },
  { value: 'analyst', label: 'SOC Analyst', description: 'Monitoring, investigation, alerts, reports, and threat hunting.' },
  { value: 'responder', label: 'Incident Responder', description: 'Manual containment, endpoint isolation, blocking, and response workflows.' },
  { value: 'viewer', label: 'Viewer / Auditor', description: 'Read-only access to dashboard, alerts, reports, and logs.' }
]

const badgeStyles = {
  superadmin: { bg: 'rgba(168, 85, 247, 0.16)', color: '#d8b4fe', border: 'rgba(168, 85, 247, 0.32)' },
  analyst: { bg: 'rgba(251, 146, 60, 0.14)', color: '#fdba74', border: 'rgba(251, 146, 60, 0.32)' },
  responder: { bg: 'rgba(59, 130, 246, 0.14)', color: '#93c5fd', border: 'rgba(59, 130, 246, 0.32)' },
  viewer: { bg: 'rgba(20, 184, 166, 0.14)', color: '#99f6e4', border: 'rgba(20, 184, 166, 0.32)' }
}

const roleLabel = (role) => roleOptions.find(option => option.value === role)?.label || role

export default function UsersModule({ userRole }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ email: '', password: '', role: 'viewer', fullName: '' })
  const [editingUser, setEditingUser] = useState(null)
  const [showEditModal, setShowEditModal] = useState(false)

  const isSuperAdmin = userRole === 'superadmin'

  // Fetch users from backend
  const fetchUsers = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token
      
      if (!token) {
        console.error('No authentication token')
        return
      }
      
      const response = await apiClient.get('/api/supabase/users', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      setUsers(response.data.users || [])
    } catch (error) {
      console.error('Failed to fetch users:', error)
      alert('Failed to load users. Please refresh the page.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const metrics = useMemo(() => ({
    total: users.length,
    active: users.filter(user => user.status === 'active').length,
    privileged: users.filter(user => user.role === 'superadmin' || user.role === 'responder').length,
    readOnly: users.filter(user => user.role === 'viewer').length
  }), [users])

  const handleAddUser = async (event) => {
    event.preventDefault()
    
    if (!form.email.trim() || !form.password.trim()) {
      alert('Email and password are required')
      return
    }

    if (form.password.length < 6) {
      alert('Password must be at least 6 characters')
      return
    }

    try {
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token
      
      if (!token) {
        alert('Authentication required. Please log in again.')
        return
      }

      const response = await apiClient.post('/api/supabase/users', {
        email: form.email.trim(),
        password: form.password,
        role: form.role,
        full_name: form.fullName.trim() || form.email.split('@')[0]
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      alert(`User created successfully with role: ${form.role}`)
      setForm({ email: '', password: '', role: 'viewer', fullName: '' })
      fetchUsers() // Refresh user list
    } catch (error) {
      console.error('Failed to create user:', error)
      alert(error.response?.data?.detail || 'Failed to create user. Please try again.')
    }
  }

  const handleUpdateRole = async (userId, newRole) => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token
      
      if (!token) {
        alert('Authentication required. Please log in again.')
        return
      }

      const user = users.find(u => u.id === userId)
      
      await apiClient.put(`/api/supabase/users/${userId}/role`, {
        email: user.email,
        role: newRole
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      alert(`User role updated to: ${newRole}. User must log out and log back in to see changes.`)
      fetchUsers() // Refresh user list
      setShowEditModal(false)
      setEditingUser(null)
    } catch (error) {
      console.error('Failed to update user role:', error)
      alert(error.response?.data?.detail || 'Failed to update user role. Please try again.')
    }
  }

  const handleDeleteUser = async (userId) => {
    const user = users.find(u => u.id === userId)
    
    if (!confirm(`Are you sure you want to delete user: ${user.email}?\n\nThis will permanently remove them from Supabase and they will not be able to log in.`)) {
      return
    }

    try {
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token
      
      if (!token) {
        alert('Authentication required. Please log in again.')
        return
      }

      await apiClient.delete(`/api/supabase/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })

      alert('User deleted successfully from Supabase')
      fetchUsers() // Refresh user list
    } catch (error) {
      console.error('Failed to delete user:', error)
      alert(error.response?.data?.detail || 'Failed to delete user. Please try again.')
    }
  }

  if (loading) {
    return (
      <div className="users-module" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>👥</div>
          <p style={{ color: '#8fa0b6' }}>Loading users...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="users-module">
      <div className="module-header">
        <div>
          <h1>User Management</h1>
          <p>Only Super Admin can add users and assign operational roles for this project.</p>
        </div>
      </div>

      <div className="users-summary-grid">
        {[
          ['Total users', metrics.total],
          ['Active accounts', metrics.active],
          ['Privileged roles', metrics.privileged],
          ['Read-only users', metrics.readOnly]
        ].map(([label, value]) => (
          <div className="glance-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>

      <section className="user-admin-layout">
        <article className="settings-card">
          <div className="card-header">
            <h2>Admin Workspace</h2>
          </div>

          {isSuperAdmin ? (
            <form className="user-create-form" onSubmit={handleAddUser}>
              <div className="input-group">
                <label>User email *</label>
                <div className="input-with-icon">
                  <input
                    type="email"
                    value={form.email}
                    onChange={(event) => setForm({ ...form, email: event.target.value })}
                    placeholder="new.user@arcs.com"
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Full Name (optional)</label>
                <div className="input-with-icon">
                  <input
                    type="text"
                    value={form.fullName}
                    onChange={(event) => setForm({ ...form, fullName: event.target.value })}
                    placeholder="John Doe"
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Temporary Password *</label>
                <div className="input-with-icon">
                  <input
                    type="password"
                    value={form.password}
                    onChange={(event) => setForm({ ...form, password: event.target.value })}
                    placeholder="Minimum 6 characters"
                    required
                    minLength={6}
                  />
                </div>
                <small style={{ color: '#8fa0b6', fontSize: '12px', marginTop: '4px' }}>
                  User can change this password after first login
                </small>
              </div>

              <div className="input-group">
                <label>Assign role *</label>
                <select
                  className="select-input"
                  value={form.role}
                  onChange={(event) => setForm({ ...form, role: event.target.value })}
                >
                  {roleOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div className="access-note">
                <strong>Super Admin controls</strong>
                <p>Create users with assigned roles. They can log in immediately with the correct permissions.</p>
              </div>

              <div className="role-explainer-list">
                {roleOptions.map((option) => (
                  <div className={`role-explainer ${form.role === option.value ? 'selected' : ''}`} key={option.value}>
                    <strong>{option.label}</strong>
                    <p>{option.description}</p>
                  </div>
                ))}
              </div>

              <button className="btn-save" type="submit">Create User in Supabase</button>
            </form>
          ) : (
            <div className="access-note">
              <strong>Super Admin access required</strong>
              <p>You can view users and role assignments here, but only the Super Admin can create new accounts or change project roles.</p>
            </div>
          )}
        </article>
      </section>

      <article className="settings-card">
        <div className="card-header">
          <h2>User Directory</h2>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Role</th>
                <th>Status</th>
                <th>Last Login</th>
                <th>Sessions</th>
                {isSuperAdmin && <th>Behavior</th>}
              </tr>
            </thead>
            <tbody>
              {users.map((user) => {
                const badge = badgeStyles[user.role] || badgeStyles.viewer
                const suspended = user.status === 'suspended'
                return (
                  <tr key={user.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          width: '38px',
                          height: '38px',
                          borderRadius: '50%',
                          background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#fff',
                          fontWeight: 700
                        }}>
                          {user.email.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <strong style={{ color: '#f8fafc', display: 'block' }}>{user.email}</strong>
                          <span style={{ color: '#8fa0b6', fontSize: '12px' }}>ID: {user.id}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        padding: '6px 12px',
                        borderRadius: '999px',
                        fontSize: '11px',
                        fontWeight: 700,
                        background: badge.bg,
                        color: badge.color,
                        border: `1px solid ${badge.border}`
                      }}>
                        {roleLabel(user.role)}
                      </span>
                    </td>
                    <td><span className={`service-status ${suspended ? 'suspended' : 'running'}`}>{user.status.toUpperCase()}</span></td>
                    <td>{user.last_sign_in_at ? new Date(user.last_sign_in_at).toLocaleString() : 'Never'}</td>
                    <td style={{ color: '#93c5fd', fontWeight: 700 }}>-</td>
                    {isSuperAdmin && (
                      <td>
                        {user.role === 'superadmin' ? (
                          <span className="table-note">Protected</span>
                        ) : (
                          <div className="table-actions">
                            <button 
                              className="table-action-button" 
                              onClick={() => {
                                setEditingUser(user)
                                setShowEditModal(true)
                              }}
                            >
                              Change Role
                            </button>
                            <button 
                              className="table-action-button danger" 
                              onClick={() => handleDeleteUser(user.id)}
                            >
                              Delete
                            </button>
                          </div>
                        )}
                      </td>
                    )}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </article>

      {/* Edit Role Modal */}
      {showEditModal && editingUser && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h2>Change User Role</h2>
              <button className="modal-close" onClick={() => setShowEditModal(false)}>×</button>
            </div>
            
            <div style={{ padding: '24px' }}>
              <div className="detail-row" style={{ marginBottom: '20px' }}>
                <span className="detail-label">User:</span>
                <span className="detail-value"><strong>{editingUser.email}</strong></span>
              </div>
              
              <div className="detail-row" style={{ marginBottom: '20px' }}>
                <span className="detail-label">Current Role:</span>
                <span className="detail-value">
                  <span className={`badge badge-${editingUser.role}`}>{roleLabel(editingUser.role)}</span>
                </span>
              </div>

              <div className="input-group">
                <label>Select New Role:</label>
                <select
                  className="select-input"
                  defaultValue={editingUser.role}
                  onChange={(e) => setEditingUser({ ...editingUser, newRole: e.target.value })}
                >
                  {roleOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div className="role-explainer-list" style={{ marginTop: '20px' }}>
                {roleOptions.map((option) => (
                  <div className={`role-explainer ${(editingUser.newRole || editingUser.role) === option.value ? 'selected' : ''}`} key={option.value}>
                    <strong>{option.label}</strong>
                    <p>{option.description}</p>
                  </div>
                ))}
              </div>

              <div className="access-note" style={{ marginTop: '20px' }}>
                <strong>⚠️ Important</strong>
                <p>User must log out and log back in to see the new role and permissions.</p>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowEditModal(false)}>
                Cancel
              </button>
              <button 
                className="btn-primary" 
                onClick={() => handleUpdateRole(editingUser.id, editingUser.newRole || editingUser.role)}
              >
                Update Role
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
