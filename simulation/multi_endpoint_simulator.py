#!/usr/bin/env python3
"""
Multi-Endpoint Simulator for ARCS
Simulates multiple endpoints (workstations, servers, databases) in an enterprise network
"""

import random
import time
import json
import socket
from kafka import KafkaProducer
from datetime import datetime
import threading

class EnterpriseEndpoint:
    """Represents a single endpoint in the enterprise network"""
    
    def __init__(self, hostname, endpoint_type, kafka_producer):
        self.hostname = hostname
        self.endpoint_type = endpoint_type  # workstation, server, database
        self.producer = kafka_producer
        self.running = False
        self.is_infected = False
        
        # Different behavior patterns based on type
        if endpoint_type == "workstation":
            self.base_file_ops = random.randint(10, 30)
            self.base_cpu = random.randint(20, 40)
            self.base_memory = random.randint(2000, 4000)
            self.base_network = random.randint(5, 15)
        elif endpoint_type == "server":
            self.base_file_ops = random.randint(30, 60)
            self.base_cpu = random.randint(40, 70)
            self.base_memory = random.randint(8000, 16000)
            self.base_network = random.randint(20, 50)
        elif endpoint_type == "database":
            self.base_file_ops = random.randint(50, 100)
            self.base_cpu = random.randint(50, 80)
            self.base_memory = random.randint(16000, 32000)
            self.base_network = random.randint(30, 80)
    
    def generate_normal_metrics(self):
        """Generate normal behavior metrics"""
        return {
            "hostname": self.hostname,
            "endpoint_type": self.endpoint_type,
            "timestamp": datetime.utcnow().isoformat(),
            "file_operations_per_min": self.base_file_ops + random.randint(-5, 5),
            "process_cpu_percent": self.base_cpu + random.randint(-10, 10),
            "process_memory_mb": self.base_memory + random.randint(-500, 500),
            "network_connections_count": self.base_network + random.randint(-3, 3),
            "suspicious_extensions_count": 0,
            "rapid_file_changes": 0,
            "encryption_indicators": 0
        }
    
    def generate_infected_metrics(self):
        """Generate ransomware-infected behavior metrics"""
        return {
            "hostname": self.hostname,
            "endpoint_type": self.endpoint_type,
            "timestamp": datetime.utcnow().isoformat(),
            "file_operations_per_min": random.randint(150, 300),  # High file activity
            "process_cpu_percent": random.randint(85, 99),  # High CPU
            "process_memory_mb": self.base_memory + random.randint(2000, 5000),
            "network_connections_count": random.randint(30, 60),  # Lateral movement
            "suspicious_extensions_count": random.randint(10, 50),  # .encrypted files
            "rapid_file_changes": random.randint(50, 150),  # Mass encryption
            "encryption_indicators": random.randint(3, 8)  # Encryption activity
        }
    
    def send_metrics(self):
        """Send metrics to Kafka"""
        if self.is_infected:
            metrics = self.generate_infected_metrics()
        else:
            metrics = self.generate_normal_metrics()
        
        try:
            self.producer.send("endpoint_logs", metrics)
            self.producer.flush()
            status = "🚨 INFECTED" if self.is_infected else "✅ Normal"
            print(f"  [{self.hostname}] {status} - CPU: {metrics['process_cpu_percent']}%, Files: {metrics['file_operations_per_min']}")
        except Exception as e:
            print(f"  ❌ [{self.hostname}] Failed to send: {e}")
    
    def run(self, interval=5):
        """Run the endpoint simulation"""
        self.running = True
        while self.running:
            self.send_metrics()
            time.sleep(interval)
    
    def infect(self):
        """Simulate ransomware infection"""
        self.is_infected = True
        print(f"\n🦠 [{self.hostname}] INFECTED WITH RANSOMWARE!")
    
    def stop(self):
        """Stop the endpoint simulation"""
        self.running = False

class EnterpriseNetworkSimulator:
    """Simulates an entire enterprise network"""
    
    def __init__(self, kafka_bootstrap_servers="localhost:9092"):
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.producer = None
        self.endpoints = []
        self.threads = []
        
        self._init_kafka()
        self._create_enterprise_network()
    
    def _init_kafka(self):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print(f"✅ Connected to Kafka at {self.kafka_bootstrap_servers}")
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            print("⚠️ Make sure Kafka is running: docker-compose up -d")
            exit(1)
    
    def _create_enterprise_network(self):
        """Create a realistic enterprise network topology"""
        
        # Workstations (10)
        for i in range(1, 11):
            endpoint = EnterpriseEndpoint(
                hostname=f"WS-{i:02d}",
                endpoint_type="workstation",
                kafka_producer=self.producer
            )
            self.endpoints.append(endpoint)
        
        # Servers (5)
        server_names = ["WEB-01", "APP-01", "FILE-01", "MAIL-01", "DNS-01"]
        for name in server_names:
            endpoint = EnterpriseEndpoint(
                hostname=name,
                endpoint_type="server",
                kafka_producer=self.producer
            )
            self.endpoints.append(endpoint)
        
        # Databases (3)
        db_names = ["DB-01", "DB-02", "DB-BACKUP"]
        for name in db_names:
            endpoint = EnterpriseEndpoint(
                hostname=name,
                endpoint_type="database",
                kafka_producer=self.producer
            )
            self.endpoints.append(endpoint)
        
        print(f"\n🏢 Created Enterprise Network:")
        print(f"   • {len([e for e in self.endpoints if e.endpoint_type == 'workstation'])} Workstations")
        print(f"   • {len([e for e in self.endpoints if e.endpoint_type == 'server'])} Servers")
        print(f"   • {len([e for e in self.endpoints if e.endpoint_type == 'database'])} Databases")
        print(f"   • Total: {len(self.endpoints)} Endpoints")
    
    def start_all_endpoints(self, interval=5):
        """Start all endpoints sending normal traffic"""
        print(f"\n🚀 Starting all {len(self.endpoints)} endpoints...")
        print(f"📊 Sending metrics every {interval} seconds\n")
        
        for endpoint in self.endpoints:
            thread = threading.Thread(target=endpoint.run, args=(interval,))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
        
        print("✅ All endpoints running (normal behavior)")
        print("💡 Press Ctrl+C to stop\n")
    
    def simulate_ransomware_attack(self, target_count=3):
        """Simulate ransomware spreading across network"""
        print(f"\n🦠 SIMULATING RANSOMWARE ATTACK!")
        print(f"   Infecting {target_count} random endpoints...\n")
        
        # Select random endpoints to infect
        targets = random.sample(self.endpoints, min(target_count, len(self.endpoints)))
        
        for i, endpoint in enumerate(targets):
            time.sleep(2)  # Stagger infections (lateral movement)
            endpoint.infect()
        
        print(f"\n✅ {len(targets)} endpoints infected")
        print("🔍 Watch the dashboard for HIGH risk alerts!")
    
    def stop_all_endpoints(self):
        """Stop all endpoints"""
        print("\n🛑 Stopping all endpoints...")
        for endpoint in self.endpoints:
            endpoint.stop()
        
        if self.producer:
            self.producer.close()
        
        print("✅ All endpoints stopped")

def main():
    """Main function"""
    print("=" * 70)
    print("  ARCS - Multi-Endpoint Enterprise Network Simulator")
    print("=" * 70)
    
    simulator = EnterpriseNetworkSimulator()
    
    print("\n📋 Simulation Options:")
    print("   1. Normal Enterprise Traffic (all endpoints)")
    print("   2. Ransomware Attack Simulation (infect 3 endpoints)")
    print("   3. Large-Scale Attack (infect 5 endpoints)")
    print("   4. Exit")
    
    try:
        choice = input("\n👉 Select option (1-4): ").strip()
        
        if choice == "1":
            print("\n🏢 Starting normal enterprise traffic...")
            simulator.start_all_endpoints(interval=5)
            
            # Keep running
            while True:
                time.sleep(1)
        
        elif choice == "2":
            print("\n🏢 Starting normal enterprise traffic...")
            simulator.start_all_endpoints(interval=5)
            
            # Wait 10 seconds for normal baseline
            print("\n⏳ Establishing normal baseline (10 seconds)...")
            time.sleep(10)
            
            # Launch attack
            simulator.simulate_ransomware_attack(target_count=3)
            
            # Keep running
            print("\n📊 Monitoring infected endpoints...")
            while True:
                time.sleep(1)
        
        elif choice == "3":
            print("\n🏢 Starting normal enterprise traffic...")
            simulator.start_all_endpoints(interval=5)
            
            # Wait 10 seconds for normal baseline
            print("\n⏳ Establishing normal baseline (10 seconds)...")
            time.sleep(10)
            
            # Launch large attack
            simulator.simulate_ransomware_attack(target_count=5)
            
            # Keep running
            print("\n📊 Monitoring infected endpoints...")
            while True:
                time.sleep(1)
        
        elif choice == "4":
            print("\n👋 Exiting...")
            return
        
        else:
            print("\n❌ Invalid option")
            return
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        simulator.stop_all_endpoints()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        simulator.stop_all_endpoints()

if __name__ == "__main__":
    main()
