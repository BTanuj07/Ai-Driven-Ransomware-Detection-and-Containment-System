const NetworkGraph = ({ graphData }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'infected': return 'bg-red-500'
      case 'at_risk': return 'bg-yellow-500'
      case 'normal': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  const nodes = graphData?.graph?.nodes || []
  const edges = graphData?.graph?.edges || []

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <span className="text-2xl">🌐</span>
        Network Topology
        {graphData?.real_data && (
          <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">REAL DATA</span>
        )}
      </h2>

      <div className="bg-slate-700 rounded p-4 mb-4">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-red-400">{graphData?.graph?.infected_count || 0}</div>
            <div className="text-xs text-slate-400">Infected</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-400">{graphData?.graph?.at_risk_count || 0}</div>
            <div className="text-xs text-slate-400">At Risk</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-400">{nodes.length}</div>
            <div className="text-xs text-slate-400">Total Nodes</div>
          </div>
        </div>
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        <h3 className="text-sm font-semibold text-slate-400 mb-2">Network Nodes</h3>
        {nodes.map((node, index) => (
          <div key={index} className="flex items-center justify-between bg-slate-700 rounded p-3">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(node.status)}`} />
              <span className="text-sm text-slate-300">{node.label}</span>
            </div>
            <span className="text-xs text-slate-400 capitalize">{node.status}</span>
          </div>
        ))}
      </div>

      {graphData?.critical_nodes && graphData.critical_nodes.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-semibold text-slate-400 mb-2">Critical Nodes</h3>
          <div className="space-y-2">
            {graphData.critical_nodes.slice(0, 3).map((node, index) => (
              <div key={index} className="bg-slate-700 rounded p-2 text-sm">
                <span className="text-slate-300">{node.hostname}</span>
                <span className="text-slate-400 ml-2">({(node.centrality * 100).toFixed(0)}% centrality)</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default NetworkGraph
