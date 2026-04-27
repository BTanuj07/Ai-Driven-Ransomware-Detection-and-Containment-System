"""
ARCS Ensemble Anomaly Detector
Uses Isolation Forest + Random Forest + XGBoost voting.
Falls back gracefully if models are missing.
"""

import joblib
import numpy as np
from typing import Dict, Tuple
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import config
except ImportError:
    class Config:
        ML_MODEL_PATH = "ml_engine/models/isolation_forest.joblib"
        ANOMALY_THRESHOLD = -0.2
        FEATURE_COLUMNS = [
            "file_operations_per_min", "process_cpu_percent",
            "process_memory_mb", "network_connections_count",
            "suspicious_extensions_count", "rapid_file_changes",
            "encryption_indicators", "disk_read_mb", "disk_write_mb",
            "open_handles", "child_processes", "network_bytes_sent_kb",
            "network_bytes_recv_kb", "login_attempts", "privilege_escalations"
        ]
    config = Config()


class AnomalyDetector:
    """Ensemble anomaly detector: Isolation Forest + Random Forest + XGBoost"""

    def __init__(self):
        self.ensemble = None          # dict with models, scaler, features
        self.feature_columns = config.FEATURE_COLUMNS
        self.threshold = config.ANOMALY_THRESHOLD
        self._load_model()

    # ── Loading ───────────────────────────────────────────────────────────────

    def _load_model(self):
        path = Path(config.ML_MODEL_PATH)
        if not path.exists():
            print(f"⚠️  Model not found at {path}. Run: python ml_engine/train_model.py")
            return

        data = joblib.load(path)

        # Support both old (bare IsolationForest) and new (ensemble dict) format
        if isinstance(data, dict) and "models" in data:
            self.ensemble = data
            names = list(data["models"].keys())
            print(f"✅ Ensemble model loaded: {names}")
        else:
            # Legacy single model — wrap it
            self.ensemble = {
                "models": {"isolation_forest": data},
                "scaler": None,
                "features": self.feature_columns
            }
            print("✅ Legacy Isolation Forest loaded (single model)")

    # ── Prediction ────────────────────────────────────────────────────────────

    def predict(self, features: Dict[str, float]) -> Tuple[bool, float]:
        """
        Returns (is_anomaly, confidence_score 0-1).
        Uses ensemble voting when available, falls back to rule-based.
        """
        if self.ensemble is None:
            return self._rule_based(features)

        feat_cols = self.ensemble.get("features", self.feature_columns)
        vec = np.array([[features.get(c, 0) for c in feat_cols]], dtype=float)

        scaler = self.ensemble.get("scaler")
        if scaler is not None:
            vec = scaler.transform(vec)

        models = self.ensemble["models"]
        votes = []
        scores = []

        # Isolation Forest
        if "isolation_forest" in models:
            iso = models["isolation_forest"]
            iso_score = iso.score_samples(vec)[0]
            iso_vote = 1 if iso_score < self.threshold else 0
            votes.append(iso_vote)
            # Normalise IF score to 0-1 probability-like value
            scores.append(max(0.0, min(1.0, (-iso_score + 0.5))))

        # Random Forest
        if "random_forest" in models:
            rf = models["random_forest"]
            rf_proba = rf.predict_proba(vec)[0][1]
            votes.append(1 if rf_proba >= 0.5 else 0)
            scores.append(rf_proba)

        # XGBoost
        if "xgboost" in models:
            xgb = models["xgboost"]
            xgb_proba = xgb.predict_proba(vec)[0][1]
            votes.append(1 if xgb_proba >= 0.5 else 0)
            scores.append(xgb_proba)

        if not votes:
            return self._rule_based(features)

        # Majority vote
        is_anomaly = sum(votes) > len(votes) / 2
        # Average confidence
        confidence = float(np.mean(scores))

        return is_anomaly, confidence

    # ── Rule-based fallback ───────────────────────────────────────────────────

    def _rule_based(self, features: Dict[str, float]) -> Tuple[bool, float]:
        score = 0.0
        if features.get("suspicious_extensions_count", 0) > 0:
            score += 0.5
        if features.get("rapid_file_changes", 0) > 20:
            score += 0.4
        if features.get("encryption_indicators", 0) > 0:
            score += 0.6
        if features.get("file_operations_per_min", 0) > 100:
            score += 0.3
        if features.get("privilege_escalations", 0) > 0:
            score += 0.4
        if features.get("login_attempts", 0) > 5:
            score += 0.2
        score = min(score, 1.0)
        return score >= 0.5, score
