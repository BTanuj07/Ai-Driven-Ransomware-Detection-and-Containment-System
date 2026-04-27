import networkx as nx
from typing import Dict, List, Any, Set
from datetime import datetime, timedelta

class NetworkGraphService:
    """Attack propagation analysis using network graphs"""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.infected_nodes: Set[str] = set()
        self.at_risk_nodes: Set[str] = set()
    
    def add_node(self, hostname: str, attributes: Dict[str, Any] = None):
        """Add a node to the network graph"""
        if attributes is None:
            attributes = {}
        self.graph.add_node(hostname, **attributes)
    
    def add_connection(self, source: str, target: str, weight: float = 1.0):
        """Add a connection between two nodes"""
        self.graph.add_edge(source, target, weight=weight)
    
    def mark_infected(self, hostname: str):
        """Mark a node as infected"""
        self.infected_nodes.add(hostname)
        if hostname in self.graph:
            self.graph.nodes[hostname]["status"] = "infected"
            self.graph.nodes[hostname]["infected_at"] = datetime.utcnow().isoformat()
    
    def predict_propagation(self, infected_node: str, threshold: float = 0.5) -> List[str]:
        """
        Predict which nodes are at risk of infection
        Returns list of at-risk hostnames
        """
        if infected_node not in self.graph:
            return []
        
        at_risk = []
        
        # Get neighbors of infected node
        neighbors = list(self.graph.neighbors(infected_node))
        
        for neighbor in neighbors:
            if neighbor not in self.infected_nodes:
                # Calculate risk based on connection weight and graph centrality
                edge_weight = self.graph[infected_node][neighbor].get("weight", 1.0)
                centrality = nx.degree_centrality(self.graph).get(neighbor, 0)
                
                risk_score = (edge_weight + centrality) / 2
                
                if risk_score >= threshold:
                    at_risk.append(neighbor)
                    self.at_risk_nodes.add(neighbor)
                    if neighbor in self.graph:
                        self.graph.nodes[neighbor]["status"] = "at_risk"
                        self.graph.nodes[neighbor]["risk_score"] = risk_score
        
        return at_risk
    
    def get_graph_data(self) -> Dict[str, Any]:
        """Get graph data for visualization"""
        nodes = []
        edges = []
        
        for node in self.graph.nodes():
            node_data = {
                "id": node,
                "label": node,
                "status": self.graph.nodes[node].get("status", "normal"),
                "risk_score": self.graph.nodes[node].get("risk_score", 0)
            }
            nodes.append(node_data)
        
        for source, target in self.graph.edges():
            edge_data = {
                "source": source,
                "target": target,
                "weight": self.graph[source][target].get("weight", 1.0)
            }
            edges.append(edge_data)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "infected_count": len(self.infected_nodes),
            "at_risk_count": len(self.at_risk_nodes)
        }
    
    def get_critical_nodes(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Identify most critical nodes based on centrality"""
        centrality = nx.degree_centrality(self.graph)
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                "hostname": node,
                "centrality": score,
                "status": self.graph.nodes[node].get("status", "normal")
            }
            for node, score in sorted_nodes[:top_n]
        ]
    
    def simulate_network(self, num_nodes: int = 10):
        """Create a simulated network topology"""
        # Add nodes
        for i in range(num_nodes):
            hostname = f"host-{i+1}"
            self.add_node(hostname, {"status": "normal"})
        
        # Add connections (simulate network topology)
        import random
        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            # Connect to 2-4 random other nodes
            num_connections = random.randint(2, min(4, len(nodes) - 1))
            targets = random.sample([n for n in nodes if n != nodes[i]], num_connections)
            for target in targets:
                weight = random.uniform(0.3, 1.0)
                self.add_connection(nodes[i], target, weight)
    
    def calculate_attack_propagation_path(self) -> List[str]:
        """Calculate real attack propagation path using shortest paths"""
        if not self.infected_nodes or len(self.graph.nodes()) == 0:
            return []
        
        # Start from first infected node
        infected_list = list(self.infected_nodes)
        source = infected_list[0]
        
        # Find high-value targets (nodes with high centrality)
        centrality = nx.betweenness_centrality(self.graph)
        targets = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate shortest path to most critical nodes
        path = [source]
        visited = {source}
        
        for target_node, _ in targets[:3]:
            if target_node not in visited:
                try:
                    shortest = nx.shortest_path(self.graph, source, target_node)
                    for node in shortest[1:]:  # Skip source
                        if node not in visited:
                            path.append(node)
                            visited.add(node)
                            source = node  # Continue from this node
                            break
                except nx.NetworkXNoPath:
                    continue
        
        return path[:4]  # Return top 4 nodes in propagation path
    
    def calculate_blast_radius(self) -> Dict[str, Any]:
        """Calculate real blast radius using graph algorithms"""
        if not self.infected_nodes or len(self.graph.nodes()) == 0:
            return {
                "affected": 0,
                "atRisk": 0,
                "critical": 0,
                "probability": 0
            }
        
        affected = len(self.infected_nodes)
        at_risk = len(self.at_risk_nodes)
        
        # Find critical assets (high centrality nodes)
        centrality = nx.betweenness_centrality(self.graph)
        critical_threshold = sorted(centrality.values(), reverse=True)[min(2, len(centrality)-1)] if centrality else 0
        critical = sum(1 for node, cent in centrality.items() 
                      if cent >= critical_threshold and node not in self.infected_nodes)
        
        # Calculate spread probability based on graph connectivity
        if len(self.graph.nodes()) > 0:
            connectivity = nx.average_node_connectivity(self.graph) if len(self.graph.nodes()) > 1 else 0
            probability = min(100, int((affected / len(self.graph.nodes()) * 100) + (connectivity * 20)))
        else:
            probability = 0
        
        return {
            "affected": affected,
            "atRisk": at_risk,
            "critical": critical,
            "probability": probability
        }
    
    def get_isolation_recommendations(self) -> List[Dict[str, str]]:
        """Generate real isolation recommendations based on graph analysis"""
        recommendations = []
        
        if not self.infected_nodes:
            return recommendations
        
        # Recommend isolating infected nodes
        recommendations.append({
            "action": "Isolate infected nodes",
            "priority": "CRITICAL",
            "color": "#ef4444"
        })
        
        # Check for lateral movement risk
        if self.at_risk_nodes:
            recommendations.append({
                "action": "Block SMB lateral movement",
                "priority": "HIGH",
                "color": "#f59e0b"
            })
        
        # Check for privilege escalation risk
        centrality = nx.betweenness_centrality(self.graph)
        high_value_at_risk = any(centrality.get(node, 0) > 0.5 for node in self.at_risk_nodes)
        
        if high_value_at_risk:
            recommendations.append({
                "action": "Disable admin privilege spread",
                "priority": "HIGH",
                "color": "#f59e0b"
            })
        
        # Always recommend enhanced monitoring
        recommendations.append({
            "action": "Enable enhanced monitoring",
            "priority": "MEDIUM",
            "color": "#0ea5e9"
        })
        
        return recommendations
