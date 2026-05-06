from typing import Dict, Any, Tuple
from services.settings_manager import settings_manager

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
        
        # Get thresholds from settings manager (real-time)
        high_threshold = settings_manager.high_risk_threshold
        medium_threshold = settings_manager.medium_risk_threshold
        low_threshold = settings_manager.low_risk_threshold
        
        # Determine risk level using dynamic thresholds
        if risk_score >= high_threshold:
            risk_level = "HIGH"
        elif risk_score >= medium_threshold:
            risk_level = "MEDIUM"
        elif risk_score >= low_threshold:
            risk_level = "LOW"
        else:
            risk_level = "LOW"  # Default to LOW for very low scores
        
        return risk_level, risk_score
