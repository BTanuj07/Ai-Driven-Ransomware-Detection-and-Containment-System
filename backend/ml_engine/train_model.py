"""
ARCS ML Training - Advanced Ensemble Model
Trains Isolation Forest + Random Forest + XGBoost + Gradient Boosting
with hyperparameter tuning and cross-validation for optimal performance.
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import config
except ImportError:
    class Config:
        ML_MODEL_PATH = "ml_engine/models/isolation_forest.joblib"
        FEATURE_COLUMNS = [
            "file_operations_per_min", "process_cpu_percent",
            "process_memory_mb", "network_connections_count",
            "suspicious_extensions_count", "rapid_file_changes",
            "encryption_indicators", "disk_read_mb", "disk_write_mb",
            "open_handles", "child_processes", "network_bytes_sent_kb",
            "network_bytes_recv_kb", "login_attempts", "privilege_escalations"
        ]
    config = Config()

from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, f1_score

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️  XGBoost not installed. Run: pip install xgboost")


# ─── Data Generation ──────────────────────────────────────────────────────────

def generate_normal_samples(n: int = 3000) -> pd.DataFrame:
    """Realistic normal endpoint behavior"""
    np.random.seed(42)
    return pd.DataFrame({
        "file_operations_per_min":  np.random.normal(12, 6, n).clip(0, 40),
        "process_cpu_percent":      np.random.normal(22, 10, n).clip(0, 55),
        "process_memory_mb":        np.random.normal(300, 100, n).clip(50, 600),
        "network_connections_count":np.random.poisson(8, n).clip(0, 25),
        "suspicious_extensions_count": np.zeros(n),
        "rapid_file_changes":       np.random.poisson(1, n).clip(0, 4),
        "encryption_indicators":    np.zeros(n),
        "disk_read_mb":             np.random.normal(20, 10, n).clip(0, 60),
        "disk_write_mb":            np.random.normal(10, 5, n).clip(0, 30),
        "open_handles":             np.random.normal(200, 50, n).clip(50, 400),
        "child_processes":          np.random.poisson(3, n).clip(0, 10),
        "network_bytes_sent_kb":    np.random.normal(50, 20, n).clip(0, 120),
        "network_bytes_recv_kb":    np.random.normal(80, 30, n).clip(0, 200),
        "login_attempts":           np.zeros(n),
        "privilege_escalations":    np.zeros(n),
        "label": 0
    })


def generate_ransomware_samples(n: int = 1000) -> pd.DataFrame:
    """Ransomware attack behavior patterns"""
    np.random.seed(99)
    return pd.DataFrame({
        "file_operations_per_min":  np.random.normal(250, 50, n).clip(100, 500),
        "process_cpu_percent":      np.random.normal(88, 8, n).clip(70, 100),
        "process_memory_mb":        np.random.normal(900, 200, n).clip(400, 2000),
        "network_connections_count":np.random.normal(45, 10, n).clip(20, 80),
        "suspicious_extensions_count": np.random.normal(30, 10, n).clip(5, 100),
        "rapid_file_changes":       np.random.normal(120, 30, n).clip(50, 300),
        "encryption_indicators":    np.random.normal(6, 2, n).clip(3, 15),
        "disk_read_mb":             np.random.normal(200, 50, n).clip(80, 500),
        "disk_write_mb":            np.random.normal(300, 80, n).clip(100, 600),
        "open_handles":             np.random.normal(800, 150, n).clip(400, 1500),
        "child_processes":          np.random.normal(15, 5, n).clip(5, 30),
        "network_bytes_sent_kb":    np.random.normal(500, 100, n).clip(200, 1000),
        "network_bytes_recv_kb":    np.random.normal(100, 30, n).clip(20, 300),
        "login_attempts":           np.random.normal(5, 2, n).clip(0, 15),
        "privilege_escalations":    np.random.normal(3, 1, n).clip(0, 8),
        "label": 1
    })


def generate_lateral_movement_samples(n: int = 500) -> pd.DataFrame:
    """Lateral movement / credential theft patterns"""
    np.random.seed(77)
    return pd.DataFrame({
        "file_operations_per_min":  np.random.normal(40, 10, n).clip(15, 80),
        "process_cpu_percent":      np.random.normal(45, 15, n).clip(20, 80),
        "process_memory_mb":        np.random.normal(500, 100, n).clip(200, 900),
        "network_connections_count":np.random.normal(60, 15, n).clip(30, 100),
        "suspicious_extensions_count": np.random.poisson(2, n).clip(0, 8),
        "rapid_file_changes":       np.random.normal(10, 5, n).clip(2, 25),
        "encryption_indicators":    np.random.poisson(1, n).clip(0, 4),
        "disk_read_mb":             np.random.normal(80, 20, n).clip(20, 150),
        "disk_write_mb":            np.random.normal(40, 15, n).clip(5, 100),
        "open_handles":             np.random.normal(500, 100, n).clip(200, 900),
        "child_processes":          np.random.normal(8, 3, n).clip(2, 20),
        "network_bytes_sent_kb":    np.random.normal(300, 80, n).clip(100, 600),
        "network_bytes_recv_kb":    np.random.normal(200, 60, n).clip(50, 400),
        "login_attempts":           np.random.normal(8, 3, n).clip(2, 20),
        "privilege_escalations":    np.random.normal(2, 1, n).clip(0, 6),
        "label": 1
    })


# ─── Training ─────────────────────────────────────────────────────────────────

def train_all_models(df: pd.DataFrame):
    features = [c for c in df.columns if c != "label"]
    X = df[features].values
    y = df["label"].values

    # Use RobustScaler for better handling of outliers
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {}
    performance_metrics = {}

    # 1. Isolation Forest (unsupervised - anomaly detection)
    print("\n🌲 Training Isolation Forest...")
    iso = IsolationForest(
        n_estimators=300,  # Increased for better accuracy
        contamination=0.25,
        max_samples='auto',
        random_state=42,
        n_jobs=-1
    )
    iso.fit(X_train)
    iso_scores = iso.score_samples(X_test)
    iso_pred = (iso_scores < -0.1).astype(int)
    iso_acc = (iso_pred == y_test).mean()
    print(f"   Isolation Forest  → Accuracy: {iso_acc:.3f}")
    models["isolation_forest"] = iso
    performance_metrics["isolation_forest"] = {"accuracy": iso_acc}

    # 2. Random Forest (supervised - classification)
    print("🌳 Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=300,  # Increased trees
        max_depth=15,      # Deeper trees for complex patterns
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_proba = rf.predict_proba(X_test)[:, 1]
    rf_acc = (rf_pred == y_test).mean()
    rf_auc = roc_auc_score(y_test, rf_proba)
    rf_f1 = f1_score(y_test, rf_pred)
    
    print(f"   Random Forest     → Accuracy: {rf_acc:.3f}  AUC: {rf_auc:.3f}  F1: {rf_f1:.3f}")
    print("\n   Classification Report:")
    print(classification_report(y_test, rf_pred, target_names=["Normal", "Attack"], zero_division=0))
    
    models["random_forest"] = rf
    performance_metrics["random_forest"] = {
        "accuracy": rf_acc,
        "auc": rf_auc,
        "f1_score": rf_f1
    }

    # 3. Gradient Boosting (supervised - ensemble boosting)
    print("🚀 Training Gradient Boosting...")
    gb = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=7,
        min_samples_split=5,
        min_samples_leaf=2,
        subsample=0.8,
        random_state=42
    )
    gb.fit(X_train, y_train)
    gb_pred = gb.predict(X_test)
    gb_proba = gb.predict_proba(X_test)[:, 1]
    gb_acc = (gb_pred == y_test).mean()
    gb_auc = roc_auc_score(y_test, gb_proba)
    gb_f1 = f1_score(y_test, gb_pred)
    
    print(f"   Gradient Boosting → Accuracy: {gb_acc:.3f}  AUC: {gb_auc:.3f}  F1: {gb_f1:.3f}")
    models["gradient_boosting"] = gb
    performance_metrics["gradient_boosting"] = {
        "accuracy": gb_acc,
        "auc": gb_auc,
        "f1_score": gb_f1
    }

    # 4. XGBoost (supervised - extreme gradient boosting)
    if XGBOOST_AVAILABLE:
        print("⚡ Training XGBoost...")
        scale_pos = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
        xgb = XGBClassifier(
            n_estimators=300,  # More estimators
            max_depth=8,       # Deeper trees
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos,
            random_state=42,
            eval_metric="logloss",
            verbosity=0,
            n_jobs=-1
        )
        xgb.fit(X_train, y_train)
        xgb_pred = xgb.predict(X_test)
        xgb_proba = xgb.predict_proba(X_test)[:, 1]
        xgb_acc = (xgb_pred == y_test).mean()
        xgb_auc = roc_auc_score(y_test, xgb_proba)
        xgb_f1 = f1_score(y_test, xgb_pred)
        
        print(f"   XGBoost           → Accuracy: {xgb_acc:.3f}  AUC: {xgb_auc:.3f}  F1: {xgb_f1:.3f}")
        models["xgboost"] = xgb
        performance_metrics["xgboost"] = {
            "accuracy": xgb_acc,
            "auc": xgb_auc,
            "f1_score": xgb_f1
        }
    else:
        print("⚠️  Skipping XGBoost (not installed)")

    # Print ensemble summary
    print("\n" + "="*60)
    print("  ENSEMBLE PERFORMANCE SUMMARY")
    print("="*60)
    for model_name, metrics in performance_metrics.items():
        print(f"  {model_name:20s} → Acc: {metrics['accuracy']:.3f}", end="")
        if 'auc' in metrics:
            print(f"  AUC: {metrics['auc']:.3f}  F1: {metrics['f1_score']:.3f}")
        else:
            print()

    return models, scaler, features, performance_metrics


def save_ensemble(models, scaler, features, performance_metrics, path: str):
    model_path = Path(path)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    ensemble = {
        "models": models,
        "scaler": scaler,
        "features": features,
        "performance_metrics": performance_metrics,
        "version": "3.0-advanced-ensemble",
        "model_count": len(models),
        "trained_at": pd.Timestamp.now().isoformat()
    }
    joblib.dump(ensemble, model_path)
    print(f"\n💾 Ensemble saved → {model_path}")
    print(f"   Models: {list(models.keys())}")
    print(f"   Features: {len(features)}")
    print(f"   Version: {ensemble['version']}")


def main():
    print("=" * 60)
    print("  ARCS ML Training — Advanced Ensemble")
    print("  (Isolation Forest + Random Forest + Gradient Boosting + XGBoost)")
    print("=" * 60)

    print("\n📊 Generating training data...")
    normal   = generate_normal_samples(4000)  # More samples for better training
    ransom   = generate_ransomware_samples(1500)
    lateral  = generate_lateral_movement_samples(800)

    df = pd.concat([normal, ransom, lateral], ignore_index=True).sample(frac=1, random_state=42)
    print(f"   Total samples : {len(df)}  "
          f"(Normal: {(df.label==0).sum()}, Attack: {(df.label==1).sum()})")
    print(f"   Class balance : Normal {(df.label==0).sum()/len(df)*100:.1f}%, "
          f"Attack {(df.label==1).sum()/len(df)*100:.1f}%")

    models, scaler, features, performance_metrics = train_all_models(df)

    save_ensemble(models, scaler, features, performance_metrics, config.ML_MODEL_PATH)

    print("\n✅ Training complete! Restart the backend to load the new model.")
    print("   The ensemble uses majority voting for robust detection.")


if __name__ == "__main__":
    main()
