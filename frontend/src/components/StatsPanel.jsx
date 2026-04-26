const StatsPanel = ({ stats }) => {
  return (
    <>
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-400">Total Alerts</p>
            <p className="text-3xl font-bold text-white">{stats?.total_alerts || 0}</p>
          </div>
          <div className="text-4xl">🚨</div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-400">High Risk Alerts</p>
            <p className="text-3xl font-bold text-red-400">{stats?.high_risk_count || 0}</p>
          </div>
          <div className="text-4xl">⚠️</div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-400">Systems Monitored</p>
            <p className="text-3xl font-bold text-green-400">{stats?.systems_monitored || 0}</p>
          </div>
          <div className="text-4xl">💻</div>
        </div>
      </div>
    </>
  )
}

export default StatsPanel
