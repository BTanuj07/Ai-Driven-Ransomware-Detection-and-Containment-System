import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import { PERMISSIONS } from './lib/supabase'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts'

const riskColors = {
  HIGH: '#ef4444',
  MEDIUM: '#f59e0b',
  LOW: '#14b8a6'
}

const navItems = [
  ['Dashboard', 'grid'],
  ['Alerts', 'bell'],
  ['Risk Overview', 'shield'],
  ['Endpoints', 'monitor'],
  ['Network Topology', 'nodes'],
  ['Logs', 'log'],
  ['Threat Hunting', 'search'],
  ['Response Actions', 'bolt'],
  ['Reports', 'report'],
  ['Settings', 'gear'],
  ['Users', 'user']
]

const formatTime = (value) => {
  if (!value) return '--'
  return new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getRiskLevel = (score = 0) => {
  if (score >= 0.8) return 'HIGH'
  if (score >= 0.6) return 'MEDIUM'
  return 'LOW'
}

const Icon = ({ type }) => {
  const common = {
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round',
    strokeLinejoin: 'round'
  }

  const paths = {
    grid: <><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /></>,
    bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 6-3 9h18c0-3-3-2-3-9" /><path d="M10 21h4" /></>,
    shield: <path d="M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6l-7-3Z" />,
    monitor: <><rect x="3" y="4" width="18" height="12" rx="2" /><path d="M8 20h8M12 16v4" /></>,
    nodes: <><circle cx="6" cy="7" r="3" /><circle cx="18" cy="7" r="3" /><circle cx="12" cy="18" r="3" /><path d="m8.5 9.3 2.3 5.1M15.5 9.3l-2.3 5.1" /></>,
    log: <><path d="M7 4h10M7 8h10M7 12h8M7 16h6" /><rect x="4" y="3" width="16" height="18" rx="2" /></>,
    search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></>,
    bolt: <path d="m13 2-8 12h7l-1 8 8-12h-7l1-8Z" />,
    report: <><path d="M7 3h7l4 4v14H7z" /><path d="M14 3v5h4M9 13h6M9 17h6" /></>,
    gear: <><circle cx="12" cy="12" r="3" /><path d="M19 12a7 7 0 0 0-.1-1l2-1.5-2-3.4-2.4 1a8 8 0 0 0-1.7-1L14.5 3h-5l-.3 3.1a8 8 0 0 0-1.7 1l-2.4-1-2 3.4 2 1.5a7 7 0 0 0 0 2l-2 1.5 2 3.4 2.4-1a8 8 0 0 0 1.7 1l.3 3.1h5l.3-3.1a8 8 0 0 0 1.7-1l2.4 1 2-3.4-2-1.5a7 7 0 0 0 .1-1Z" /></>,
    user: <><circle cx="12" cy="8" r="4" /><path d="M4 21c1.4-4 14.6-4 16 0" /></>
  }

  return <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>{paths[type]}</svg>
}

const MetricCard = ({ title, value, trend, tone, icon }) => (
  <section className={`metric-card metric-${tone}`}>
    <div className="metric-icon"><Icon type={icon} /></div>
    <div>
      <p>{title}</p>
      <strong>{value}</strong>
      <span>{trend}</span>
    </div>
  </section>
)

const EmptyState = ({ label }) => (
  <div className="empty-state">{label}</div>
)

function AppContent() {
  const { user, signOut, userRole } = useAuth()
  const [alerts, setAlerts] = useState([])
  const [riskScores, setRiskScores] = useState([])
  const [networkGraph, setNetworkGraph] = useState(null)
  const [stats, setStats] = useState(null)
  const [logs, setLogs] = useState([])
  const [containmentActions, setContainmentActions] = useState([])
  
  // New state for additional features
  const [activeSection, setActiveSection] = useState('Dashboard')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [showSearchResults, setShowSearchResults] = useState(false)
  const [endpoints, setEndpoints] = useState([])
  const [threatPatterns, setThreatPatterns] = useState([])
  const [alertsTimeline, setAlertsTimeline] = useState([])
  const [systemResources, setSystemResources] = useState(null)
  const [showAllAlerts, setShowAllAlerts] = useState(false)
  const [allAlerts, setAllAlerts] = useState([])

  const fetchData = async () => {
    try {
      const [alertsRes, scoresRes, graphRes, statsRes, logsRes, actionsRes, timelineRes, resourcesRes] = await Promise.all([
        axios.get('/api/alerts?limit=20'),
        axios.get('/api/risk-scores'),
        axios.get('/api/network-graph'),
        axios.get('/api/stats'),
        axios.get('/api/logs?limit=50'),
        axios.get('/api/containment-actions?limit=20'),
        axios.get('/api/alerts/timeline?days=7'),
        axios.get('/api/system-resources')
      ])

      setAlerts(alertsRes.data.alerts || [])
      setRiskScores(scoresRes.data.risk_scores || [])
      setNetworkGraph(graphRes.data || null)
      setStats(statsRes.data || null)
      setLogs(logsRes.data.logs || [])
      setContainmentActions(actionsRes.data.actions || [])
      setAlertsTimeline(timelineRes.data.timeline || [])
      setSystemResources(resourcesRes.data || null)
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  }

  const handleSearch = async (query) => {
    if (!query || query.length < 2) {
      setSearchResults([])
      setShowSearchResults(false)
      return
    }
    try {
      const res = await axios.get(`/api/search?query=${encodeURIComponent(query)}`)
      setSearchResults(res.data.results || [])
      setShowSearchResults(true)
    } catch (error) {
      console.error('Error searching:', error)
    }
  }

  const fetchEndpoints = async () => {
    try {
      const res = await axios.get('/api/endpoints')
      setEndpoints(res.data.endpoints || [])
    } catch (error) {
      console.error('Error fetching endpoints:', error)
    }
  }

  const fetchThreatHunting = async () => {
    try {
      const res = await axios.get('/api/threat-hunting')
      setThreatPatterns(res.data.patterns || [])
    } catch (error) {
      console.error('Error fetching threat patterns:', error)
    }
  }

  const handleViewAllAlerts = async () => {
    try {
      const res = await axios.get('/api/alerts?limit=100')
      setAllAlerts(res.data.alerts || [])
      setShowAllAlerts(true)
    } catch (error) {
      console.error('Error fetching all alerts:', error)
    }
  }

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await axios.post(`/api/alerts/${alertId}/acknowledge`)
      fetchData()
    } catch (error) {
      console.error('Error acknowledging alert:', error)
    }
  }

  const handleResolveAlert = async (alertId) => {
    try {
      await axios.post(`/api/alerts/${alertId}/resolve`)
      fetchData()
    } catch (error) {
      console.error('Error resolving alert:', error)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (activeSection === 'Endpoints') {
      fetchEndpoints()
    } else if (activeSection === 'Threat Hunting') {
      fetchThreatHunting()
    }
  }, [activeSection])

  const totals = useMemo(() => {
    const high = stats?.high_risk_count || 0
    const medium = stats?.medium_risk_count || 0
    const low = stats?.low_risk_count || 0
    return {
      high,
      medium,
      low,
      total: stats?.total_alerts || high + medium + low,
      systems: stats?.systems_monitored || networkGraph?.graph?.nodes?.length || 0
    }
  }, [networkGraph, stats])

  const riskTrend = useMemo(() => {
    if (riskScores.length) {
      return riskScores.slice(0, 24).reverse().map((item, index) => ({
        label: formatTime(item.timestamp) || `${index}:00`,
        score: Number(((item.risk_score || 0) * 100).toFixed(0))
      }))
    }

    return logs.slice(0, 24).reverse().map((item) => ({
      label: formatTime(item.timestamp),
      score: Math.min(100, Math.round((item.file_operations_per_min || 0) + (item.encryption_indicators || 0) * 20))
    }))
  }, [logs, riskScores])

  const severityData = [
    { name: 'High', value: totals.high, color: riskColors.HIGH },
    { name: 'Medium', value: totals.medium, color: riskColors.MEDIUM },
    { name: 'Low', value: totals.low, color: riskColors.LOW }
  ]

  const alertsOverTime = useMemo(() => {
    // Use real timeline data from API
    if (alertsTimeline.length > 0) {
      return alertsTimeline
    }
    // Fallback to mock data if API data not available
    const labels = ['16 Apr', '17 Apr', '18 Apr', '19 Apr', '20 Apr', '21 Apr', '22 Apr']
    return labels.map((label, index) => ({
      label,
      high: index === labels.length - 1 ? totals.high : Math.max(0, Math.round(totals.high * (index + 1) / 8)),
      medium: index === labels.length - 1 ? totals.medium : Math.max(0, Math.round(totals.medium * (index + 1) / 8)),
      low: index === labels.length - 1 ? totals.low : Math.max(0, Math.round(totals.low * (index + 1) / 8))
    }))
  }, [alertsTimeline, totals])

  const nodes = networkGraph?.graph?.nodes || []
  const edges = networkGraph?.graph?.edges || []

  const recentAlerts = alerts.slice(0, 5)
  const recentActions = containmentActions.slice(0, 4)
  const latestLog = logs[0]
  const now = new Date().toLocaleString([], {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Icon type="shield" /></div>
          <div>
            <h1>ARCS</h1>
            <p>AI-Driven Ransomware Detection & Containment System</p>
          </div>
        </div>

        <nav>
          {navItems.map(([label, icon], index) => (
            <button 
              className={activeSection === label ? 'active' : ''} 
              key={label}
              onClick={() => setActiveSection(label)}
            >
              <Icon type={icon} />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        <section className="system-status">
          <h2>System Status</h2>
          <div className="status-row">
            <span className="status-dot" />
            <strong>All Systems Operational</strong>
          </div>
          <div className="mini-sparkline">
            {Array.from({ length: 22 }).map((_, index) => (
              <span key={index} style={{ height: `${18 + ((index * 11) % 34)}px` }} />
            ))}
          </div>
          <p>Last Updated: {formatTime(latestLog?.timestamp) || formatTime(new Date())}</p>
        </section>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <button className="icon-button" aria-label="Menu"><span /></button>
          <label className="search-box">
            <Icon type="search" />
            <input 
              placeholder="Search for devices, alerts, IPs..." 
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                handleSearch(e.target.value)
              }}
              onBlur={() => setTimeout(() => setShowSearchResults(false), 200)}
              onFocus={() => searchResults.length > 0 && setShowSearchResults(true)}
            />
            {showSearchResults && searchResults.length > 0 && (
              <div className="search-results">
                {searchResults.map((result, index) => (
                  <div key={index} onClick={() => {
                    setSearchQuery(result.hostname || '')
                    setShowSearchResults(false)
                  }}>
                    <span style={{ fontWeight: 600 }}>{result.hostname || 'Unknown'}</span>
                    <span style={{ marginLeft: '12px', fontSize: '12px', color: '#8fa0b6' }}>
                      {result.result_type}
                    </span>
                    {result.risk_level && (
                      <span style={{ 
                        marginLeft: '12px', 
                        fontSize: '11px', 
                        padding: '2px 8px', 
                        borderRadius: '4px',
                        background: result.risk_level === 'HIGH' ? '#7e22ce' : result.risk_level === 'MEDIUM' ? '#b45309' : '#0d9488',
                        color: '#fff'
                      }}>
                        {result.risk_level}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </label>
          <div className="topbar-actions">
            <button className="notification-button" aria-label="Notifications">
              <Icon type="bell" />
              <span>{totals.high}</span>
            </button>
            <button className="icon-button" aria-label="Settings"><Icon type="gear" /></button>
            <div className="profile" style={{ position: 'relative' }}>
              <div className="avatar"><Icon type="user" /></div>
              <div>
                <strong>{user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User'}</strong>
                <p style={{ textTransform: 'capitalize' }}>{userRole || 'viewer'}</p>
              </div>
              <button 
                onClick={() => signOut()}
                style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  marginTop: '8px',
                  padding: '8px 16px',
                  background: '#ef4444',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  opacity: 0,
                  pointerEvents: 'none',
                  transition: 'opacity 0.2s'
                }}
                className="logout-btn"
              >
                Sign Out
              </button>
            </div>
            <style>{`
              .profile:hover .logout-btn {
                opacity: 1 !important;
                pointer-events: auto !important;
              }
            `}</style>
          </div>
        </header>

        <main>
          {activeSection === 'Dashboard' && (
            <>
              <div className="timestamp">{now}</div>

              <section className="metrics-grid">
                <MetricCard title="Total Endpoints" value={totals.systems || 0} trend="+ monitored live" tone="blue" icon="monitor" />
                <MetricCard title="High Risk Alerts" value={totals.high} trend="critical priority" tone="red" icon="shield" />
                <MetricCard title="Medium Risk Alerts" value={totals.medium} trend="requires review" tone="orange" icon="shield" />
                <MetricCard title="Low Risk Alerts" value={totals.low} trend="monitoring" tone="teal" icon="shield" />
                <MetricCard title="Contained Threats" value={containmentActions.length} trend="+ actions logged" tone="purple" icon="bolt" />
              </section>

          <section className="dashboard-grid">
            <article className="panel risk-overview">
              <div className="panel-header">
                <h2>Risk Score Overview</h2>
                <button>Last 24 Hours</button>
              </div>
              {riskTrend.length ? (
                <ResponsiveContainer width="100%" height={260}>
                  <AreaChart data={riskTrend}>
                    <defs>
                      <linearGradient id="riskFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#ef4444" stopOpacity={0.42} />
                        <stop offset="100%" stopColor="#ef4444" stopOpacity={0.02} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke="#203044" strokeDasharray="3 3" />
                    <XAxis dataKey="label" stroke="#8b9bb0" fontSize={11} tickLine={false} />
                    <YAxis stroke="#8b9bb0" fontSize={11} tickLine={false} domain={[0, 100]} />
                    <Tooltip contentStyle={{ background: '#101a2b', border: '1px solid #2c3b52', borderRadius: 8 }} />
                    <Area type="monotone" dataKey="score" stroke="#ef4444" fill="url(#riskFill)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              ) : <EmptyState label="No risk score data yet" />}
            </article>

            <article className="panel network-panel">
              <div className="panel-header">
                <h2>Network Topology</h2>
                <div className="legend">
                  <span><i className="normal" />Normal</span>
                  <span><i className="risk" />At Risk</span>
                  <span><i className="infected" />Infected</span>
                  <span><i className="isolated" />Isolated</span>
                </div>
              </div>
              <div className="topology-stage">
                {nodes.length ? (
                  nodes.slice(0, 9).map((node, index) => {
                    const level = node.status === 'infected' ? 'infected' : node.status === 'at_risk' ? 'risk' : 'normal'
                    return (
                      <div className={`node node-${index + 1} ${level}`} key={node.id || node.label}>
                        <Icon type={index % 3 === 0 ? 'monitor' : index % 3 === 1 ? 'log' : 'shield'} />
                        <span>{node.label}</span>
                      </div>
                    )
                  })
                ) : <EmptyState label="No monitored systems yet" />}
                {edges.length > 0 && <div className="connection-lines" />}
              </div>
            </article>

            <article className="panel severity-panel">
              <h2>Alerts by Severity</h2>
              <div className="severity-content">
                <ResponsiveContainer width="58%" height={190}>
                  <PieChart>
                    <Pie data={severityData} dataKey="value" innerRadius={54} outerRadius={82} paddingAngle={1}>
                      {severityData.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="severity-total">
                  <strong>{totals.total}</strong>
                  <span>Total</span>
                </div>
                <div className="severity-list">
                  {severityData.map((entry) => (
                    <p key={entry.name}><i style={{ background: entry.color }} />{entry.name}<span>{entry.value}</span></p>
                  ))}
                </div>
              </div>
            </article>

            <article className="panel time-panel">
              <h2>Alerts Over Time</h2>
              <ResponsiveContainer width="100%" height={190}>
                <BarChart data={alertsOverTime}>
                  <CartesianGrid stroke="#203044" strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="label" stroke="#8b9bb0" fontSize={11} tickLine={false} />
                  <YAxis stroke="#8b9bb0" fontSize={11} tickLine={false} />
                  <Tooltip contentStyle={{ background: '#101a2b', border: '1px solid #2c3b52', borderRadius: 8 }} />
                  <Bar dataKey="low" stackId="a" fill={riskColors.LOW} />
                  <Bar dataKey="medium" stackId="a" fill={riskColors.MEDIUM} />
                  <Bar dataKey="high" stackId="a" fill={riskColors.HIGH} />
                </BarChart>
              </ResponsiveContainer>
            </article>

            <article className="panel critical-panel">
              <div className="panel-header">
                <h2>Recent Critical Alerts</h2>
                <button onClick={handleViewAllAlerts}>View All</button>
              </div>
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Endpoint</th>
                    <th>Alert</th>
                    <th>Risk Score</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recentAlerts.length ? recentAlerts.map((alert, index) => {
                    const score = alert.risk_score || 0
                    const level = alert.risk_level || getRiskLevel(score)
                    return (
                      <tr key={alert._id || index}>
                        <td>{formatTime(alert.timestamp)}</td>
                        <td>{alert.hostname || 'Unknown'}</td>
                        <td>{alert.message || 'Suspicious activity detected'}</td>
                        <td style={{ color: riskColors[level] }}>{score.toFixed(2)}</td>
                        <td><span className={`pill pill-${level.toLowerCase()}`}>{level === 'HIGH' ? 'Contained' : 'Monitoring'}</span></td>
                        <td>
                          <button 
                            onClick={() => handleAcknowledgeAlert(alert._id)}
                            style={{ 
                              padding: '4px 8px', 
                              marginRight: '4px', 
                              fontSize: '11px',
                              background: '#0ea5e9',
                              border: 'none',
                              borderRadius: '4px',
                              color: '#fff',
                              cursor: 'pointer'
                            }}
                          >
                            ACK
                          </button>
                          <button 
                            onClick={() => handleResolveAlert(alert._id)}
                            style={{ 
                              padding: '4px 8px', 
                              fontSize: '11px',
                              background: '#10b981',
                              border: 'none',
                              borderRadius: '4px',
                              color: '#fff',
                              cursor: 'pointer'
                            }}
                          >
                            Resolve
                          </button>
                        </td>
                      </tr>
                    )
                  }) : (
                    <tr><td colSpan="6"><EmptyState label="No recent alerts" /></td></tr>
                  )}
                </tbody>
              </table>
            </article>

            <article className="panel response-panel">
              <h2>Recent Response Actions</h2>
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Action</th>
                    <th>Endpoint</th>
                    <th>Status</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {recentActions.length ? recentActions.map((action, index) => (
                    <tr key={action._id || index}>
                      <td>{formatTime(action.timestamp)}</td>
                      <td>{action.action?.split(':')[0] || action.action}</td>
                      <td>{action.hostname || 'Unknown'}</td>
                      <td><span className="success-text">Success</span></td>
                      <td>{action.action || 'Action logged'}</td>
                    </tr>
                  )) : (
                    <tr><td colSpan="5"><EmptyState label="No response actions yet" /></td></tr>
                  )}
                </tbody>
              </table>
            </article>

            <article className="panel resources-panel">
              <h2>System Resources</h2>
              <div className="resource-gauges">
                {[
                  ['CPU Usage', latestLog?.process_cpu_percent || 0, '#10b981'],
                  ['Memory Usage', Math.min(100, Math.round((latestLog?.process_memory_mb || 0) / 10)), '#f59e0b'],
                  ['File Activity', Math.min(100, latestLog?.file_operations_per_min || 0), '#8b5cf6'],
                  ['Network I/O', Math.min(100, latestLog?.network_connections_count || 0), '#0ea5e9']
                ].map(([label, value, color]) => (
                  <div className="gauge" key={label} style={{ '--value': value, '--color': color }}>
                    <p>{label}</p>
                    <div><strong>{Math.round(value)}%</strong></div>
                  </div>
                ))}
              </div>
            </article>
          </section>
          </>
          )}

          {activeSection === 'Endpoints' && (
            <section className="endpoints-section">
              <div className="timestamp">{now}</div>
              <h1 style={{ fontSize: '32px', marginBottom: '24px', marginTop: '24px' }}>Monitored Endpoints</h1>
              
              <section className="metrics-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '32px' }}>
                <MetricCard title="Total Endpoints" value={endpoints.length} trend="actively monitored" tone="blue" icon="monitor" />
                <MetricCard title="Infected" value={endpoints.filter(e => e.status === 'infected').length} trend="critical threats" tone="red" icon="shield" />
                <MetricCard title="At Risk" value={endpoints.filter(e => e.status === 'at_risk').length} trend="potential threats" tone="orange" icon="shield" />
                <MetricCard title="Normal" value={endpoints.filter(e => e.status === 'normal').length} trend="healthy systems" tone="teal" icon="shield" />
              </section>

              <article className="panel">
                <h2 style={{ marginBottom: '20px' }}>Endpoint Details</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Hostname</th>
                      <th>Status</th>
                      <th>Risk Level</th>
                      <th>Total Alerts</th>
                      <th>High Risk Alerts</th>
                      <th>Last Seen</th>
                    </tr>
                  </thead>
                  <tbody>
                    {endpoints.length ? endpoints.map((endpoint, index) => (
                      <tr key={index}>
                        <td style={{ fontWeight: 600 }}>{endpoint.hostname}</td>
                        <td>
                          <span style={{
                            display: 'inline-block',
                            width: '10px',
                            height: '10px',
                            borderRadius: '50%',
                            marginRight: '8px',
                            background: endpoint.status === 'infected' ? '#ef4444' : endpoint.status === 'at_risk' ? '#f59e0b' : '#14b8a6'
                          }} />
                          {endpoint.status}
                        </td>
                        <td>
                          <span className={`pill pill-${endpoint.risk_level.toLowerCase()}`}>
                            {endpoint.risk_level}
                          </span>
                        </td>
                        <td>{endpoint.alert_count}</td>
                        <td style={{ color: '#ef4444', fontWeight: 600 }}>{endpoint.high_risk_count}</td>
                        <td>{formatTime(endpoint.last_seen)}</td>
                      </tr>
                    )) : (
                      <tr><td colSpan="6"><EmptyState label="No endpoints monitored yet" /></td></tr>
                    )}
                  </tbody>
                </table>
              </article>
            </section>
          )}

          {activeSection === 'Threat Hunting' && (
            <section className="threat-hunting-section">
              <div className="timestamp">{now}</div>
              <h1 style={{ fontSize: '32px', marginBottom: '24px', marginTop: '24px' }}>Threat Hunting</h1>
              
              <article className="panel" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
                  <h2>Suspicious Patterns Detected</h2>
                  <div style={{ fontSize: '14px', color: '#8fa0b6' }}>
                    Total Indicators: <span style={{ color: '#ef4444', fontWeight: 700, fontSize: '18px' }}>{threatPatterns.length}</span>
                  </div>
                </div>
                
                {threatPatterns.length > 0 ? (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '18px' }}>
                    {threatPatterns.map((pattern, index) => (
                      <div 
                        key={index}
                        style={{
                          padding: '20px',
                          border: '1px solid rgba(99, 121, 150, 0.24)',
                          borderLeft: `4px solid ${pattern.severity === 'CRITICAL' ? '#ef4444' : pattern.severity === 'HIGH' ? '#f59e0b' : '#14b8a6'}`,
                          borderRadius: '8px',
                          background: 'rgba(15, 23, 42, 0.95)'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                          <h3 style={{ margin: 0, fontSize: '16px', color: '#f8fafc' }}>{pattern.type}</h3>
                          <span style={{
                            padding: '4px 12px',
                            fontSize: '11px',
                            fontWeight: 800,
                            textTransform: 'uppercase',
                            borderRadius: '4px',
                            background: pattern.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                            color: pattern.severity === 'CRITICAL' ? '#fca5a5' : '#fbbf24'
                          }}>
                            {pattern.severity}
                          </span>
                        </div>
                        <p style={{ margin: '12px 0', color: '#cbd5e1', fontSize: '14px' }}>{pattern.description}</p>
                        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(99, 121, 150, 0.16)' }}>
                          <div style={{ fontSize: '13px', color: '#8fa0b6', marginBottom: '8px' }}>
                            <strong style={{ color: '#e2e8f0' }}>Count:</strong> {pattern.count}
                          </div>
                          <div style={{ fontSize: '13px', color: '#8fa0b6' }}>
                            <strong style={{ color: '#e2e8f0' }}>Affected Systems:</strong> {pattern.affected_systems.join(', ')}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState label="No suspicious patterns detected" />
                )}
              </article>
            </section>
          )}

          {activeSection === 'Alerts' && (
            <section className="alerts-section">
              <div className="timestamp">{now}</div>
              <h1 style={{ fontSize: '32px', marginBottom: '24px', marginTop: '24px' }}>All Alerts</h1>
              
              <section className="metrics-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '32px' }}>
                <MetricCard title="Total Alerts" value={totals.total} trend="all time" tone="blue" icon="bell" />
                <MetricCard title="High Risk" value={totals.high} trend="critical priority" tone="red" icon="shield" />
                <MetricCard title="Medium Risk" value={totals.medium} trend="requires review" tone="orange" icon="shield" />
                <MetricCard title="Low Risk" value={totals.low} trend="monitoring" tone="teal" icon="shield" />
              </section>

              <article className="panel">
                <h2 style={{ marginBottom: '20px' }}>Alert History</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Endpoint</th>
                      <th>Alert Message</th>
                      <th>Risk Score</th>
                      <th>Risk Level</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {alerts.length ? alerts.map((alert, index) => {
                      const score = alert.risk_score || 0
                      const level = alert.risk_level || getRiskLevel(score)
                      return (
                        <tr key={alert._id || index}>
                          <td>{formatTime(alert.timestamp)}</td>
                          <td>{alert.hostname || 'Unknown'}</td>
                          <td>{alert.message || 'Suspicious activity detected'}</td>
                          <td style={{ color: riskColors[level] }}>{score.toFixed(2)}</td>
                          <td><span className={`pill pill-${level.toLowerCase()}`}>{level}</span></td>
                          <td>
                            <button 
                              onClick={() => handleAcknowledgeAlert(alert._id)}
                              style={{ 
                                padding: '4px 8px', 
                                marginRight: '4px', 
                                fontSize: '11px',
                                background: '#0ea5e9',
                                border: 'none',
                                borderRadius: '4px',
                                color: '#fff',
                                cursor: 'pointer'
                              }}
                            >
                              ACK
                            </button>
                            <button 
                              onClick={() => handleResolveAlert(alert._id)}
                              style={{ 
                                padding: '4px 8px', 
                                fontSize: '11px',
                                background: '#10b981',
                                border: 'none',
                                borderRadius: '4px',
                                color: '#fff',
                                cursor: 'pointer'
                              }}
                            >
                              Resolve
                            </button>
                          </td>
                        </tr>
                      )
                    }) : (
                      <tr><td colSpan="6"><EmptyState label="No alerts" /></td></tr>
                    )}
                  </tbody>
                </table>
              </article>
            </section>
          )}

          {activeSection === 'Logs' && (
            <section className="logs-section">
              <div className="timestamp">{now}</div>
              <h1 style={{ fontSize: '32px', marginBottom: '24px', marginTop: '24px' }}>System Logs</h1>
              
              <article className="panel">
                <h2 style={{ marginBottom: '20px' }}>Recent Activity</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Hostname</th>
                      <th>CPU %</th>
                      <th>Memory (MB)</th>
                      <th>File Ops/min</th>
                      <th>Network Connections</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.length ? logs.map((log, index) => (
                      <tr key={index}>
                        <td>{formatTime(log.timestamp)}</td>
                        <td>{log.hostname || 'Unknown'}</td>
                        <td>{(log.process_cpu_percent || 0).toFixed(1)}%</td>
                        <td>{(log.process_memory_mb || 0).toFixed(1)}</td>
                        <td style={{ 
                          color: (log.file_operations_per_min || 0) > 100 ? '#ef4444' : '#14b8a6',
                          fontWeight: (log.file_operations_per_min || 0) > 100 ? 700 : 400
                        }}>
                          {log.file_operations_per_min || 0}
                        </td>
                        <td>{log.network_connections_count || 0}</td>
                      </tr>
                    )) : (
                      <tr><td colSpan="6"><EmptyState label="No logs available" /></td></tr>
                    )}
                  </tbody>
                </table>
              </article>
            </section>
          )}

          {activeSection === 'Response Actions' && (
            <section className="response-section">
              <div className="timestamp">{now}</div>
              <h1 style={{ fontSize: '32px', marginBottom: '24px', marginTop: '24px' }}>Response Actions</h1>
              
              <article className="panel">
                <h2 style={{ marginBottom: '20px' }}>Containment History</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Action Type</th>
                      <th>Endpoint</th>
                      <th>Status</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {containmentActions.length ? containmentActions.map((action, index) => (
                      <tr key={action._id || index}>
                        <td>{formatTime(action.timestamp)}</td>
                        <td style={{ fontWeight: 600 }}>{action.action?.split(':')[0] || action.action}</td>
                        <td>{action.hostname || 'Unknown'}</td>
                        <td><span className="success-text">Success</span></td>
                        <td>{action.action || 'Action logged'}</td>
                      </tr>
                    )) : (
                      <tr><td colSpan="5"><EmptyState label="No response actions yet" /></td></tr>
                    )}
                  </tbody>
                </table>
              </article>
            </section>
          )}

          {showAllAlerts && (
            <div style={{
              position: 'fixed',
              inset: 0,
              zIndex: 1000,
              display: 'grid',
              placeItems: 'center',
              background: 'rgba(0, 0, 0, 0.7)',
              backdropFilter: 'blur(4px)'
            }} onClick={() => setShowAllAlerts(false)}>
              <div style={{
                width: '90%',
                maxWidth: '1200px',
                maxHeight: '90vh',
                overflowY: 'auto',
                padding: '32px',
                border: '1px solid rgba(99, 121, 150, 0.24)',
                borderRadius: '12px',
                background: '#0a1628'
              }} onClick={(e) => e.stopPropagation()}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                  <h2 style={{ margin: 0 }}>All Alerts ({allAlerts.length})</h2>
                  <button onClick={() => setShowAllAlerts(false)} style={{
                    padding: '8px 16px',
                    background: '#ef4444',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff',
                    cursor: 'pointer',
                    fontWeight: 600
                  }}>Close</button>
                </div>
                <table>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Endpoint</th>
                      <th>Alert</th>
                      <th>Risk Score</th>
                      <th>Level</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allAlerts.map((alert, index) => {
                      const score = alert.risk_score || 0
                      const level = alert.risk_level || getRiskLevel(score)
                      return (
                        <tr key={alert._id || index}>
                          <td>{formatTime(alert.timestamp)}</td>
                          <td>{alert.hostname || 'Unknown'}</td>
                          <td>{alert.message || 'Suspicious activity detected'}</td>
                          <td style={{ color: riskColors[level] }}>{score.toFixed(2)}</td>
                          <td><span className={`pill pill-${level.toLowerCase()}`}>{level}</span></td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <AppContent />
      </ProtectedRoute>
    </AuthProvider>
  )
}

export default App
