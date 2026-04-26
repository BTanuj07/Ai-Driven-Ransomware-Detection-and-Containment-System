import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const RiskScorePanel = ({ riskScores }) => {
  const getRiskColor = (level) => {
    switch (level) {
      case 'HIGH': return '#ef4444'
      case 'MEDIUM': return '#eab308'
      case 'LOW': return '#3b82f6'
      default: return '#6b7280'
    }
  }

  const chartData = riskScores?.slice(0, 10).map(score => ({
    hostname: score.hostname,
    risk_score: (score.risk_score * 100).toFixed(0),
    fill: getRiskColor(score.risk_level)
  })) || []

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <span className="text-2xl">📊</span>
        Risk Scores
      </h2>
      
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="hostname" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
              labelStyle={{ color: '#e2e8f0' }}
            />
            <Bar dataKey="risk_score" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="text-center text-slate-400 py-8">
          <p>No risk scores available</p>
        </div>
      )}

      <div className="mt-4 space-y-2">
        {riskScores?.slice(0, 5).map((score, index) => (
          <div key={index} className="flex items-center justify-between bg-slate-700 rounded p-3">
            <span className="text-sm text-slate-300">{score.hostname}</span>
            <div className="flex items-center gap-2">
              <div className="w-24 bg-slate-600 rounded-full h-2">
                <div 
                  className="h-2 rounded-full" 
                  style={{ 
                    width: `${score.risk_score * 100}%`,
                    backgroundColor: getRiskColor(score.risk_level)
                  }}
                />
              </div>
              <span className="text-xs font-semibold" style={{ color: getRiskColor(score.risk_level) }}>
                {score.risk_level}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default RiskScorePanel
