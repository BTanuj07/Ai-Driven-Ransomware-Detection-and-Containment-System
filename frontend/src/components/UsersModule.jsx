import { useEffect, useMemo, useState } from 'react'

const STORAGE_KEY = 'arcs_user_management'

const defaultUsers = [
  { id: 1, email: 'tanuj077777@gmail.com', role: 'superadmin', status: 'active', lastLogin: '2026-04-26 11:45:23', activeSessions: 2 },
  { id: 2, email: 'analyst@arcs.com', role: 'analyst', status: 'active', lastLogin: '2026-04-26 10:23:15', activeSessions: 1 },
  { id: 3, email: 'responder@arcs.com', role: 'responder', status: 'active', lastLogin: '2026-04-26 09:12:45', activeSessions: 1 },
  { id: 4, email: 'viewer@arcs.com', role: 'viewer', status: 'active', lastLogin: '2026-04-25 18:34:12', activeSessions: 0 }
]

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
  const [users, setUsers] = useState(() => {
    if (typeof window === 'undefined') return defaultUsers
    const saved = window.localStorage.getItem(STORAGE_KEY)
    if (!saved) return defaultUsers

    try {
      const parsed = JSON.parse(saved)
      return Array.isArray(parsed) && parsed.length ? parsed : defaultUsers
    } catch {
      return defaultUsers
    }
  })
  const [form, setForm] = useState({ email: '', role: 'viewer' })

  const isSuperAdmin = userRole === 'superadmin'

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(users))
    }
  }, [users])

  const metrics = useMemo(() => ({
    total: users.length,
    active: users.filter(user => user.status === 'active').length,
    privileged: users.filter(user => user.role === 'superadmin' || user.role === 'responder').length,
    readOnly: users.filter(user => user.role === 'viewer').length
  }), [users])

  const handleAddUser = (event) => {
    event.preventDefault()
    if (!form.email.trim()) return

    setUsers((current) => [
      {
        id: current.length + 1,
        email: form.email.trim(),
        role: form.role,
        status: 'active',
        lastLogin: 'Not signed in yet',
        activeSessions: 0
      },
      ...current
    ])

    setForm({ email: '', role: 'viewer' })
  }

  const handleTerminateUser = (id) => {
    setUsers((current) => current.map((user) => (
      user.id === id
        ? { ...user, status: 'suspended', activeSessions: 0, lastLogin: `${user.lastLogin} • suspended` }
        : user
    )))
  }

  const handleDeleteUser = (id) => {
    setUsers((current) => current.filter((user) => user.id !== id))
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
                <label>User email</label>
                <div className="input-with-icon">
                  <input
                    type="email"
                    value={form.email}
                    onChange={(event) => setForm({ ...form, email: event.target.value })}
                    placeholder="new.user@arcs.com"
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Assign role</label>
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
                <p>You can add new users, assign their project role, and terminate accounts directly from the directory below.</p>
              </div>

              <div className="role-explainer-list">
                {roleOptions.map((option) => (
                  <div className={`role-explainer ${form.role === option.value ? 'selected' : ''}`} key={option.value}>
                    <strong>{option.label}</strong>
                    <p>{option.description}</p>
                  </div>
                ))}
              </div>

              <button className="btn-save" type="submit">Add User</button>
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
                    <td>{user.lastLogin}</td>
                    <td style={{ color: '#93c5fd', fontWeight: 700 }}>{user.activeSessions}</td>
                    {isSuperAdmin && (
                      <td>
                        {user.role === 'superadmin' ? (
                          <span className="table-note">Protected</span>
                        ) : suspended ? (
                          <div className="table-actions">
                            <span className="table-note danger">Suspended</span>
                            <button className="table-action-button ghost-danger" onClick={() => handleDeleteUser(user.id)}>
                              Delete
                            </button>
                          </div>
                        ) : (
                          <div className="table-actions">
                            <button className="table-action-button warning" onClick={() => handleTerminateUser(user.id)}>
                              Suspend
                            </button>
                            <button className="table-action-button danger" onClick={() => handleDeleteUser(user.id)}>
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
    </div>
  )
}
