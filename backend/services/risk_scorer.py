from typing import Dict, Any, Tuple
from services.settings_manager import settings_manager

class RiskScorer:
    """Calculate risk scores based on multiple factors"""
    
    def calculate_risk(self, message: Dict[str, Any], anomaly_score: float) -> Tuple[str, float]:
        """
        Calculate risk level and score based on metrics
        Returns: (risk_level, risk_score)
        """
        # Start with a base score from metrics (not anomaly score)
        risk_score = 0.0
        
        # Factor 1: File operation intensity (0-0.25)
        file_ops = message.get("file_operations_per_min", 0)
        if file_ops > 150:  # HIGH
            risk_score += 0.25
        elif file_ops > 80:  # MEDIUM
            risk_score += 0.15
        elif file_ops > 30:  # LOW
            risk_score += 0.08
        
        # Factor 2: CPU usage (0-0.20)
        cpu = message.get("process_cpu_percent", 0)
        if cpu > 85:  # HIGH
            risk_score += 0.20
        elif cpu > 65:  # MEDIUM
            risk_score += 0.12
        elif cpu > 40:  # LOW
            risk_score += 0.06
        
        # Factor 3: Encryption indicators (0-0.25)
        encryption_indicators = message.get("encryption_indicators", 0)
        if encryption_indicators > 3:  # HIGH
            risk_score += 0.25
        elif encryption_indicators > 1:  # MEDIUM
            risk_score += 0.15
        elif encryption_indicators > 0:  # LOW
            risk_score += 0.08
        
        # Factor 4: Suspicious file extensions (0-0.15)
        suspicious_ext = message.get("suspicious_extensions_count", 0)
        if suspicious_ext > 10:  # HIGH
            risk_score += 0.15
        elif suspicious_ext > 5:  # MEDIUM
            risk_score += 0.10
        elif suspicious_ext > 1:  # LOW
            risk_score += 0.05
        
        # Factor 5: Rapid file changes (0-0.15)
        rapid_changes = message.get("rapid_file_changes", 0)
        if rapid_changes > 50:  # HIGH
            risk_score += 0.15
        elif rapid_changes > 30:  # MEDIUM
            risk_score += 0.10
        elif rapid_changes > 10:  # LOW
            risk_score += 0.05
        
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
