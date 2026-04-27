#!/usr/bin/env python3
"""
Quick script to trigger ransomware attack on Docker endpoints
This will simulate infected behavior on specific Docker endpoints
"""

import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime

def create_infected_metrics(hostname, endpoint_type="workstation"):
    """Generate infected endpoint metrics"""
    return {
        "hostname": hostname,
        "endpoint_type": endpoint_type,
        "timestamp": datetime.utcnow().isoformat(),
        "file_operations_per_min": random.randint(150, 300),  # HIGH
        "process_cpu_percent": random.randint(85, 99),  # HIGH
        "process_memory_mb": random.randint(4000, 8000),  # HIGH
        "network_connections_count": random.randint(30, 60),  # Lateral movement
        "suspicious_extensions_count": random.randint(10, 50),  # .encrypted files
        "rapid_file_changes": random.randint(50, 150),  # Mass encryption
        "encryption_indicators": random.randint(3, 8),  # Encryption activity
        "source_ip": f"192.168.1.{random.randint(10, 250)}",
        "destination_ip": f"192.168.1.{random.randint(10, 250)}",
        "port_scan_detected": random.randint(0, 1),
        "usb_device_connected": 0,
        "hidden_process_count": random.randint(1, 3),
        "suspicious_process_count": random.randint(2, 5)
    }

def main():
    print("=" * 70)
    print("  🦠 DOCKER ENDPOINT ATTACK SIMULATOR")
    print("=" * 70)
    
    # Connect to Kafka
    try:
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("\n✅ Connected to Kafka at localhost:9092")
    except Exception as e:
        print(f"\n❌ Failed to connect to Kafka: {e}")
        print("⚠️  Make sure Kafka is running: docker-compose up -d")
        return
    
    # Available Docker endpoints
    docker_endpoints = {
        "workstations": [f"WS-{i:02d}" for i in range(1, 11)],
        "servers": ["WEB-01", "APP-01", "FILE-01", "MAIL-01", "DNS-01"],
        "databases": ["DB-01", "DB-02", "DB-BACKUP"]
    }
    
    print("\n📋 Available Docker Endpoints:")
    print(f"   Workstations: {', '.join(docker_endpoints['workstations'])}")
    print(f"   Servers: {', '.join(docker_endpoints['servers'])}")
    print(f"   Databases: {', '.join(docker_endpoints['databases'])}")
    
    print("\n🎯 Attack Options:")
    print("   1. Infect 1 random workstation")
    print("   2. Infect 3 random endpoints (any type)")
    print("   3. Infect 5 random endpoints (large attack)")
    print("   4. Infect specific endpoint (manual)")
    print("   5. Infect WS-05 (quick test)")
    print("   6. Exit")
    
    choice = input("\n👉 Select option (1-6): ").strip()
    
    targets = []
    
    if choice == "1":
        targets = [random.choice(docker_endpoints["workstations"])]
        endpoint_types = ["workstation"]
    elif choice == "2":
        all_endpoints = docker_endpoints["workstations"] + docker_endpoints["servers"] + docker_endpoints["databases"]
        targets = random.sample(all_endpoints, 3)
        endpoint_types = ["workstation"] * len(targets)
    elif choice == "3":
        all_endpoints = docker_endpoints["workstations"] + docker_endpoints["servers"] + docker_endpoints["databases"]
        targets = random.sample(all_endpoints, 5)
        endpoint_types = ["workstation"] * len(targets)
    elif choice == "4":
        hostname = input("Enter endpoint hostname (e.g., WS-05, DB-01): ").strip().upper()
        all_endpoints = docker_endpoints["workstations"] + docker_endpoints["servers"] + docker_endpoints["databases"]
        if hostname in all_endpoints:
            targets = [hostname]
            endpoint_types = ["workstation"]
        else:
            print(f"❌ Invalid hostname: {hostname}")
            return
    elif choice == "5":
        targets = ["WS-05"]
        endpoint_types = ["workstation"]
    elif choice == "6":
        print("\n👋 Exiting...")
        return
    else:
        print("\n❌ Invalid option")
        return
    
    if not targets:
        print("\n❌ No targets selected")
        return
    
    print(f"\n🦠 Infecting {len(targets)} endpoint(s):")
    for target in targets:
        print(f"   • {target}")
    
    print(f"\n📤 Sending infected metrics (30 seconds)...")
    print("   This will trigger HIGH risk alerts in the dashboard")
    print("   Press Ctrl+C to stop\n")
    
    try:
        for i in range(60):  # Send for 60 iterations (30 seconds at 0.5s interval)
            for target, endpoint_type in zip(targets, endpoint_types):
                metrics = create_infected_metrics(target, endpoint_type)
                producer.send("endpoint_logs", metrics)
                
                # Print status every 10 iterations
                if i % 10 == 0:
                    print(f"  [{target}] 🚨 INFECTED - CPU: {metrics['process_cpu_percent']}%, "
                          f"FileOps: {metrics['file_operations_per_min']}, "
                          f"Encryption: {metrics['encryption_indicators']}")
            
            producer.flush()
            time.sleep(0.5)
        
        print(f"\n✅ Attack simulation complete!")
        print(f"   Sent infected metrics for {len(targets)} endpoint(s)")
        print(f"\n🔍 Check the dashboard:")
        print(f"   • Alerts panel should show HIGH risk alerts")
        print(f"   • Network Topology should show infected nodes in red")
        print(f"   • Risk Overview should show elevated risk scores")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        producer.close()
        print("\n✅ Kafka producer closed")

if __name__ == "__main__":
    main()
