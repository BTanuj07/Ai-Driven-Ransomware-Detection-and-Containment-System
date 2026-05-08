import { useState, useEffect } from 'react'
import { BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'
import { apiClient } from '../lib/api'
import { supabase } from '../lib/supabase'

const Icon = ({ type }) => {
  const common = { fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round', strokeLinejoin: 'round', width: '20px', height: '20px' }
  const paths = {
    download: <><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></>,
    file: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></>,
    calendar: <><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></>,
    shield: <path d="M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6l-7-3Z" />,
    alert: <><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></>,
    check: <polyline points="20 6 9 17 4 12" />
  }
  return <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>{paths[type]}</svg>
}

const ReportsModule = () => {
  const [dateRange, setDateRange] = useState('7days')
  const [reportType, setReportType] = useState('all')
  const [loading, setLoading] = useState(true)
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [showIncidentDetails, setShowIncidentDetails] = useState(false)
  
  // Real data from backend with default values
  const [threatSummary, setThreatSummary] = useState({
    totalThreats: 0,
    highRisk: 0,
    mediumRisk: 0,
    lowRisk: 0,
    falsePositives: 0,
    automatedResponses: 0,
    containmentSuccess: 0,
    avgResponseTime: '0s',
    threatsBlocked: 0,
    underInvestigation: 0
  })
  const [trendData, setTrendData] = useState([])
  const [attackTypes, setAttackTypes] = useState([])
  const [incidents, setIncidents] = useState([])

  // Fetch data from backend with real-time refresh
  useEffect(() => {
    const fetchReportsData = async () => {
      try {
        setLoading(true)
        
        // Get token from Supabase session
        const { data: { session } } = await supabase.auth.getSession()
        const token = session?.access_token
        
        if (!token) {
          console.error('No authentication token available for Reports')
          setLoading(false)
          return
        }
        
        const headers = { Authorization: `Bearer ${token}` }

        console.log('Fetching reports data...')
        const [summaryRes, trendRes, attackTypesRes, incidentsRes] = await Promise.all([
          apiClient.get('/api/reports/summary', { headers }),
          apiClient.get('/api/reports/trend?days=7', { headers }),
          apiClient.get('/api/reports/attack-types', { headers }),
          apiClient.get('/api/reports/incidents?limit=50', { headers })
        ])

        console.log('Reports data received:', {
          summary: summaryRes.data,
          trendCount: trendRes.data.trendData?.length,
          attackTypesCount: attackTypesRes.data.attackTypes?.length,
          incidentsCount: incidentsRes.data.incidents?.length
        })

        setThreatSummary(summaryRes.data)
        setTrendData(trendRes.data.trendData || [])
        setAttackTypes(attackTypesRes.data.attackTypes || [])
        setIncidents(incidentsRes.data.incidents || [])
      } catch (error) {
        console.error('Failed to fetch reports data:', error)
        console.error('Error details:', error.response?.data || error.message)
        if (error.response?.status === 401) {
          console.error('Authentication failed - please log in again')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchReportsData()
    
    // Real-time refresh every 30 seconds
    const interval = setInterval(fetchReportsData, 30000)
    
    return () => clearInterval(interval)
  }, [dateRange])

  const handleExport = async (format) => {
    try {
      // Get token from Supabase session
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token
      
      if (!token) {
        alert('Authentication required. Please log in again.')
        return
      }
      
      const headers = { Authorization: `Bearer ${token}` }
      
      await apiClient.post(`/api/reports/export?format=${format}`, {}, { headers })
      alert(`Report export initiated in ${format.toUpperCase()} format`)
    } catch (error) {
      console.error('Export failed:', error)
      alert('Failed to export report')
    }
  }

  if (loading) {
    return (
      <div className="reports-module" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
          <p style={{ color: '#8fa0b6' }}>Loading reports data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="reports-module">
      {/* Header */}
      <div className="module-header">
        <div>
          <h1>Threat Intelligence Reports</h1>
          <p>Comprehensive security analytics and incident reporting</p>
        </div>
        <div className="header-actions">
          <select value={dateRange} onChange={(e) => setDateRange(e.target.value)} className="select-input">
            <option value="24hours">Last 24 Hours</option>
            <option value="7days">Last 7 Days</option>
            <option value="30days">Last 30 Days</option>
            <option value="90days">Last 90 Days</option>
          </select>
          <button className="btn-export" onClick={() => handleExport('pdf')}>
            <Icon type="download" />
            Download PDF Report
          </button>
        </div>
      </div>

      {/* Executive Summary */}
      <section className="executive-summary">
        <h2><Icon type="shield" /> Executive Summary - Today</h2>
        <div className="summary-grid">
          <div className="summary-card critical">
            <div className="summary-value">{threatSummary.totalThreats}</div>
            <div className="summary-label">Threats Detected</div>
            <div className="summary-trend">↑ 12% from yesterday</div>
          </div>
          <div className="summary-card success">
            <div className="summary-value">{threatSummary.automatedResponses}</div>
            <div className="summary-label">Auto-Contained</div>
            <div className="summary-trend">↑ 8% efficiency</div>
          </div>
          <div className="summary-card warning">
            <div className="summary-value">{threatSummary.underInvestigation}</div>
            <div className="summary-label">Under Investigation</div>
            <div className="summary-trend">Requires attention</div>
          </div>
          <div className="summary-card info">
            <div className="summary-value">{threatSummary.containmentSuccess}%</div>
            <div className="summary-label">Spread Prevented</div>
            <div className="summary-trend">↑ 2.1% improvement</div>
          </div>
        </div>
      </section>

      {/* Threat Detection Summary */}
      <div className="reports-grid">
        <section className="report-card">
          <h3>Threat Detection Summary</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Total Threats</span>
              <span className="stat-value">{threatSummary.totalThreats}</span>
            </div>
            <div className="stat-item high">
              <span className="stat-label">High Risk</span>
              <span className="stat-value">{threatSummary.highRisk}</span>
            </div>
            <div className="stat-item medium">
              <span className="stat-label">Medium Risk</span>
              <span className="stat-value">{threatSummary.mediumRisk}</span>
            </div>
            <div className="stat-item low">
              <span className="stat-label">Low Risk</span>
              <span className="stat-value">{threatSummary.lowRisk}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">False Positives</span>
              <span className="stat-value">{threatSummary.falsePositives}</span>
            </div>
            <div className="stat-item success">
              <span className="stat-label">Automated Responses</span>
              <span className="stat-value">{threatSummary.automatedResponses}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Containment Success</span>
              <span className="stat-value">{threatSummary.containmentSuccess}%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Avg Response Time</span>
              <span className="stat-value">{threatSummary.avgResponseTime}</span>
            </div>
          </div>
        </section>

        {/* Attack Type Distribution */}
        <section className="report-card">
          <h3>Attack Type Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={attackTypes}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
              >
                {attackTypes.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="legend-grid">
            {attackTypes.map((type, i) => (
              <div key={i} className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: type.color }}></span>
                <span className="legend-label">{type.name}</span>
                <span className="legend-value">{type.value}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Threat Trend Chart */}
      <section className="report-card">
        <h3>7-Day Threat Trend Analysis</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="date" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155' }} />
            <Legend />
            <Bar dataKey="threats" fill="#3b82f6" name="Total Threats" />
            <Bar dataKey="blocked" fill="#10b981" name="Blocked" />
            <Bar dataKey="falsePos" fill="#f59e0b" name="False Positives" />
          </BarChart>
        </ResponsiveContainer>
      </section>

      {/* Incident Reports Table */}
      <section className="report-card">
        <div className="card-header">
          <h3>Incident Reports</h3>
          <select value={reportType} onChange={(e) => setReportType(e.target.value)} className="select-input-sm">
            <option value="all">All Incidents</option>
            <option value="high">High Risk Only</option>
            <option value="contained">Contained</option>
            <option value="investigating">Under Investigation</option>
          </select>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Incident ID</th>
                <th>Attack Type</th>
                <th>Endpoint</th>
                <th>Detection Time</th>
                <th>Risk Score</th>
                <th>Containment Action</th>
                <th>Response Time</th>
                <th>Status</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((incident) => (
                <tr key={incident.id}>
                  <td><code>{incident.id}</code></td>
                  <td>{incident.type}</td>
                  <td><strong>{incident.endpoint}</strong></td>
                  <td>{incident.time}</td>
                  <td><span className={`badge badge-${incident.risk.toLowerCase()}`}>{incident.risk}</span></td>
                  <td>{incident.action}</td>
                  <td>{incident.duration}</td>
                  <td>
                    <span className={`status-badge ${incident.status.toLowerCase()}`}>
                      {incident.status === 'Contained' || incident.status === 'Resolved' ? <Icon type="check" /> : <Icon type="alert" />}
                      {incident.status}
                    </span>
                  </td>
                  <td>
                    <button 
                      className="btn-details"
                      onClick={() => {
                        setSelectedIncident(incident)
                        setShowIncidentDetails(true)
                      }}
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Incident Details Modal */}
      {showIncidentDetails && selectedIncident && (
        <div className="modal-overlay" onClick={() => setShowIncidentDetails(false)}>
          <div className="modal-content incident-details" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Incident Details - {selectedIncident.id}</h2>
              <button className="modal-close" onClick={() => setShowIncidentDetails(false)}>×</button>
            </div>
            
            <div className="incident-details-grid">
              <div className="detail-section">
                <h3>Basic Information</h3>
                <div className="detail-row">
                  <span className="detail-label">Incident ID:</span>
                  <span className="detail-value"><code>{selectedIncident.id}</code></span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Attack Type:</span>
                  <span className="detail-value">{selectedIncident.type}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Endpoint:</span>
                  <span className="detail-value"><strong>{selectedIncident.endpoint}</strong></span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Detection Time:</span>
                  <span className="detail-value">{selectedIncident.time}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Risk Score:</span>
                  <span className="detail-value">
                    <span className={`badge badge-${selectedIncident.risk.toLowerCase()}`}>{selectedIncident.risk}</span>
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Status:</span>
                  <span className="detail-value">
                    <span className={`status-badge ${selectedIncident.status.toLowerCase()}`}>
                      {selectedIncident.status}
                    </span>
                  </span>
                </div>
              </div>

              <div className="detail-section">
                <h3>Response Information</h3>
                <div className="detail-row">
                  <span className="detail-label">Containment Action:</span>
                  <span className="detail-value">{selectedIncident.action}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Response Time:</span>
                  <span className="detail-value">{selectedIncident.duration}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Automated Response:</span>
                  <span className="detail-value">{selectedIncident.automated ? 'Yes' : 'No'}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Spread Prevented:</span>
                  <span className="detail-value">{selectedIncident.spreadPrevented ? 'Yes' : 'No'}</span>
                </div>
              </div>

              <div className="detail-section full-width">
                <h3>Threat Indicators</h3>
                <div className="indicators-grid">
                  <div className="indicator-item">
                    <span className="indicator-label">File Operations/min:</span>
                    <span className="indicator-value">{selectedIncident.indicators?.fileOps || 'N/A'}</span>
                  </div>
                  <div className="indicator-item">
                    <span className="indicator-label">Suspicious Extensions:</span>
                    <span className="indicator-value">{selectedIncident.indicators?.suspiciousExt || 'N/A'}</span>
                  </div>
                  <div className="indicator-item">
                    <span className="indicator-label">Encryption Indicators:</span>
                    <span className="indicator-value">{selectedIncident.indicators?.encryption || 'N/A'}</span>
                  </div>
                  <div className="indicator-item">
                    <span className="indicator-label">Network Connections:</span>
                    <span className="indicator-value">{selectedIncident.indicators?.networkConn || 'N/A'}</span>
                  </div>
                  <div className="indicator-item">
                    <span className="indicator-label">CPU Usage:</span>
                    <span className="indicator-value">{selectedIncident.indicators?.cpuUsage || 'N/A'}%</span>
                  </div>
                  <div className="indicator-item">
                    <span className="indicator-label">Memory Usage:</span>
                    <span className="indicator-value">{selectedIncident.indicators?.memoryUsage || 'N/A'} MB</span>
                  </div>
                </div>
              </div>

              <div className="detail-section full-width">
                <h3>Actions Taken</h3>
                <div className="actions-timeline">
                  {selectedIncident.actions?.map((action, index) => (
                    <div key={index} className="timeline-item">
                      <div className="timeline-dot"></div>
                      <div className="timeline-content">
                        <div className="timeline-time">{action.time}</div>
                        <div className="timeline-action">{action.description}</div>
                      </div>
                    </div>
                  )) || (
                    <div className="timeline-item">
                      <div className="timeline-dot"></div>
                      <div className="timeline-content">
                        <div className="timeline-action">Threat detected and contained automatically</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="detail-section full-width">
                <h3>Additional Notes</h3>
                <p className="detail-notes">
                  {selectedIncident.notes || 'No additional notes available for this incident.'}
                </p>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowIncidentDetails(false)}>
                Close
              </button>
              <button className="btn-primary" onClick={() => handleExport('pdf')}>
                <Icon type="download" />
                Download Incident Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ReportsModule
