import { useState, useEffect } from 'react'
import { apiClient } from '../lib/api'
import { supabase } from '../lib/supabase'

const NetworkTopologyAdvanced = ({ networkGraph = {} }) => {
  const [selectedNode, setSelectedNode] = useState(null)
  const [attackPath, setAttackPath] = useState([])
  const [blastRadius, setBlastRadius] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)

  // Extract nodes and edges from networkGraph prop or use empty arrays
  const [nodes, setNodes] = useState(networkGraph.nodes || [])
  const [edges, setEdges] = useState(networkGraph.edges || [])

  // Simple Icon component
  const Icon = ({ type }) => {
    const icons = {
      bolt: '⚡',
      shield: '🛡️',
      alert: '⚠️'
    }
    return <span>{icons[type] || '•'}</span>
  }

  // Fetch real network graph data from backend
  useEffect(() => {
    const fetchNetworkData = async () => {
      try {
        setLoading(true)
        
        // Get token from Supabase session
        const { data: { session } } = await supabase.auth.getSession()
        const token = session?.access_token
        const headers = token ? { Authorization: `Bearer ${token}` } : {}

        const response = await apiClient.get('/api/network-graph', { headers })
        
        // Update state with real backend data
        if (response.data.graph) {
          setNodes(response.data.graph.nodes || [])
          setEdges(response.data.graph.edges || [])
        }
        
        if (response.data.attack_path) {
          setAttackPath(response.data.attack_path)
        }
        
        if (response.data.blast_radius) {
          setBlastRadius(response.data.blast_radius)
        }
        
        if (response.data.recommendations) {
          setRecommendations(response.data.recommendations)
        }
      } catch (error) {
        console.error('Failed to fetch network graph:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchNetworkData()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchNetworkData, 30000)
    return () => clearInterval(interval)
  }, [])

  const getNodeColor = (status) => {
    switch(status) {
      case 'infected': return '#ef4444'
      case 'at_risk': return '#f59e0b'
      case 'isolated': return '#8b5cf6'
      default: return '#14b8a6'
    }
  }

  const getNodePosition = (index, total) => {
    const angle = (index / total) * 2 * Math.PI
    const radius = 180
    const centerX = 250 // SVG center X
    const centerY = 250 // SVG center Y
    return {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    }
  }

  // Show loading state
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '600px',
        border: '1px solid rgba(99, 121, 150, 0.24)',
        borderRadius: '12px',
        background: 'rgba(15, 23, 42, 0.95)',
        padding: '24px'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🌐</div>
          <p style={{ color: '#8fa0b6', margin: 0 }}>Loading network topology...</p>
        </div>
      </div>
    )
  }

  // Show message if no network data
  if (!nodes || nodes.length === 0) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '600px',
        border: '1px solid rgba(99, 121, 150, 0.24)',
        borderRadius: '12px',
        background: 'rgba(15, 23, 42, 0.95)',
        padding: '24px'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🌐</div>
          <h2 style={{ margin: '0 0 8px 0', fontSize: '20px', color: '#fff' }}>Network Topology</h2>
          <p style={{ color: '#8fa0b6', margin: 0 }}>No network data available. Start monitoring endpoints to see the network topology.</p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '24px', height: '100%' }}>
      {/* Main Network Visualization */}
      <div style={{
        position: 'relative',
        border: '1px solid rgba(99, 121, 150, 0.24)',
        borderRadius: '12px',
        background: 'rgba(15, 23, 42, 0.95)',
        padding: '24px',
        minHeight: '600px'
      }}>
        <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: '20px' }}>Network Topology Map</h2>
          <div style={{ display: 'flex', gap: '16px', fontSize: '13px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#14b8a6' }} />
              Normal ({nodes.filter(n => n.status === 'normal').length})
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#f59e0b' }} />
              At Risk ({nodes.filter(n => n.status === 'at_risk').length})
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ef4444' }} />
              Infected ({nodes.filter(n => n.status === 'infected').length})
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#8b5cf6' }} />
              Isolated ({nodes.filter(n => n.status === 'isolated').length})
            </span>
          </div>
        </div>

        {/* SVG Network Graph */}
        <svg width="100%" height="500" style={{ background: 'rgba(0, 0, 0, 0.2)', borderRadius: '8px' }}>
          {/* Draw connections */}
          {edges.map((edge, i) => {
            const sourceIndex = nodes.findIndex(n => n.id === edge.source)
            const targetIndex = nodes.findIndex(n => n.id === edge.target)
            if (sourceIndex === -1 || targetIndex === -1) return null
            
            const source = getNodePosition(sourceIndex, nodes.length)
            const target = getNodePosition(targetIndex, nodes.length)
            
            return (
              <line
                key={i}
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke="rgba(99, 121, 150, 0.3)"
                strokeWidth="2"
                strokeDasharray={nodes[sourceIndex].status === 'infected' || nodes[targetIndex].status === 'infected' ? '5,5' : '0'}
              />
            )
          })}

          {/* Draw nodes */}
          {nodes.map((node, i) => {
            const pos = getNodePosition(i, nodes.length)
            const color = getNodeColor(node.status)
            const isSelected = selectedNode?.id === node.id
            
            return (
              <g key={node.id} transform={`translate(${pos.x}, ${pos.y})`}>
                {/* Pulse animation for infected nodes */}
                {node.status === 'infected' && (
                  <circle
                    r="35"
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                    opacity="0.6"
                  >
                    <animate
                      attributeName="r"
                      from="35"
                      to="50"
                      dur="2s"
                      repeatCount="indefinite"
                    />
                    <animate
                      attributeName="opacity"
                      from="0.6"
                      to="0"
                      dur="2s"
                      repeatCount="indefinite"
                    />
                  </circle>
                )}
                
                {/* Node circle */}
                <circle
                  r="30"
                  fill={color}
                  stroke={isSelected ? '#fff' : color}
                  strokeWidth={isSelected ? '3' : '2'}
                  style={{ cursor: 'pointer', filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.4))' }}
                  onClick={() => setSelectedNode(node)}
                />
                
                {/* Node icon */}
                <text
                  textAnchor="middle"
                  dy="5"
                  fill="#fff"
                  fontSize="14"
                  fontWeight="bold"
                  style={{ pointerEvents: 'none' }}
                >
                  {node.label?.substring(0, 2) || 'N'}
                </text>
                
                {/* Node label */}
                <text
                  textAnchor="middle"
                  dy="50"
                  fill="#f8fafc"
                  fontSize="12"
                  fontWeight="600"
                  style={{ pointerEvents: 'none' }}
                >
                  {node.label}
                </text>
              </g>
            )
          })}
        </svg>
      </div>

      {/* Right Panel - Analysis */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Attack Propagation Path */}
        <div style={{
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '12px',
          background: 'rgba(239, 68, 68, 0.05)',
          padding: '20px'
        }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#ef4444', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Icon type="bolt" />
            Attack Propagation Path
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {attackPath.map((step, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: i === 0 ? '#ef4444' : i < attackPath.length - 1 ? '#f59e0b' : '#64748b',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                  fontWeight: 'bold',
                  color: '#fff'
                }}>
                  {i + 1}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '14px' }}>{step}</div>
                  <div style={{ fontSize: '11px', color: '#8fa0b6', marginTop: '2px' }}>
                    {i === 0 ? 'Initial infection' : i < attackPath.length - 1 ? 'Lateral movement' : 'Predicted target'}
                  </div>
                </div>
                {i < attackPath.length - 1 && (
                  <div style={{ color: '#ef4444', fontSize: '18px' }}>→</div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Blast Radius Estimation */}
        {blastRadius && (
          <div style={{
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '12px',
            background: 'rgba(245, 158, 11, 0.05)',
            padding: '20px'
          }}>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Icon type="shield" />
              Blast Radius Estimation
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div style={{ padding: '12px', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ef4444' }}>{blastRadius.affected}</div>
                <div style={{ fontSize: '12px', color: '#8fa0b6', marginTop: '4px' }}>Currently Affected</div>
              </div>
              <div style={{ padding: '12px', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>{blastRadius.atRisk}</div>
                <div style={{ fontSize: '12px', color: '#8fa0b6', marginTop: '4px' }}>At Risk</div>
              </div>
              <div style={{ padding: '12px', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#8b5cf6' }}>{blastRadius.critical}</div>
                <div style={{ fontSize: '12px', color: '#8fa0b6', marginTop: '4px' }}>Critical Assets</div>
              </div>
              <div style={{ padding: '12px', background: 'rgba(0, 0, 0, 0.2)', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0ea5e9' }}>{blastRadius.probability}%</div>
                <div style={{ fontSize: '12px', color: '#8fa0b6', marginTop: '4px' }}>Spread Probability</div>
              </div>
            </div>
          </div>
        )}

        {/* Isolation Recommendations - Real Data from Backend */}
        <div style={{
          border: '1px solid rgba(139, 92, 246, 0.3)',
          borderRadius: '12px',
          background: 'rgba(139, 92, 246, 0.05)',
          padding: '20px'
        }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#8b5cf6', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Icon type="bolt" />
            Recommended Actions
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {recommendations && recommendations.length > 0 ? (
              recommendations.map((rec, i) => (
                <div key={i} style={{
                  padding: '12px',
                  background: 'rgba(0, 0, 0, 0.2)',
                  borderRadius: '8px',
                  borderLeft: `3px solid ${rec.priority === 'CRITICAL' ? '#ef4444' : rec.priority === 'HIGH' ? '#f59e0b' : '#0ea5e9'}`,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span style={{ fontSize: '13px', fontWeight: 500 }}>{rec.action}</span>
                  <span style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '10px',
                    fontWeight: 'bold',
                    background: rec.priority === 'CRITICAL' ? '#ef4444' : rec.priority === 'HIGH' ? '#f59e0b' : '#0ea5e9',
                    color: '#fff'
                  }}>
                    {rec.priority}
                  </span>
                </div>
              ))
            ) : (
              <div style={{ padding: '12px', textAlign: 'center', color: '#8fa0b6', fontSize: '13px' }}>
                No immediate actions required
              </div>
            )}
          </div>
          <button style={{
            width: '100%',
            marginTop: '16px',
            padding: '12px',
            background: '#8b5cf6',
            border: 'none',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '14px',
            fontWeight: 'bold',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => e.target.style.background = '#7c3aed'}
          onMouseOut={(e) => e.target.style.background = '#8b5cf6'}
          >
            Execute Containment Protocol
          </button>
        </div>

        {/* Selected Node Details */}
        {selectedNode && (
          <div style={{
            border: '1px solid rgba(99, 121, 150, 0.24)',
            borderRadius: '12px',
            background: 'rgba(15, 23, 42, 0.95)',
            padding: '20px'
          }}>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px' }}>Node Details</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#8fa0b6' }}>Hostname:</span>
                <span style={{ fontWeight: 600 }}>{selectedNode.label}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#8fa0b6' }}>Status:</span>
                <span style={{ 
                  padding: '2px 8px', 
                  borderRadius: '4px', 
                  background: getNodeColor(selectedNode.status),
                  color: '#fff',
                  fontSize: '11px',
                  fontWeight: 'bold'
                }}>
                  {selectedNode.status?.toUpperCase()}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#8fa0b6' }}>Connections:</span>
                <span style={{ fontWeight: 600 }}>{edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).length}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default NetworkTopologyAdvanced
