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

def create_infected_metrics(hostname, endpoint_type="workstation", risk_level="HIGH"):
    """Generate infected endpoint metrics with specified risk level"""
    
    if risk_level == "LOW":
        # LOW risk - Suspicious but not critical
        return {
            "hostname": hostname,
            "endpoint_type": endpoint_type,
            "timestamp": datetime.utcnow().isoformat(),
            "file_operations_per_min": random.randint(30, 60),  # Slightly elevated
            "process_cpu_percent": random.randint(40, 60),  # Moderate CPU
            "process_memory_mb": random.randint(1000, 2000),  # Normal memory
            "network_connections_count": random.randint(5, 15),  # Few connections
            "suspicious_extensions_count": random.randint(1, 3),  # Few suspicious files
            "rapid_file_changes": random.randint(10, 25),  # Some file activity
            "encryption_indicators": random.randint(0, 1),  # Minimal encryption
            "source_ip": f"192.168.1.{random.randint(10, 250)}",
            "destination_ip": f"192.168.1.{random.randint(10, 250)}",
            "port_scan_detected": 0,
            "usb_device_connected": 0,
            "hidden_process_count": random.randint(0, 1),
            "suspicious_process_count": random.randint(0, 1)
        }
    
    elif risk_level == "MEDIUM":
        # MEDIUM risk - Concerning behavior
        return {
            "hostname": hostname,
            "endpoint_type": endpoint_type,
            "timestamp": datetime.utcnow().isoformat(),
            "file_operations_per_min": random.randint(80, 120),  # Elevated
            "process_cpu_percent": random.randint(65, 80),  # High CPU
            "process_memory_mb": random.randint(2500, 4000),  # High memory
            "network_connections_count": random.randint(15, 30),  # Moderate connections
            "suspicious_extensions_count": random.randint(5, 15),  # Some encrypted files
            "rapid_file_changes": random.randint(30, 60),  # Moderate encryption
            "encryption_indicators": random.randint(2, 4),  # Some encryption
            "source_ip": f"192.168.1.{random.randint(10, 250)}",
            "destination_ip": f"192.168.1.{random.randint(10, 250)}",
            "port_scan_detected": random.randint(0, 1),
            "usb_device_connected": 0,
            "hidden_process_count": random.randint(1, 2),
            "suspicious_process_count": random.randint(1, 3)
        }
    
    else:  # HIGH risk
        # HIGH risk - Critical ransomware activity
        return {
            "hostname": hostname,
            "endpoint_type": endpoint_type,
            "timestamp": datetime.utcnow().isoformat(),
            "file_operations_per_min": random.randint(150, 300),  # Very high
            "process_cpu_percent": random.randint(85, 99),  # Critical CPU
            "process_memory_mb": random.randint(4000, 8000),  # Critical memory
            "network_connections_count": random.randint(30, 60),  # Lateral movement
            "suspicious_extensions_count": random.randint(10, 50),  # Many encrypted files
            "rapid_file_changes": random.randint(50, 150),  # Mass encryption
            "encryption_indicators": random.randint(3, 8),  # Heavy encryption
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
    print("   1. LOW risk attack (1 endpoint)")
    print("   2. MEDIUM risk attack (1 endpoint)")
    print("   3. HIGH risk attack (1 endpoint)")
    print("   4. Mixed attack (3 endpoints - LOW, MEDIUM, HIGH)")
    print("   5. Large attack (5 endpoints - random risk levels)")
    print("   6. Custom attack (choose endpoint and risk level)")
    print("   7. Quick test - WS-05 HIGH risk")
    print("   8. Exit")
    
    choice = input("\n👉 Select option (1-8): ").strip()
    
    targets = []
    risk_levels = []
    
    if choice == "1":
        targets = [random.choice(docker_endpoints["workstations"])]
        risk_levels = ["LOW"]
    elif choice == "2":
        targets = [random.choice(docker_endpoints["workstations"])]
        risk_levels = ["MEDIUM"]
    elif choice == "3":
        targets = [random.choice(docker_endpoints["workstations"])]
        risk_levels = ["HIGH"]
    elif choice == "4":
        all_endpoints = docker_endpoints["workstations"] + docker_endpoints["servers"]
        targets = random.sample(all_endpoints, 3)
        risk_levels = ["LOW", "MEDIUM", "HIGH"]
    elif choice == "5":
        all_endpoints = docker_endpoints["workstations"] + docker_endpoints["servers"] + docker_endpoints["databases"]
        targets = random.sample(all_endpoints, 5)
        risk_levels = [random.choice(["LOW", "MEDIUM", "HIGH"]) for _ in range(5)]
    elif choice == "6":
        hostname = input("Enter endpoint hostname (e.g., WS-05, DB-01): ").strip().upper()
        all_endpoints = docker_endpoints["workstations"] + docker_endpoints["servers"] + docker_endpoints["databases"]
        if hostname in all_endpoints:
            targets = [hostname]
            print("\nSelect risk level:")
            print("   1. LOW")
            print("   2. MEDIUM")
            print("   3. HIGH")
            risk_choice = input("👉 Select (1-3): ").strip()
            if risk_choice == "1":
                risk_levels = ["LOW"]
            elif risk_choice == "2":
                risk_levels = ["MEDIUM"]
            elif risk_choice == "3":
                risk_levels = ["HIGH"]
            else:
                print("❌ Invalid risk level, using HIGH")
                risk_levels = ["HIGH"]
        else:
            print(f"❌ Invalid hostname: {hostname}")
            return
    elif choice == "7":
        targets = ["WS-05"]
        risk_levels = ["HIGH"]
    elif choice == "8":
        print("\n👋 Exiting...")
        return
    else:
        print("\n❌ Invalid option")
        return
    
    if not targets:
        print("\n❌ No targets selected")
        return
    
    print(f"\n🦠 Simulating attack on {len(targets)} endpoint(s):")
    for target, risk in zip(targets, risk_levels):
        risk_emoji = "🟢" if risk == "LOW" else "🟡" if risk == "MEDIUM" else "🔴"
        print(f"   {risk_emoji} {target} - {risk} risk")
    
    print(f"\n📤 Sending attack metrics (30 seconds)...")
    print("   This will trigger alerts in the dashboard")
    print("   Press Ctrl+C to stop\n")
    
    try:
        for i in range(60):  # Send for 60 iterations (30 seconds at 0.5s interval)
            for target, risk_level in zip(targets, risk_levels):
                metrics = create_infected_metrics(target, "workstation", risk_level)
                producer.send("endpoint_logs", metrics)
                
                # Print status every 10 iterations
                if i % 10 == 0:
                    risk_emoji = "🟢" if risk_level == "LOW" else "🟡" if risk_level == "MEDIUM" else "🔴"
                    print(f"  {risk_emoji} [{target}] {risk_level} - CPU: {metrics['process_cpu_percent']}%, "
                          f"FileOps: {metrics['file_operations_per_min']}, "
                          f"Encryption: {metrics['encryption_indicators']}")
            
            producer.flush()
            time.sleep(0.5)
        
        print(f"\n✅ Attack simulation complete!")
        print(f"   Sent metrics for {len(targets)} endpoint(s)")
        print(f"\n🔍 Check the dashboard:")
        print(f"   • Alerts panel should show alerts with different risk levels")
        print(f"   • Network Topology should show infected nodes")
        print(f"   • Risk Overview should show risk distribution")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        producer.close()
        print("\n✅ Kafka producer closed")

if __name__ == "__main__":
    main()
