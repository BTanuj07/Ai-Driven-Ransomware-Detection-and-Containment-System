import joblib
import numpy as np
from typing import Dict, Tuple
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import config from parent directory
try:
    from config import config
except ImportError:
    # Fallback: define config inline
    class Config:
        ML_MODEL_PATH = "ml_engine/models/isolation_forest.joblib"
        ANOMALY_THRESHOLD = -0.5
        FEATURE_COLUMNS = [
            "file_operations_per_min",
            "process_cpu_percent",
            "process_memory_mb",
            "network_connections_count",
            "suspicious_extensions_count",
            "rapid_file_changes",
            "encryption_indicators"
        ]
    config = Config()

class AnomalyDetector:
    """ML-based anomaly detection using Isolation Forest"""
    
    def __init__(self):
        self.model = None
        self.feature_columns = config.FEATURE_COLUMNS
        self.threshold = config.ANOMALY_THRESHOLD
        self._load_model()
    
    def _load_model(self):
        """Load trained model"""
        model_path = Path(config.ML_MODEL_PATH)
        if model_path.exists():
            self.model = joblib.load(model_path)
            print(f"✅ ML model loaded from {model_path}")
        else:
            print(f"⚠️ Model not found at {model_path}. Please train the model first.")
    
    def predict(self, features: Dict[str, float]) -> Tuple[bool, float]:
        """
        Predict if behavior is anomalous
        Returns: (is_anomaly, anomaly_score)
        """
        if self.model is None:
            # Fallback: simple rule-based detection
            return self._rule_based_detection(features)
        
        # Prepare feature vector
        feature_vector = np.array([
            [features.get(col, 0) for col in self.feature_columns]
        ])
        
        # Get anomaly score
        anomaly_score = self.model.score_samples(feature_vector)[0]
        
        # Predict anomaly (score < threshold indicates anomaly)
        is_anomaly = anomaly_score < self.threshold
        
        return is_anomaly, anomaly_score
    
    def _rule_based_detection(self, features: Dict[str, float]) -> Tuple[bool, float]:
        """Fallback rule-based detection when model is not available"""
        score = 0.0
        
        # Check for suspicious patterns
        if features.get("suspicious_extensions_count", 0) > 0:
            score -= 0.5
        
        if features.get("rapid_file_changes", 0) > 20:
            score -= 0.4
        
        if features.get("encryption_indicators", 0) > 0:
            score -= 0.6
        
        if features.get("file_operations_per_min", 0) > 100:
            score -= 0.3
        
        is_anomaly = score < -0.5
        
        return is_anomaly, score
