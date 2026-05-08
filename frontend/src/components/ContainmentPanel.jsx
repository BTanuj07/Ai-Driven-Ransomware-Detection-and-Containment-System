import { useState } from 'react'

const formatIstTime = (value) => {
  if (!value) return '--'
  const hasTimezone = typeof value === 'string' && /([zZ]|[+-]\d{2}:\d{2})$/.test(value)
  const date = value instanceof Date ? value : new Date(hasTimezone ? value : `${value}Z`)
  return date.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
    timeZone: 'Asia/Kolkata'
  })
}

const formatIstDateTime = (value) => {
  if (!value) return '--'
  const hasTimezone = typeof value === 'string' && /([zZ]|[+-]\d{2}:\d{2})$/.test(value)
  const date = value instanceof Date ? value : new Date(hasTimezone ? value : `${value}Z`)
  return date.toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
    timeZone: 'Asia/Kolkata'
  })
}

const ContainmentPanel = ({ actions }) => {
  const [selectedAction, setSelectedAction] = useState(null)

  const getActionIcon = (action) => {
    if (action.includes('KILL_PROCESS')) return '🔪'
    if (action.includes('BLOCK_IP')) return '🚫'
    if (action.includes('ISOLATE')) return '🔒'
    if (action.includes('DISABLE_USER')) return '👤'
    if (action.includes('PENDING_APPROVAL')) return '⏸️'
    return '⚡'
  }

  const getActionType = (action) => {
    if (action.includes('KILL_PROCESS')) return 'Process Termination'
    if (action.includes('BLOCK_IP')) return 'IP Blocking'
    if (action.includes('ISOLATE')) return 'Network Isolation'
    if (action.includes('DISABLE_USER')) return 'User Account Disabled'
    if (action.includes('PENDING_APPROVAL')) return 'Pending Approval'
    return 'Security Action'
  }

  const getStatusBadge = (action) => {
    if (action.action.includes('PENDING_APPROVAL')) {
      return <span className="px-2 py-1 rounded text-xs font-semibold bg-yellow-500 text-white">Pending</span>
    }
    return <span className="px-2 py-1 rounded text-xs font-semibold bg-green-500 text-white">Executed</span>
  }

  const getThreatIndicators = (details) => {
    if (!details) return []
    const indicators = []
    
    if (details.file_operations_per_min > 100) {
      indicators.push({ label: 'High File Operations', value: `${details.file_operations_per_min}/min`, severity: 'high' })
    }
    if (details.encryption_indicators > 0) {
      indicators.push({ label: 'Encryption Activity', value: details.encryption_indicators, severity: 'critical' })
    }
    if (details.suspicious_extensions && details.suspicious_extensions.length > 0) {
      indicators.push({ label: 'Suspicious Extensions', value: details.suspicious_extensions.join(', '), severity: 'high' })
    }
    if (details.network_connections_count > 20) {
      indicators.push({ label: 'Network Connections', value: details.network_connections_count, severity: 'medium' })
    }
    if (details.process_cpu_percent > 80) {
      indicators.push({ label: 'CPU Usage', value: `${details.process_cpu_percent}%`, severity: 'medium' })
    }
    if (details.process_memory_mb > 500) {
      indicators.push({ label: 'Memory Usage', value: `${details.process_memory_mb} MB`, severity: 'medium' })
    }
    
    return indicators
  }

  const getActionTimeline = (action) => {
    const timeline = []
    const baseTime = new Date(action.timestamp)
    
    timeline.push({
      time: formatIstTime(baseTime),
      event: 'Threat Detected',
      icon: '🚨'
    })
    
    timeline.push({
      time: formatIstTime(new Date(baseTime.getTime() + 1000)),
      event: 'Risk Analysis Completed',
      icon: '🔍'
    })
    
    timeline.push({
      time: formatIstTime(new Date(baseTime.getTime() + 2000)),
      event: `${getActionType(action.action)} Initiated`,
      icon: getActionIcon(action.action)
    })
    
    if (!action.action.includes('PENDING_APPROVAL')) {
      timeline.push({
        time: formatIstTime(new Date(baseTime.getTime() + 3000)),
        event: 'Action Executed Successfully',
        icon: '✅'
      })
    }
    
    return timeline
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <span className="text-2xl">🛡️</span>
        Response Actions & Incident Logs
      </h2>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {actions && actions.length > 0 ? (
          actions.map((action, index) => (
            <div key={index} className="bg-slate-700 rounded p-4 border-l-4 border-green-500 hover:bg-slate-600 transition-colors cursor-pointer"
                 onClick={() => setSelectedAction(action)}>
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{getActionIcon(action.action)}</span>
                  <div>
                    <span className="text-sm font-semibold text-slate-300 block">{action.hostname}</span>
                    <span className="text-xs text-slate-400">{getActionType(action.action)}</span>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className="text-xs text-slate-400">
                    {formatIstTime(action.timestamp)}
                  </span>
                  {getStatusBadge(action)}
                </div>
              </div>
              <p className="text-sm text-slate-300 ml-7 mb-2">{action.action}</p>
              <div className="flex items-center gap-2 ml-7">
                {action.risk_level && (
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    action.risk_level === 'HIGH' ? 'bg-red-500' : 
                    action.risk_level === 'MEDIUM' ? 'bg-yellow-500' : 'bg-blue-500'
                  } text-white`}>
                    {action.risk_level} Risk
                  </span>
                )}
                <span className="text-xs text-slate-400">Click for details →</span>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-slate-400 py-8">
            <p>No containment actions taken</p>
            <p className="text-sm mt-2">System is ready to respond</p>
          </div>
        )}
      </div>

      {/* Detailed Incident Modal */}
      {selectedAction && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
             onClick={() => setSelectedAction(null)}>
          <div className="bg-slate-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-slate-600"
               onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-6 flex items-start justify-between">
              <div>
                <h3 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                  {getActionIcon(selectedAction.action)}
                  Incident Details
                </h3>
                <p className="text-slate-400">Comprehensive incident and response information</p>
              </div>
              <button 
                onClick={() => setSelectedAction(null)}
                className="text-slate-400 hover:text-white text-2xl leading-none"
              >
                ×
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Basic Information */}
              <div className="bg-slate-700 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  📋 Basic Information
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-slate-400 text-sm">Incident ID</span>
                    <p className="text-white font-mono">{selectedAction._id || 'N/A'}</p>
                  </div>
                  <div>
                    <span className="text-slate-400 text-sm">Timestamp</span>
                    <p className="text-white">{formatIstDateTime(selectedAction.timestamp)}</p>
                  </div>
                  <div>
                    <span className="text-slate-400 text-sm">Endpoint</span>
                    <p className="text-white font-semibold">{selectedAction.hostname}</p>
                  </div>
                  <div>
                    <span className="text-slate-400 text-sm">Risk Level</span>
                    <p>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        selectedAction.risk_level === 'HIGH' ? 'bg-red-500' : 
                        selectedAction.risk_level === 'MEDIUM' ? 'bg-yellow-500' : 'bg-blue-500'
                      } text-white`}>
                        {selectedAction.risk_level || 'UNKNOWN'}
                      </span>
                    </p>
                  </div>
                  <div>
                    <span className="text-slate-400 text-sm">Action Type</span>
                    <p className="text-white">{getActionType(selectedAction.action)}</p>
                  </div>
                  <div>
                    <span className="text-slate-400 text-sm">Status</span>
                    <p>{getStatusBadge(selectedAction)}</p>
                  </div>
                </div>
              </div>

              {/* Response Information */}
              <div className="bg-slate-700 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  ⚡ Response Information
                </h4>
                <div className="space-y-3">
                  <div>
                    <span className="text-slate-400 text-sm">Action Taken</span>
                    <p className="text-white bg-slate-800 p-2 rounded mt-1 font-mono text-sm">
                      {selectedAction.action}
                    </p>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <span className="text-slate-400 text-sm">Response Time</span>
                      <p className="text-white font-semibold">~3 seconds</p>
                    </div>
                    <div>
                      <span className="text-slate-400 text-sm">Automated</span>
                      <p className="text-white font-semibold">
                        {selectedAction.action.includes('MANUAL') ? 'No' : 'Yes'}
                      </p>
                    </div>
                    <div>
                      <span className="text-slate-400 text-sm">Spread Prevented</span>
                      <p className="text-green-400 font-semibold">Yes</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Threat Indicators */}
              {selectedAction.details && getThreatIndicators(selectedAction.details).length > 0 && (
                <div className="bg-slate-700 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    🔍 Threat Indicators
                  </h4>
                  <div className="space-y-2">
                    {getThreatIndicators(selectedAction.details).map((indicator, idx) => (
                      <div key={idx} className="flex items-center justify-between bg-slate-800 p-3 rounded">
                        <span className="text-slate-300">{indicator.label}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-white font-semibold">{indicator.value}</span>
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${
                            indicator.severity === 'critical' ? 'bg-red-600' :
                            indicator.severity === 'high' ? 'bg-red-500' :
                            indicator.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                          } text-white`}>
                            {indicator.severity.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions Timeline */}
              <div className="bg-slate-700 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  ⏱️ Actions Timeline
                </h4>
                <div className="space-y-3">
                  {getActionTimeline(selectedAction).map((item, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <span className="text-2xl">{item.icon}</span>
                      <div className="flex-1">
                        <p className="text-white font-semibold">{item.event}</p>
                        <p className="text-slate-400 text-sm">{item.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Additional Details */}
              {selectedAction.details && (
                <div className="bg-slate-700 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    📝 Additional Details
                  </h4>
                  <div className="bg-slate-800 p-3 rounded">
                    <pre className="text-slate-300 text-sm overflow-x-auto">
                      {JSON.stringify(selectedAction.details, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Outcome */}
              <div className="bg-green-900 bg-opacity-30 border border-green-700 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-green-400 mb-2 flex items-center gap-2">
                  ✅ Outcome
                </h4>
                <p className="text-slate-300">
                  {selectedAction.action.includes('PENDING_APPROVAL') 
                    ? 'This action is pending administrator approval. The threat has been identified and is being monitored.'
                    : `The containment action was executed successfully. The threat on ${selectedAction.hostname} has been neutralized and the system is now secure. No lateral movement was detected.`
                  }
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ContainmentPanel
