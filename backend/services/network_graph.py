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
