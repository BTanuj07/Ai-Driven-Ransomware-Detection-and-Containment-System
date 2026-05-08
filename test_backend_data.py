f"""
Quick test to check backend data and generate sample data if needed
"""
import sys
sys.path.insert(0, 'backend')

from services.database import DatabaseService
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

def check_data():
    print("🔍 Checking MongoDB data...")
    db = DatabaseService()
    
    # Check collections
    alerts = db.get_recent_alerts(10)
    logs = db.get_recent_logs(10)
    risk_scores = db.get_risk_scores()
    
    print(f"\n📊 Current Data:")
    print(f"   Alerts: {len(alerts)}")
    print(f"   Logs: {len(logs)}")
    print(f"   Risk Scores: {len(risk_scores)}")
    
    if len(alerts) == 0:
        print("\n⚠️  No data found! Generating sample data...")
        generate_sample_data(db)
    else:
        print("\n✅ Data exists in database")
        print(f"\n📋 Recent Alerts:")
        for alert in alerts[:3]:
            print(f"   - {alert.get('hostname')}: {alert.get('risk_level')} ({alert.get('risk_score', 0):.2f})")

def generate_sample_data(db):
    """Generate sample data for testing"""
    
    # Sample alert
    sample_alert = {
        "hostname": "WORKSTATION-01",
        "endpoint": "WORKSTATION-01",
        "attack_type": "Ransomware Encryption",
        "risk_level": "HIGH",
        "risk_score": 0.92,
        "anomaly_score": 0.88,
        "message": "Suspicious ransomware-like activity detected",
        "timestamp": datetime.now(IST),
        "details": {
            "file_operations_per_min": 250,
            "process_cpu_percent": 85.5,
            "process_memory_mb": 1024,
            "network_connections_count": 45,
            "suspicious_extensions_count": 15,
            "rapid_file_changes": 120,
            "encryption_indicators": 5
        }
    }
    
    # Insert sample data
    db.insert_alert(sample_alert)
    
    # Sample log
    sample_log = {
        "hostname": "WORKSTATION-01",
        "timestamp": datetime.now(IST),
        "file_operations_per_min": 250,
        "process_cpu_percent": 85.5,
        "process_memory_mb": 1024,
        "network_connections_count": 45,
        "suspicious_extensions_count": 15,
        "rapid_file_changes": 120,
        "encryption_indicators": 5,
        "disk_read_mb": 150,
        "disk_write_mb": 200,
        "open_handles": 500,
        "child_processes": 10,
        "network_bytes_sent_kb": 300,
        "network_bytes_recv_kb": 150,
        "login_attempts": 0,
        "privilege_escalations": 0
    }
    
    db.insert_log(sample_log)
    
    # Sample risk score
    sample_risk = {
        "hostname": "WORKSTATION-01",
        "risk_level": "HIGH",
        "risk_score": 0.92,
        "anomaly_score": 0.88,
        "timestamp": datetime.now(IST),
        "features": sample_log
    }
    
    db.insert_risk_score(sample_risk)
    
    # Sample containment action
    sample_action = {
        "hostname": "WORKSTATION-01",
        "risk_level": "HIGH",
        "action": "ISOLATE: Network isolation enabled for WORKSTATION-01",
        "timestamp": datetime.now(IST),
        "details": {"reason": "High risk ransomware activity detected"}
    }
    
    db.insert_containment_action(sample_action)
    
    # Update system status
    db.update_system_status("WORKSTATION-01", {
        "status": "contained",
        "risk_level": "HIGH",
        "last_action": "Network isolation enabled"
    })
    
    print("✅ Sample data generated!")
    print("\n📋 Generated:")
    print("   - 1 HIGH risk alert")
    print("   - 1 log entry")
    print("   - 1 risk score")
    print("   - 1 containment action")
    print("   - 1 system status")
    print("\n🔄 Refresh your dashboard to see the data!")

if __name__ == "__main__":
    check_data()
