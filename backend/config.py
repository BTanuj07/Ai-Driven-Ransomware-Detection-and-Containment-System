import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Get the directory where this config file is located (backend/)
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file in the backend directory
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

print(f"📁 Loading .env from: {env_path}")
print(f"✅ .env loaded: {env_path.exists()}")

class Config:
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPICS = {
        "endpoint_logs": "endpoint_logs",
        "network_logs": "network_logs",
        "alerts": "alerts"
    }
    
    # MongoDB Configuration
    # Try with authentication first, fallback to no auth
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    MONGODB_DB_NAME = "arcs_db"
    
    # ML Model Configuration
    ML_MODEL_PATH = "ml_engine/models/isolation_forest.joblib"
    ANOMALY_THRESHOLD = -0.2  # Raised: only real anomalies trigger (was -0.5)

    # Risk Scoring Thresholds
    RISK_THRESHOLDS = {
        "LOW": 0.30,
        "MEDIUM": 0.55,
        "HIGH": 0.75   # Raised: needs strong indicators (was 0.8)
    }
    
    # Response Configuration
    AUTO_CONTAINMENT_ENABLED = True
    HIGH_RISK_AUTO_RESPONSE = True
    
    # Feature Configuration — 15 features
    FEATURE_COLUMNS = [
        "file_operations_per_min",
        "process_cpu_percent",
        "process_memory_mb",
        "network_connections_count",
        "suspicious_extensions_count",
        "rapid_file_changes",
        "encryption_indicators",
        "disk_read_mb",
        "disk_write_mb",
        "open_handles",
        "child_processes",
        "network_bytes_sent_kb",
        "network_bytes_recv_kb",
        "login_attempts",
        "privilege_escalations"
    ]
    
    # Behavioral Patterns
    SUSPICIOUS_EXTENSIONS = [
        ".encrypted", ".locked", ".crypto", ".crypt", ".enc",
        ".locky", ".cerber", ".zepto", ".thor", ".aaa"
    ]
    
    # Network Graph Configuration
    NETWORK_GRAPH_UPDATE_INTERVAL = 30  # seconds
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        return {
            "kafka": {
                "bootstrap_servers": cls.KAFKA_BOOTSTRAP_SERVERS,
                "topics": cls.KAFKA_TOPICS
            },
            "mongodb": {
                "url": cls.MONGODB_URL,
                "db_name": cls.MONGODB_DB_NAME
            },
            "ml": {
                "model_path": cls.ML_MODEL_PATH,
                "threshold": cls.ANOMALY_THRESHOLD
            }
        }

config = Config()
