from typing import Dict, Any, Tuple
from config import config

class RiskScorer:
    """Calculate risk scores based on multiple factors"""
    
    def calculate_risk(self, message: Dict[str, Any], anomaly_score: float) -> Tuple[str, float]:
        """
        Calculate risk level and score
        Returns: (risk_level, risk_score)
        """
        # Base score from anomaly detection
        risk_score = abs(anomaly_score)
        
        # Factor 1: File operation intensity
        file_ops = message.get("file_operations_per_min", 0)
        if file_ops > 100:
            risk_score += 0.3
        elif file_ops > 50:
            risk_score += 0.15
        
        # Factor 2: Suspicious file extensions
        suspicious_ext = message.get("suspicious_extensions_count", 0)
        if suspicious_ext > 0:
            risk_score += 0.4
        
        # Factor 3: Rapid file changes (encryption indicator)
        rapid_changes = message.get("rapid_file_changes", 0)
        if rapid_changes > 20:
            risk_score += 0.35
        elif rapid_changes > 10:
            risk_score += 0.2
        
        # Factor 4: Encryption indicators
        encryption_indicators = message.get("encryption_indicators", 0)
        if encryption_indicators > 0:
            risk_score += 0.5
        
        # Factor 5: CPU/Memory spikes
        cpu = message.get("process_cpu_percent", 0)
        memory = message.get("process_memory_mb", 0)
        if cpu > 80 or memory > 1000:
            risk_score += 0.2
        
        # Factor 6: Network activity
        network_conns = message.get("network_connections_count", 0)
        if network_conns > 50:
            risk_score += 0.15
        
        # Normalize score to 0-1 range
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score >= config.RISK_THRESHOLDS["HIGH"]:
            risk_level = "HIGH"
        elif risk_score >= config.RISK_THRESHOLDS["MEDIUM"]:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return risk_level, risk_score
