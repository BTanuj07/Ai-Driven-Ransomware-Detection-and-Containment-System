import { useState, useEffect } from 'react'
import { apiClient } from '../lib/api'
import { supabase } from '../lib/supabase'
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function RiskOverview() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  const [riskData, setRiskData] = useState({
    globalRiskScore: 0,
    highRiskDevices: 0,
    mediumRiskDevices: 0,
    lowRiskDevices: 0,
    containmentSuccess: 0,
    autoContainmentConfidence: 0
  })

  const [endpointRisks, setEndpointRisks] = useState([])
  const [riskTrendData, setRiskTrendData] = useState([])
  const [riskFactors, setRiskFactors] = useState([])
  const [severityData, setSeverityData] = useState([])

  // Fetch all risk overview data
  useEffect(() => {
    fetchRiskOverviewData()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchRiskOverviewData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchRiskOverviewData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Get authentication token
      const { data: { session } } = await supabase.auth.getSession()
      const token = session?.access_token
      
      if (!token) {
        setError('Authentication required. Please log in.')
        setLoading(false)
        return
      }
      
      const headers = { Authorization: `Bearer ${token}` }

      const [statsRes, endpointsRes, trendsRes, factorsRes, severityRes] = await Promise.all([
        apiClient.get('/api/risk-overview/stats', { headers }),
        apiClient.get('/api/risk-overview/endpoints?limit=10', { headers }),
        apiClient.get('/api/risk-overview/trends?hours=24', { headers }),
        apiClient.get('/api/risk-overview/factors', { headers }),
        apiClient.get('/api/risk-overview/severity-distribution', { headers })
      ])

      setRiskData(statsRes.data)
      setEndpointRisks(endpointsRes.data.endpoints || [])
      setRiskTrendData(trendsRes.data.trends || [])
      setRiskFactors(factorsRes.data.factors || [])
      setSeverityData(severityRes.data.distribution || [])
      
      setLoading(false)
    } catch (err) {
      console.error('Error fetching risk overview data:', err)
      if (err.response?.status === 401) {
        setError('Authentication failed. Please log in again.')
      } else if (err.response?.status === 500) {
        setError('Server error. Please check backend logs.')
      } else {
        setError('Failed to load risk data. Make sure the backend is running.')
      }
      setLoading(false)
    }
  }

  // Attack Progress Timeline (static for now, can be made dynamic)
  const attackTimeline = [
    { stage: 'Detection', time: '14:23:15', status: 'complete', icon: '🔍' },
    { stage: 'Escalation', time: '14:24:32', status: 'complete', icon: '⚠️' },
    { stage: 'Lateral Movement', time: '14:26:18', status: 'complete', icon: '🔄' },
    { stage: 'Containment', time: '14:27:45', status: 'active', icon: '🛡️' }
  ]

  const getStatusColor = (status) => {
    const colors = {
      'Critical': '#dc2626',
      'High': '#f59e0b',
      'Medium': '#eab308',
      'Low': '#14b8a6'
    }
    return colors[status] || '#64748b'
  }

  const getRiskScoreColor = (score) => {
    if (score >= 0.85) return '#dc2626'
    if (score >= 0.70) return '#f59e0b'
    if (score >= 0.50) return '#eab308'
    return '#14b8a6'
  }

  // Loading state
  if (loading) {
    return (
      <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto' }}>
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: 'bold', color: '#fff', marginBottom: '8px' }}>Risk Overview</h1>
          <p style={{ color: '#8fa0b6', fontSize: '14px' }}>Threat Intelligence & Risk Prioritization Center</p>
        </div>
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center', 
          minHeight: '400px',
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(99, 121, 150, 0.24)',
          borderRadius: '12px',
          padding: '48px'
        }}>
          <div style={{ 
            width: '48px', 
            height: '48px', 
            border: '4px solid rgba(59, 130, 246, 0.3)',
            borderTop: '4px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            marginBottom: '16px'
          }}></div>
          <div style={{ fontSize: '16px', color: '#8fa0b6', fontWeight: '500' }}>Loading risk data...</div>
          <style>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto' }}>
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: 'bold', color: '#fff', marginBottom: '8px' }}>Risk Overview</h1>
          <p style={{ color: '#8fa0b6', fontSize: '14px' }}>Threat Intelligence & Risk Prioritization Center</p>
        </div>
        <div style={{ 
          background: 'rgba(220, 38, 38, 0.1)',
          border: '1px solid rgba(220, 38, 38, 0.3)',
          borderRadius: '12px',
          padding: '32px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#ef4444', marginBottom: '8px' }}>Failed to Load Risk Data</div>
          <div style={{ fontSize: '14px', color: '#8fa0b6', marginBottom: '24px' }}>{error}</div>
          <button 
            onClick={fetchRiskOverviewData}
            style={{
              padding: '12px 24px',
              background: '#3b82f6',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto' }}>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 'bold', color: '#fff', marginBottom: '8px' }}>Risk Overview</h1>
        <p style={{ color: '#8fa0b6', fontSize: '14px' }}>Threat Intelligence & Risk Prioritization Center</p>
      </div>

      {/* TOP SUMMARY CARDS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ color: '#8fa0b6', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase' }}>Global Risk Score</span>
            <span style={{ fontSize: '24px' }}>⚠️</span>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#f59e0b', marginBottom: '8px' }}>{riskData.globalRiskScore}%</div>
          <div style={{ fontSize: '12px', color: '#ef4444' }}>↑ High Risk Level</div>
        </div>

        <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ color: '#8fa0b6', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase' }}>High Risk Devices</span>
            <span style={{ fontSize: '24px' }}>🔴</span>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#dc2626', marginBottom: '8px' }}>{riskData.highRiskDevices}</div>
          <div style={{ fontSize: '12px', color: '#8fa0b6' }}>Require immediate action</div>
        </div>

        <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ color: '#8fa0b6', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase' }}>Medium Risk Devices</span>
            <span style={{ fontSize: '24px' }}>🟡</span>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#f59e0b', marginBottom: '8px' }}>{riskData.mediumRiskDevices}</div>
          <div style={{ fontSize: '12px', color: '#8fa0b6' }}>Under monitoring</div>
        </div>

        <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ color: '#8fa0b6', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase' }}>Low Risk Devices</span>
            <span style={{ fontSize: '24px' }}>🟢</span>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#14b8a6', marginBottom: '8px' }}>{riskData.lowRiskDevices}</div>
          <div style={{ fontSize: '12px', color: '#8fa0b6' }}>Normal operation</div>
        </div>

        <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ color: '#8fa0b6', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase' }}>Containment Success</span>
            <span style={{ fontSize: '24px' }}>✅</span>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#10b981', marginBottom: '8px' }}>{riskData.containmentSuccess}%</div>
          <div style={{ fontSize: '12px', color: '#10b981' }}>↑ Excellent performance</div>
        </div>
      </div>

      {/* MAIN CONTENT GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px' }}>
        {/* ENDPOINT RISK RANKING TABLE */}
        <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#fff', margin: 0 }}>Endpoint Risk Ranking</h2>
            <span style={{ fontSize: '12px', color: '#8fa0b6', background: 'rgba(239, 68, 68, 0.1)', padding: '4px 12px', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
              LIVE
            </span>
          </div>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(99, 121, 150, 0.24)' }}>
                  <th style={{ padding: '12px 8px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: '#8fa0b6', textTransform: 'uppercase' }}>Rank</th>
                  <th style={{ padding: '12px 8px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: '#8fa0b6', textTransform: 'uppercase' }}>Endpoint</th>
                  <th style={{ padding: '12px 8px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: '#8fa0b6', textTransform: 'uppercase' }}>Risk Score</th>
                  <th style={{ padding: '12px 8px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: '#8fa0b6', textTransform: 'uppercase' }}>Threat Type</th>
                  <th style={{ padding: '12px 8px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: '#8fa0b6', textTransform: 'uppercase' }}>Status</th>
                  <th style={{ padding: '12px 8px', textAlign: 'left', fontSize: '11px', fontWeight: '600', color: '#8fa0b6', textTransform: 'uppercase' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {endpointRisks.map((endpoint, index) => (
                  <tr key={endpoint.id} style={{ borderBottom: '1px solid rgba(99, 121, 150, 0.12)' }}>
                    <td style={{ padding: '16px 8px' }}>
                      <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: index < 3 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(99, 121, 150, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 'bold', color: index < 3 ? '#ef4444' : '#8fa0b6' }}>
                        {index + 1}
                      </div>
                    </td>
                    <td style={{ padding: '16px 8px' }}>
                      <div style={{ fontWeight: '600', color: '#fff', fontSize: '14px' }}>{endpoint.name}</div>
                      <div style={{ fontSize: '11px', color: '#8fa0b6', marginTop: '2px' }}>{endpoint.lastActivity}</div>
                    </td>
                    <td style={{ padding: '16px 8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ fontSize: '16px', fontWeight: 'bold', color: getRiskScoreColor(endpoint.riskScore) }}>
                          {(endpoint.riskScore * 100).toFixed(0)}%
                        </div>
                        <div style={{ width: '60px', height: '6px', background: 'rgba(99, 121, 150, 0.2)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${endpoint.riskScore * 100}%`, height: '100%', background: getRiskScoreColor(endpoint.riskScore) }}></div>
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '16px 8px', fontSize: '13px', color: '#cbd5e1' }}>{endpoint.threatType}</td>
                    <td style={{ padding: '16px 8px' }}>
                      <span style={{ 
                        padding: '4px 10px', 
                        borderRadius: '12px', 
                        fontSize: '11px', 
                        fontWeight: 'bold',
                        background: `${getStatusColor(endpoint.status)}20`,
                        color: getStatusColor(endpoint.status),
                        border: `1px solid ${getStatusColor(endpoint.status)}40`
                      }}>
                        {endpoint.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: '16px 8px' }}>
                      <button style={{
                        padding: '6px 12px',
                        background: index < 2 ? '#dc2626' : '#3b82f6',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}>
                        {endpoint.action}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* AUTO-CONTAINMENT CONFIDENCE */}
          <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 'bold', color: '#fff', marginBottom: '16px' }}>Auto-Containment Confidence</h3>
            <div style={{ textAlign: 'center', marginBottom: '16px' }}>
              <div style={{ fontSize: '48px', fontWeight: 'bold', color: '#10b981', marginBottom: '8px' }}>{riskData.autoContainmentConfidence}%</div>
              <div style={{ fontSize: '12px', color: '#8fa0b6' }}>System Confidence Level</div>
            </div>
            <div style={{ width: '100%', height: '12px', background: 'rgba(99, 121, 150, 0.2)', borderRadius: '6px', overflow: 'hidden' }}>
              <div style={{ width: `${riskData.autoContainmentConfidence}%`, height: '100%', background: 'linear-gradient(90deg, #10b981, #06b6d4)', transition: 'width 0.5s' }}></div>
            </div>
            <div style={{ marginTop: '16px', padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              <div style={{ fontSize: '12px', color: '#10b981', fontWeight: '600' }}>✓ High Confidence</div>
              <div style={{ fontSize: '11px', color: '#8fa0b6', marginTop: '4px' }}>Automated response recommended</div>
            </div>
          </div>

          {/* THREAT SEVERITY DISTRIBUTION */}
          <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 'bold', color: '#fff', marginBottom: '16px' }}>Threat Severity Distribution</h3>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              {severityData.map((item) => (
                <div key={item.name} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: item.color }}></div>
                  <div style={{ fontSize: '12px', color: '#cbd5e1' }}>{item.name}</div>
                  <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#fff', marginLeft: 'auto' }}>{item.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* RISK TREND GRAPH */}
      <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#fff', marginBottom: '20px' }}>Risk Score Trend - Last 24 Hours</h2>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={riskTrendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(99, 121, 150, 0.2)" />
            <XAxis dataKey="time" stroke="#8fa0b6" style={{ fontSize: '12px' }} />
            <YAxis stroke="#8fa0b6" style={{ fontSize: '12px' }} />
            <Tooltip 
              contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              labelStyle={{ color: '#fff' }}
            />
            <Line 
              type="monotone" 
              dataKey="score" 
              stroke="#f59e0b" 
              strokeWidth={3}
              dot={{ fill: '#f59e0b', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
        <div style={{ marginTop: '16px', display: 'flex', gap: '16px', justifyContent: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#f59e0b' }}></div>
            <span style={{ fontSize: '12px', color: '#8fa0b6' }}>Risk Score (%)</span>
          </div>
          <div style={{ fontSize: '12px', color: '#ef4444' }}>↑ Escalating Threat Level</div>
        </div>
      </div>

      {/* BOTTOM GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
        {/* RISK FACTOR BREAKDOWN */}
        <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#fff', marginBottom: '8px' }}>Risk Factor Breakdown</h2>
          <p style={{ fontSize: '12px', color: '#8fa0b6', marginBottom: '20px' }}>Explainable AI - Why endpoints are marked as risky</p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {riskFactors.map((factor, index) => (
              <div key={index}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '13px', color: '#cbd5e1', fontWeight: '500' }}>{factor.factor}</span>
                  <span style={{ fontSize: '13px', fontWeight: 'bold', color: factor.color }}>{factor.percentage}%</span>
                </div>
                <div style={{ width: '100%', height: '10px', background: 'rgba(99, 121, 150, 0.2)', borderRadius: '5px', overflow: 'hidden' }}>
                  <div style={{ 
                    width: `${factor.percentage}%`, 
                    height: '100%', 
                    background: factor.color,
                    transition: 'width 0.5s ease',
                    boxShadow: `0 0 10px ${factor.color}40`
                  }}></div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '20px', padding: '12px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
            <div style={{ fontSize: '11px', color: '#3b82f6', fontWeight: '600' }}>ℹ️ ML Model Explanation</div>
            <div style={{ fontSize: '11px', color: '#8fa0b6', marginTop: '4px' }}>Risk factors are weighted by anomaly detection model confidence</div>
          </div>
        </div>

        {/* RECOMMENDED RESPONSE ACTIONS */}
        <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#fff', marginBottom: '8px' }}>Recommended Response Actions</h2>
          <p style={{ fontSize: '12px', color: '#8fa0b6', marginBottom: '20px' }}>AI-suggested containment strategies</p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ padding: '14px', background: 'rgba(220, 38, 38, 0.1)', border: '1px solid rgba(220, 38, 38, 0.3)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#dc2626', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' }}>
                🔒
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '14px', fontWeight: '600', color: '#fff' }}>Isolate Endpoint</div>
                <div style={{ fontSize: '11px', color: '#8fa0b6', marginTop: '2px' }}>Priority: CRITICAL</div>
              </div>
              <div style={{ fontSize: '20px', color: '#10b981' }}>✓</div>
            </div>

            <div style={{ padding: '14px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' }}>
                🚫
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '14px', fontWeight: '600', color: '#fff' }}>Disable SMB Communication</div>
                <div style={{ fontSize: '11px', color: '#8fa0b6', marginTop: '2px' }}>Priority: HIGH</div>
              </div>
              <div style={{ fontSize: '20px', color: '#10b981' }}>✓</div>
            </div>

            <div style={{ padding: '14px', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#f59e0b', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' }}>
                🛡️
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '14px', fontWeight: '600', color: '#fff' }}>Block Suspicious IP</div>
                <div style={{ fontSize: '11px', color: '#8fa0b6', marginTop: '2px' }}>Priority: HIGH</div>
              </div>
              <div style={{ fontSize: '20px', color: '#10b981' }}>✓</div>
            </div>

            <div style={{ padding: '14px', background: 'rgba(234, 179, 8, 0.1)', border: '1px solid rgba(234, 179, 8, 0.3)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#eab308', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' }}>
                👤
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '14px', fontWeight: '600', color: '#fff' }}>Disable Compromised Account</div>
                <div style={{ fontSize: '11px', color: '#8fa0b6', marginTop: '2px' }}>Priority: MEDIUM</div>
              </div>
              <div style={{ fontSize: '20px', color: '#10b981' }}>✓</div>
            </div>
          </div>

          <button style={{
            width: '100%',
            marginTop: '16px',
            padding: '14px',
            background: 'linear-gradient(135deg, #dc2626, #ef4444)',
            border: 'none',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '14px',
            fontWeight: 'bold',
            cursor: 'pointer',
            transition: 'all 0.2s',
            boxShadow: '0 4px 12px rgba(220, 38, 38, 0.3)'
          }}>
            Execute All Recommended Actions
          </button>
        </div>
      </div>

      {/* ATTACK PROGRESS TIMELINE */}
      <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(99, 121, 150, 0.24)', borderRadius: '12px', padding: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#fff', marginBottom: '8px' }}>Attack Progress Timeline</h2>
        <p style={{ fontSize: '12px', color: '#8fa0b6', marginBottom: '24px' }}>Real-time threat progression tracking</p>
        
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }}>
          {/* Progress Line */}
          <div style={{ 
            position: 'absolute', 
            top: '24px', 
            left: '40px', 
            right: '40px', 
            height: '4px', 
            background: 'rgba(99, 121, 150, 0.3)',
            zIndex: 0
          }}>
            <div style={{ 
              width: '75%', 
              height: '100%', 
              background: 'linear-gradient(90deg, #10b981, #06b6d4)',
              transition: 'width 1s ease'
            }}></div>
          </div>

          {attackTimeline.map((stage, index) => (
            <div key={index} style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              flex: 1,
              position: 'relative',
              zIndex: 1
            }}>
              <div style={{ 
                width: '48px', 
                height: '48px', 
                borderRadius: '50%', 
                background: stage.status === 'complete' ? 'linear-gradient(135deg, #10b981, #06b6d4)' : stage.status === 'active' ? 'linear-gradient(135deg, #f59e0b, #eab308)' : 'rgba(99, 121, 150, 0.3)',
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                fontSize: '20px',
                border: '3px solid #0f172a',
                boxShadow: stage.status === 'active' ? '0 0 20px rgba(245, 158, 11, 0.5)' : 'none',
                animation: stage.status === 'active' ? 'pulse 2s infinite' : 'none'
              }}>
                {stage.icon}
              </div>
              <div style={{ marginTop: '12px', textAlign: 'center' }}>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#fff' }}>{stage.stage}</div>
                <div style={{ fontSize: '11px', color: '#8fa0b6', marginTop: '4px' }}>{stage.time}</div>
                {stage.status === 'active' && (
                  <div style={{ 
                    marginTop: '6px', 
                    padding: '3px 8px', 
                    background: 'rgba(245, 158, 11, 0.2)', 
                    borderRadius: '10px',
                    fontSize: '10px',
                    fontWeight: 'bold',
                    color: '#f59e0b',
                    border: '1px solid rgba(245, 158, 11, 0.4)'
                  }}>
                    IN PROGRESS
                  </div>
                )}
                {stage.status === 'complete' && (
                  <div style={{ marginTop: '6px', fontSize: '16px', color: '#10b981' }}>✓</div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: '24px', padding: '16px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ fontSize: '24px' }}>⚡</div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: '600', color: '#10b981' }}>Automated Response Active</div>
            <div style={{ fontSize: '11px', color: '#8fa0b6', marginTop: '2px' }}>System is actively containing the threat. Estimated completion: 2 minutes</div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.5);
          }
          50% {
            box-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
          }
        }
      `}</style>
    </div>
  )
}
