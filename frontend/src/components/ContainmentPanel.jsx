const ContainmentPanel = ({ actions }) => {
  const getActionIcon = (action) => {
    if (action.includes('KILL_PROCESS')) return '🔪'
    if (action.includes('BLOCK_IP')) return '🚫'
    if (action.includes('ISOLATE')) return '🔒'
    if (action.includes('DISABLE_USER')) return '👤'
    return '⚡'
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <span className="text-2xl">🛡️</span>
        Containment Actions
      </h2>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {actions && actions.length > 0 ? (
          actions.map((action, index) => (
            <div key={index} className="bg-slate-700 rounded p-4 border-l-4 border-green-500">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{getActionIcon(action.action)}</span>
                  <span className="text-sm font-semibold text-slate-300">{action.hostname}</span>
                </div>
                <span className="text-xs text-slate-400">
                  {new Date(action.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-sm text-slate-300 ml-7">{action.action}</p>
              {action.risk_level && (
                <span className={`inline-block mt-2 ml-7 px-2 py-1 rounded text-xs font-semibold ${
                  action.risk_level === 'HIGH' ? 'bg-red-500' : 
                  action.risk_level === 'MEDIUM' ? 'bg-yellow-500' : 'bg-blue-500'
                } text-white`}>
                  {action.risk_level}
                </span>
              )}
            </div>
          ))
        ) : (
          <div className="text-center text-slate-400 py-8">
            <p>No containment actions taken</p>
            <p className="text-sm mt-2">System is ready to respond</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ContainmentPanel
