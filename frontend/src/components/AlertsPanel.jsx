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

const AlertsPanel = ({ alerts }) => {
  const getRiskColor = (level) => {
    switch (level) {
      case 'HIGH': return 'bg-red-500'
      case 'MEDIUM': return 'bg-yellow-500'
      case 'LOW': return 'bg-blue-500'
      default: return 'bg-gray-500'
    }
  }

  const getRiskTextColor = (level) => {
    switch (level) {
      case 'HIGH': return 'text-red-400'
      case 'MEDIUM': return 'text-yellow-400'
      case 'LOW': return 'text-blue-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <span className="text-2xl">🚨</span>
        Recent Alerts
      </h2>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {alerts && alerts.length > 0 ? (
          alerts.map((alert, index) => (
            <div key={index} className="bg-slate-700 rounded p-4 border-l-4" style={{ borderLeftColor: getRiskColor(alert.risk_level).replace('bg-', '#') }}>
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getRiskColor(alert.risk_level)} text-white`}>
                    {alert.risk_level}
                  </span>
                  <span className="text-sm text-slate-300">{alert.hostname}</span>
                </div>
                <span className="text-xs text-slate-400">
                  {formatIstTime(alert.timestamp)}
                </span>
              </div>
              <p className="text-sm text-slate-300 mb-2">{alert.message}</p>
              <div className="flex gap-4 text-xs text-slate-400">
                <span>Risk Score: {alert.risk_score?.toFixed(2)}</span>
                <span>Anomaly: {alert.anomaly_score?.toFixed(2)}</span>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-slate-400 py-8">
            <p>No alerts detected</p>
            <p className="text-sm mt-2">System is monitoring...</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default AlertsPanel
