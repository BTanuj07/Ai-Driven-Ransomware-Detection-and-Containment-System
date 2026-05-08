python centralized_agent.py#!/usr/bin/env python3
"""
ARCS Centralized Monitoring Agent
Monitors multiple endpoints from a single agent:
- Local machine (BEAST)
- Docker containers (WS-01 to WS-10, servers, databases)
- Remote machines (via SSH - optional)
"""

import psutil
import time
import json
import socket
import os
import platform
import docker
from kafka import KafkaProducer
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import threading
from collections import defaultdict
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))

SUSPICIOUS_EXTENSIONS = {
    ".encrypted", ".locked", ".crypto", ".crypt", ".enc",
    ".locky", ".cerber", ".zepto", ".thor", ".aaa", ".wnry"
}

class EndpointMonitor:
    """Base class for monitoring an endpoint"""
    
    def __init__(self, hostname: str, endpoint_type: str = "workstation"):
        self.hostname = hostname
        self.endpoint_type = endpoint_type
        self.baseline = {}
    
    def collect_metrics(self) -> Dict:
        """Override in subclasses"""
        raise NotImplementedError
    
    def establish_baseline(self):
        """Establish baseline metrics"""
        metrics = self.collect_metrics()
        self.baseline = {
            "cpu": metrics.get("process_cpu_percent", 0),
            "memory": metrics.get("process_memory_mb", 0),
            "network": metrics.get("network_connections_count", 0)
        }
        return self.baseline


class LocalEndpointMonitor(EndpointMonitor):
    """Monitor local machine (BEAST)"""
    
    def __init__(self, hostname: str = None):
        if hostname is None:
            hostname = socket.gethostname()
        super().__init__(hostname, "workstation")
        self.file_ops = []
        self.monitor_path = Path.home() / "arcs_monitor"
        self.monitor_path.mkdir(exist_ok=True)
    
    def collect_metrics(self) -> Dict:
        """Collect metrics from local machine"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Network connections
            connections = len(psutil.net_connections(kind='inet'))
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            
            # Process info
            process = psutil.Process()
            process_cpu = process.cpu_percent()
            process_memory = process.memory_info().rss / (1024 * 1024)  # MB
            
            # File operations (check monitor directory)
            file_ops_count = self._count_file_operations()
            
            # Suspicious indicators
            suspicious_extensions = self._check_suspicious_files()
            encryption_indicators = self._detect_encryption_activity()
            
            # USB devices
            usb_devices = self._detect_usb_devices()
            
            # Port scanning detection
            port_scans = self._detect_port_scanning()
            
            # Suspicious processes
            suspicious_procs = self._detect_suspicious_processes()
            
            return {
                "hostname": self.hostname,
                "endpoint_type": self.endpoint_type,
                "timestamp": datetime.now(IST).isoformat(),
                "os": platform.system(),
                "os_version": platform.version(),
                
                # System metrics
                "system_cpu_percent": cpu_percent,
                "system_memory_percent": memory.percent,
                "system_memory_available_mb": memory.available / (1024 * 1024),
                
                # Process metrics
                "process_cpu_percent": process_cpu,
                "process_memory_mb": process_memory,
                
                # Network
                "network_connections_count": connections,
                
                # Disk
                "disk_read_mb": disk_io.read_bytes / (1024 * 1024) if disk_io else 0,
                "disk_write_mb": disk_io.write_bytes / (1024 * 1024) if disk_io else 0,
                
                # File operations
                "file_operations_per_min": file_ops_count,
                "suspicious_extensions_count": suspicious_extensions,
                
                # Security indicators
                "encryption_indicators": encryption_indicators,
                "rapid_file_changes": file_ops_count if file_ops_count > 100 else 0,
                "usb_device_connected": usb_devices,
                "port_scan_detected": port_scans,
                "suspicious_process_count": suspicious_procs,
                "hidden_process_count": 0,
                
                # Baseline deviations
                "cpu_deviation": abs(cpu_percent - self.baseline.get("cpu", cpu_percent)),
                "memory_deviation": abs(memory.percent - self.baseline.get("memory", memory.percent)),
                "network_deviation": abs(connections - self.baseline.get("network", connections))
            }
        except Exception as e:
            print(f"  ⚠️  [{self.hostname}] Error collecting metrics: {e}")
            return self._get_default_metrics()
    
    def _count_file_operations(self) -> int:
        """Count recent file operations"""
        try:
            if not self.monitor_path.exists():
                return 0
            
            cutoff = datetime.now() - timedelta(minutes=1)
            count = 0
            
            for file in self.monitor_path.rglob("*"):
                if file.is_file():
                    mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if mtime > cutoff:
                        count += 1
            
            return count
        except:
            return 0
    
    def _check_suspicious_files(self) -> int:
        """Check for suspicious file extensions"""
        try:
            count = 0
            for file in self.monitor_path.rglob("*"):
                if file.suffix.lower() in SUSPICIOUS_EXTENSIONS:
                    count += 1
            return count
        except:
            return 0
    
    def _detect_encryption_activity(self) -> int:
        """Detect potential encryption activity"""
        # Simple heuristic: high file ops + suspicious extensions
        file_ops = self._count_file_operations()
        suspicious = self._check_suspicious_files()
        
        if file_ops > 100 and suspicious > 5:
            return min(8, suspicious)
        elif file_ops > 50:
            return min(3, suspicious)
        return 0
    
    def _detect_usb_devices(self) -> int:
        """Detect USB device connections"""
        try:
            partitions = psutil.disk_partitions()
            usb_count = sum(1 for p in partitions if 'removable' in p.opts.lower())
            return usb_count
        except:
            return 0
    
    def _detect_port_scanning(self) -> int:
        """Detect potential port scanning"""
        try:
            connections = psutil.net_connections(kind='inet')
            # Check for many connections to different ports
            dest_ports = set()
            for conn in connections:
                if conn.raddr:
                    dest_ports.add(conn.raddr.port)
            
            # If connecting to many different ports, might be scanning
            return 1 if len(dest_ports) > 50 else 0
        except:
            return 0
    
    def _detect_suspicious_processes(self) -> int:
        """Detect suspicious process names"""
        try:
            suspicious_keywords = ['encrypt', 'crypt', 'ransom', 'locker']
            count = 0
            
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name'].lower()
                    if any(keyword in name for keyword in suspicious_keywords):
                        count += 1
                except:
                    pass
            
            return count
        except:
            return 0
    
    def _get_default_metrics(self) -> Dict:
        """Return default metrics on error"""
        return {
            "hostname": self.hostname,
            "endpoint_type": self.endpoint_type,
            "timestamp": datetime.now(IST).isoformat(),
            "process_cpu_percent": 0,
            "process_memory_mb": 0,
            "network_connections_count": 0,
            "file_operations_per_min": 0,
            "encryption_indicators": 0
        }


class DockerEndpointMonitor(EndpointMonitor):
    """Monitor Docker container endpoint"""
    
    def __init__(self, container_name: str, docker_client):
        # Extract hostname from container name (e.g., arcs-ws-01 -> WS-01)
        hostname = container_name.replace("arcs-", "").upper()
        super().__init__(hostname, "workstation")
        self.container_name = container_name
        self.docker_client = docker_client
        self.container = None
        self._connect()
    
    def _connect(self):
        """Connect to Docker container"""
        try:
            self.container = self.docker_client.containers.get(self.container_name)
        except Exception as e:
            print(f"  ⚠️  [{self.hostname}] Failed to connect to container: {e}")
    
    def collect_metrics(self) -> Dict:
        """Collect metrics from Docker container"""
        try:
            if not self.container:
                self._connect()
            
            if not self.container:
                return self._get_default_metrics()
            
            # Get container stats
            stats = self.container.stats(stream=False)
            
            # CPU usage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0
            
            # Memory usage
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_mb = memory_usage / (1024 * 1024)
            
            # Network
            networks = stats.get('networks', {})
            rx_bytes = sum(net.get('rx_bytes', 0) for net in networks.values())
            tx_bytes = sum(net.get('tx_bytes', 0) for net in networks.values())
            
            # Simulate other metrics based on container type
            file_ops = self._simulate_file_ops()
            network_conns = self._simulate_network_connections()
            
            return {
                "hostname": self.hostname,
                "endpoint_type": self.endpoint_type,
                "timestamp": datetime.now(IST).isoformat(),
                "os": "Linux",
                "os_version": "Container",
                
                # Container metrics
                "process_cpu_percent": round(cpu_percent, 2),
                "process_memory_mb": round(memory_mb, 2),
                "network_connections_count": network_conns,
                "network_rx_mb": round(rx_bytes / (1024 * 1024), 2),
                "network_tx_mb": round(tx_bytes / (1024 * 1024), 2),
                
                # Simulated metrics
                "file_operations_per_min": file_ops,
                "suspicious_extensions_count": 0,
                "encryption_indicators": 0,
                "rapid_file_changes": 0,
                "usb_device_connected": 0,
                "port_scan_detected": 0,
                "suspicious_process_count": 0,
                "hidden_process_count": 0,
                
                # Baseline deviations
                "cpu_deviation": 0,
                "memory_deviation": 0,
                "network_deviation": 0
            }
        except Exception as e:
            print(f"  ⚠️  [{self.hostname}] Error collecting metrics: {e}")
            return self._get_default_metrics()
    
    def _simulate_file_ops(self) -> int:
        """Simulate file operations based on endpoint type"""
        import random
        if "WS-" in self.hostname:
            return random.randint(5, 25)
        elif "DB-" in self.hostname:
            return random.randint(40, 80)
        else:
            return random.randint(20, 50)
    
    def _simulate_network_connections(self) -> int:
        """Simulate network connections"""
        import random
        if "WS-" in self.hostname:
            return random.randint(3, 15)
        elif "DB-" in self.hostname:
            return random.randint(20, 60)
        else:
            return random.randint(10, 40)
    
    def _get_default_metrics(self) -> Dict:
        """Return default metrics on error"""
        return {
            "hostname": self.hostname,
            "endpoint_type": self.endpoint_type,
            "timestamp": datetime.now(IST).isoformat(),
            "process_cpu_percent": 0,
            "process_memory_mb": 0,
            "network_connections_count": 0,
            "file_operations_per_min": 0,
            "encryption_indicators": 0
        }


class CentralizedMonitoringAgent:
    """Centralized agent that monitors multiple endpoints"""
    
    def __init__(self, kafka_bootstrap_servers: str = "localhost:9092"):
        self.kafka_servers = kafka_bootstrap_servers
        self.producer = None
        self.monitors: List[EndpointMonitor] = []
        self.running = False
        
        self._init_kafka()
        self._discover_endpoints()
    
    def _init_kafka(self):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print(f"✅ Connected to Kafka at {self.kafka_servers}")
        except Exception as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            exit(1)
    
    def _discover_endpoints(self):
        """Discover all endpoints to monitor"""
        print("\n🔍 Discovering endpoints...")
        
        # 1. Add local machine (BEAST)
        local_monitor = LocalEndpointMonitor()
        self.monitors.append(local_monitor)
        print(f"  ✅ Local machine: {local_monitor.hostname}")
        
        # 2. Discover Docker containers
        try:
            docker_client = docker.from_env()
            containers = docker_client.containers.list()
            
            docker_count = 0
            for container in containers:
                name = container.name
                # Only monitor ARCS endpoint containers
                if name.startswith("arcs-") and name not in ["arcs-kafka", "arcs-zookeeper", "arcs-mongodb"]:
                    monitor = DockerEndpointMonitor(name, docker_client)
                    self.monitors.append(monitor)
                    docker_count += 1
            
            print(f"  ✅ Docker containers: {docker_count} endpoints")
        except Exception as e:
            print(f"  ⚠️  Docker not available: {e}")
        
        print(f"\n📊 Total endpoints to monitor: {len(self.monitors)}")
        for monitor in self.monitors:
            print(f"     • {monitor.hostname} ({monitor.endpoint_type})")
    
    def establish_baselines(self):
        """Establish baseline metrics for all endpoints"""
        print("\n📊 Establishing baseline metrics...")
        for monitor in self.monitors:
            try:
                baseline = monitor.establish_baseline()
                print(f"  ✅ {monitor.hostname}: CPU={baseline.get('cpu', 0):.1f}%, "
                      f"Mem={baseline.get('memory', 0):.1f}%, "
                      f"Net={baseline.get('network', 0)}")
            except Exception as e:
                print(f"  ⚠️  {monitor.hostname}: Failed to establish baseline - {e}")
    
    def collect_all_metrics(self) -> List[Dict]:
        """Collect metrics from all endpoints"""
        metrics_list = []
        
        for monitor in self.monitors:
            try:
                metrics = monitor.collect_metrics()
                metrics_list.append(metrics)
            except Exception as e:
                print(f"  ⚠️  [{monitor.hostname}] Error: {e}")
        
        return metrics_list
    
    def send_metrics(self, metrics_list: List[Dict]):
        """Send metrics to Kafka"""
        for metrics in metrics_list:
            try:
                self.producer.send("endpoint_logs", metrics)
            except Exception as e:
                print(f"  ❌ [{metrics.get('hostname')}] Failed to send: {e}")
        
        self.producer.flush()
    
    def run(self, interval: int = 5):
        """Run the centralized monitoring agent"""
        self.running = True
        
        print("\n" + "=" * 70)
        print("  🚀 CENTRALIZED MONITORING AGENT STARTED")
        print("=" * 70)
        print(f"\n📡 Monitoring {len(self.monitors)} endpoints")
        print(f"⏱️  Collection interval: {interval} seconds")
        print(f"📤 Sending to Kafka: {self.kafka_servers}")
        print("\n💡 Press Ctrl+C to stop\n")
        
        # Establish baselines
        self.establish_baselines()
        
        print("\n🔄 Starting continuous monitoring...\n")
        
        iteration = 0
        try:
            while self.running:
                iteration += 1
                
                # Collect metrics from all endpoints
                metrics_list = self.collect_all_metrics()
                
                # Send to Kafka
                self.send_metrics(metrics_list)
                
                # Print summary
                if iteration % 5 == 0:
                    print(f"\n📊 Iteration {iteration} - Monitoring {len(metrics_list)} endpoints:")
                    for metrics in metrics_list:
                        status = "🟢"
                        if metrics.get("encryption_indicators", 0) > 0:
                            status = "🔴"
                        elif metrics.get("file_operations_per_min", 0) > 100:
                            status = "🟡"
                        
                        print(f"  {status} [{metrics['hostname']}] "
                              f"CPU={metrics.get('process_cpu_percent', 0):.1f}% "
                              f"Mem={metrics.get('process_memory_mb', 0):.0f}MB "
                              f"FileOps={metrics.get('file_operations_per_min', 0)} "
                              f"Enc={metrics.get('encryption_indicators', 0)}")
                else:
                    print(f"  📤 Iteration {iteration}: Sent metrics for {len(metrics_list)} endpoints", end="\r")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the monitoring agent"""
        self.running = False
        if self.producer:
            self.producer.close()
        print("\n✅ Centralized monitoring agent stopped")


def main():
    """Main function"""
    print("=" * 70)
    print("  ARCS - Centralized Monitoring Agent")
    print("  Monitors multiple endpoints from a single agent")
    print("=" * 70)
    
    agent = CentralizedMonitoringAgent()
    agent.run(interval=5)


if __name__ == "__main__":
    main()
