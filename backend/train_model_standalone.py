"""
Standalone ML Model Training Script
No external dependencies on config.py
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
from pathlib import Path

# Configuration
MODEL_PATH = "ml_engine/models/isolation_forest.joblib"
FEATURE_COLUMNS = [
    "file_operations_per_min",
    "process_cpu_percent",
    "process_memory_mb",
    "network_connections_count",
    "suspicious_extensions_count",
    "rapid_file_changes",
    "encryption_indicators"
]

def generate_training_data(n_samples: int = 1000) -> pd.DataFrame:
    """Generate synthetic normal behavior data for training"""
    np.random.seed(42)
    
    data = {
        # Normal file operations: 0-30 per minute
        "file_operations_per_min": np.random.normal(10, 5, n_samples).clip(0, 30),
        
        # Normal CPU usage: 10-50%
        "process_cpu_percent": np.random.normal(25, 10, n_samples).clip(0, 50),
        
        # Normal memory: 50-300 MB
        "process_memory_mb": np.random.normal(150, 50, n_samples).clip(50, 300),
        
        # Normal network connections: 0-20
        "network_connections_count": np.random.poisson(5, n_samples).clip(0, 20),
        
        # Suspicious extensions: mostly 0 for normal behavior
        "suspicious_extensions_count": np.random.choice([0, 0, 0, 0, 1], n_samples),
        
        # Rapid file changes: 0-5 for normal
        "rapid_file_changes": np.random.poisson(2, n_samples).clip(0, 5),
        
        # Encryption indicators: mostly 0
        "encryption_indicators": np.random.choice([0, 0, 0, 0, 0, 1], n_samples)
    }
    
    return pd.DataFrame(data)

def train_isolation_forest(data: pd.DataFrame) -> IsolationForest:
    """Train Isolation Forest model"""
    print("🎓 Training Isolation Forest model...")
    
    model = IsolationForest(
        contamination=0.1,  # Expect 10% anomalies
        random_state=42,
        n_estimators=100,
        max_samples='auto',
        n_jobs=-1
    )
    
    model.fit(data)
    
    print("✅ Model training complete")
    return model

def evaluate_model(model: IsolationForest, data: pd.DataFrame):
    """Evaluate model on training data"""
    predictions = model.predict(data)
    scores = model.score_samples(data)
    
    n_anomalies = (predictions == -1).sum()
    n_normal = (predictions == 1).sum()
    
    print(f"\n📊 Model Evaluation:")
    print(f"  Normal samples: {n_normal}")
    print(f"  Anomalies detected: {n_anomalies}")
    print(f"  Anomaly rate: {n_anomalies/len(data)*100:.2f}%")
    print(f"  Score range: [{scores.min():.3f}, {scores.max():.3f}]")
    print(f"  Mean score: {scores.mean():.3f}")

def save_model(model: IsolationForest, path: str):
    """Save trained model"""
    model_path = Path(path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(model, model_path)
    print(f"💾 Model saved to {model_path}")

def main():
    print("🚀 Starting ML model training...\n")
    
    # Generate training data
    print("📊 Generating training data...")
    training_data = generate_training_data(n_samples=2000)
    print(f"✅ Generated {len(training_data)} training samples")
    print(f"\nFeatures: {list(training_data.columns)}\n")
    
    # Train model
    model = train_isolation_forest(training_data)
    
    # Evaluate
    evaluate_model(model, training_data)
    
    # Save model
    save_model(model, MODEL_PATH)
    
    print("\n✅ Training complete! Model is ready for use.")
    print(f"\nModel location: {Path(MODEL_PATH).absolute()}")

if __name__ == "__main__":
    main()
