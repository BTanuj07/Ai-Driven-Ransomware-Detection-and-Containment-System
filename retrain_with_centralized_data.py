"""
Retrain ML model with centralized agent data
This will reduce false positives
"""
import sys
sys.path.insert(0, 'backend')
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
import joblib
from services.database import DatabaseService

print("=" * 70)
print("RETRAINING ML MODEL WITH CENTRALIZED AGENT DATA")
print("=" * 70)

# Get recent logs from database
db = DatabaseService()
logs = db.get_recent_logs(1000)

print(f"\n📊 Collected {len(logs)} log entries from database")

if len(logs) < 100:
    print(f"\n⚠️  Not enough data to retrain (need at least 100 logs)")
    print(f"   Let the centralized agent run for 10-15 minutes to collect more data")
    exit(1)

# Extract features
def extract_features(log):
    """Extract features from log entry"""
    return [
        log.get('process_cpu_percent', 0),
        log.get('process_memory_mb', 0),
        log.get('file_operations_per_min', 0),
        log.get('network_connections_count', 0),
        log.get('suspicious_extensions_count', 0),
        log.get('rapid_file_changes', 0),
        log.get('encryption_indicators', 0),
        log.get('usb_device_connected', 0),
        log.get('port_scan_detected', 0),
        log.get('suspicious_process_count', 0),
        log.get('hidden_process_count', 0),
        log.get('cpu_deviation', 0),
        log.get('memory_deviation', 0),
        log.get('network_deviation', 0)
    ]

# Prepare data
X = np.array([extract_features(log) for log in logs])
print(f"\n📈 Feature matrix shape: {X.shape}")

# Create labels (0 = normal, 1 = attack)
# For now, assume all current data is normal
# We'll add attack data synthetically
y_normal = np.zeros(len(logs))

# Generate synthetic attack data
print(f"\n🦠 Generating synthetic attack data...")
n_attacks = len(logs) // 3  # 33% attack data

attack_data = []
for _ in range(n_attacks):
    attack_features = [
        np.random.uniform(80, 99),  # High CPU
        np.random.uniform(2000, 5000),  # High memory
        np.random.uniform(150, 300),  # High file ops
        np.random.uniform(30, 60),  # High network
        np.random.uniform(10, 50),  # Suspicious extensions
        np.random.uniform(50, 150),  # Rapid changes
        np.random.uniform(3, 8),  # Encryption indicators
        np.random.randint(0, 2),  # USB
        np.random.randint(0, 2),  # Port scan
        np.random.uniform(2, 5),  # Suspicious processes
        np.random.randint(0, 3),  # Hidden processes
        np.random.uniform(20, 50),  # CPU deviation
        np.random.uniform(500, 2000),  # Memory deviation
        np.random.uniform(10, 30)  # Network deviation
    ]
    attack_data.append(attack_features)

X_attack = np.array(attack_data)
y_attack = np.ones(n_attacks)

# Combine normal and attack data
X_combined = np.vstack([X, X_attack])
y_combined = np.concatenate([y_normal, y_attack])

print(f"  Normal samples: {len(y_normal)}")
print(f"  Attack samples: {len(y_attack)}")
print(f"  Total samples: {len(y_combined)}")

# Train models
print(f"\n🤖 Training ensemble models...")

# 1. Isolation Forest (unsupervised)
print(f"  Training Isolation Forest...")
iso_forest = IsolationForest(
    contamination=0.1,  # Expect 10% anomalies
    random_state=42,
    n_estimators=100
)
iso_forest.fit(X_combined)
iso_pred = iso_forest.predict(X_combined)
iso_acc = np.mean((iso_pred == -1) == (y_combined == 1))
print(f"    Accuracy: {iso_acc*100:.2f}%")

# 2. Random Forest (supervised)
print(f"  Training Random Forest...")
rf = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    max_depth=10
)
rf.fit(X_combined, y_combined)
rf_acc = rf.score(X_combined, y_combined)
print(f"    Accuracy: {rf_acc*100:.2f}%")

# 3. Gradient Boosting (supervised)
print(f"  Training Gradient Boosting...")
gb = GradientBoostingClassifier(
    n_estimators=100,
    random_state=42,
    max_depth=5
)
gb.fit(X_combined, y_combined)
gb_acc = gb.score(X_combined, y_combined)
print(f"    Accuracy: {gb_acc*100:.2f}%")

# 4. XGBoost (supervised)
print(f"  Training XGBoost...")
xgb = XGBClassifier(
    n_estimators=100,
    random_state=42,
    max_depth=5,
    use_label_encoder=False,
    eval_metric='logloss'
)
xgb.fit(X_combined, y_combined)
xgb_acc = xgb.score(X_combined, y_combined)
print(f"    Accuracy: {xgb_acc*100:.2f}%")

# Save ensemble model in correct format for detector
print(f"\n💾 Saving ensemble model...")
ensemble = {
    'models': {
        'isolation_forest': iso_forest,
        'random_forest': rf,
        'gradient_boosting': gb,
        'xgboost': xgb
    },
    'scaler': None,
    'features': [
        'process_cpu_percent', 'process_memory_mb', 'file_operations_per_min',
        'network_connections_count', 'suspicious_extensions_count',
        'rapid_file_changes', 'encryption_indicators', 'usb_device_connected',
        'port_scan_detected', 'suspicious_process_count', 'hidden_process_count',
        'cpu_deviation', 'memory_deviation', 'network_deviation'
    ]
}

model_path = 'backend/ml_engine/models/isolation_forest.joblib'
joblib.dump(ensemble, model_path)
print(f"  ✅ Model saved to {model_path}")

# Test on normal data
print(f"\n🧪 Testing on normal data...")
normal_sample = X[:10]  # First 10 normal samples

for i, sample in enumerate(normal_sample):
    # Isolation Forest
    iso_pred = iso_forest.predict([sample])[0]
    
    # Supervised models
    rf_pred = rf.predict_proba([sample])[0][1]
    gb_pred = gb.predict_proba([sample])[0][1]
    xgb_pred = xgb.predict_proba([sample])[0][1]
    
    # Ensemble vote
    ensemble_score = (rf_pred + gb_pred + xgb_pred) / 3
    
    print(f"  Sample {i+1}: Ensemble={ensemble_score:.2f} (should be <0.5 for normal)")

# Test on attack data
print(f"\n🦠 Testing on attack data...")
attack_sample = X_attack[:5]  # First 5 attack samples

for i, sample in enumerate(attack_sample):
    # Supervised models
    rf_pred = rf.predict_proba([sample])[0][1]
    gb_pred = gb.predict_proba([sample])[0][1]
    xgb_pred = xgb.predict_proba([sample])[0][1]
    
    # Ensemble vote
    ensemble_score = (rf_pred + gb_pred + xgb_pred) / 3
    
    print(f"  Sample {i+1}: Ensemble={ensemble_score:.2f} (should be >0.5 for attack)")

print(f"\n" + "=" * 70)
print(f"✅ MODEL RETRAINED SUCCESSFULLY!")
print(f"=" * 70)
print(f"\nNext steps:")
print(f"  1. Restart backend: python backend/main.py")
print(f"  2. Let centralized agent run for 5 minutes")
print(f"  3. Check dashboard - should see fewer false positives")
print(f"\nThe model is now trained on:")
print(f"  • {len(y_normal)} normal samples from centralized agent")
print(f"  • {len(y_attack)} synthetic attack samples")
print(f"  • Should have ~10% false positive rate")
