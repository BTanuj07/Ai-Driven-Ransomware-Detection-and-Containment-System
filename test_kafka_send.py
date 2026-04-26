"""Quick test to send data to Kafka"""
import json
from kafka import KafkaProducer
import time

# Create producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send test ransomware data
test_data = {
    "hostname": "TEST-MACHINE",
    "file_operations_per_min": 150,  # High - suspicious
    "process_cpu_percent": 85,  # High
    "process_memory_mb": 500,
    "network_connections_count": 45,
    "suspicious_extensions_count": 10,  # High - ransomware indicator
    "rapid_file_changes": 30,  # High - encryption activity
    "encryption_indicators": 3  # High
}

print("📤 Sending test ransomware data to Kafka...")
producer.send("endpoint_logs", test_data)
producer.flush()
print("✅ Data sent! Check backend logs for alerts.")
print("\nWait 5 seconds then check: http://localhost:8000/api/alerts")

time.sleep(5)
producer.close()
