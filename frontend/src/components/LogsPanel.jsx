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

const LogsPanel = ({ logs }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <span className="text-2xl">📋</span>
        System Logs
      </h2>
      
      <div className="bg-slate-900 rounded p-4 max-h-96 overflow-y-auto font-mono text-xs">
        {logs && logs.length > 0 ? (
          logs.map((log, index) => (
            <div key={index} className="mb-2 text-slate-300 hover:bg-slate-800 p-2 rounded">
              <span className="text-slate-500">[{formatIstDateTime(log.timestamp)}]</span>
              <span className="text-blue-400 ml-2">{log.hostname}</span>
              <span className="text-slate-400 ml-2">
                CPU: {log.process_cpu_percent?.toFixed(1)}% | 
                Mem: {log.process_memory_mb?.toFixed(0)}MB | 
                Files: {log.file_operations_per_min} | 
                Net: {log.network_connections_count}
              </span>
            </div>
          ))
        ) : (
          <div className="text-center text-slate-400 py-8">
            <p>No logs available</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default LogsPanel
