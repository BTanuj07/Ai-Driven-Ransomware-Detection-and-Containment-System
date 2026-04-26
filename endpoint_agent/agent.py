import psutil
import time
import json
import socket
from kafka import KafkaProducer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List
import os
from pathlib import Path

class FileMonitor(FileSystemEventHandler):
    """Monitor file system events"""
    
    def __init__(self):
        self.file_operations = []
        self.suspicious_extensions = [
            ".encrypted", ".locked", ".crypto", ".crypt", ".enc",
            ".locky", ".cerber", ".zepto", ".thor", ".aaa"
        ]
    
    def on_created(self, event):
        if not event.is_directory:
            self.file_operations.append({
                "type": "created",
                "path": event.src_path,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.file_operations.append({
                "type": "deleted",
                "path": event.src_path,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def on_modified(self, event):
        if not event.is_directory:
            self.file_operations.append({
                "type": "modified",
                "path": event.src_path,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def get_metrics(self) -> Dict:
        """Calculate file operation metrics"""
        now = datetime.utcnow()
        one_min_ago = now - timedelta(minutes=1)
        
        # Count operations in last minute
        recent_ops = [
            op for op in self.file_operations
            if datetime.fromisoformat(op["timestamp"]) > one_min_ago
        ]
        
        # Count suspicious extensions
        suspicious_count = sum(
            1 for op in recent_ops
            if any(op["path"].endswith(ext) for ext in self.suspicious_extensions)
        )
        
        # Detect rapid file changes (same file modified multiple times)
        file_change_count = defaultdict(int)
        for op in recent_ops:
            file_change_count[op["path"]] += 1
        
        rapid_changes = sum(1 for count in file_change_count.values() if count > 3)
        
        # Clear old operations
        self.file_operations = recent_ops
        
        return {
            "file_operations_per_min": len(recent_ops),
            "suspicious_extensions_count": suspicious_count,
            "rapid_file_changes": rapid_changes
        }

class EndpointAgent:
    """Endpoint monitoring agent"""
    
    def __init__(self, kafka_bootstrap_servers: str = "localhost:9092"):
        self.hostname = socket.gethostname()
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.producer = None
        self.file_monitor = FileMonitor()
        self.observer = None
        self.running = False
        
        self._init_kafka()
        self._init_file_monitor()
    
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
            print("⚠️ Running in offline mode (no data will be sent)")
    
    def _init_file_monitor(self):
        """Initialize file system monitor"""
        # Monitor user's home directory or a test directory
        monitor_path = os.path.expanduser("~/arcs_monitor")
        Path(monitor_path).mkdir(exist_ok=True)
        
        self.observer = Observer()
        self.observer.schedule(self.file_monitor, monitor_path, recursive=True)
        self.observer.start()
        print(f"✅ Monitoring directory: {monitor_path}")
    
    def collect_metrics(self) -> Dict:
        """Collect all endpoint metrics"""
        # Process metrics
        process = psutil.Process()
        cpu_percent = process.cpu_percent(interval=0.1)
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
        
        # Network connections
        connections = psutil.net_connections(kind='inet')
        connection_count = len(connections)
        
        # File operation metrics
        file_metrics = self.file_monitor.get_metrics()
        
        # Detect encryption indicators
        encryption_indicators = self._detect_encryption_indicators()
        
        metrics = {
            "hostname": self.hostname,
            "timestamp": datetime.utcnow().isoformat(),
            "process_cpu_percent": cpu_percent,
            "process_memory_mb": memory_mb,
            "network_connections_count": connection_count,
            "encryption_indicators": encryption_indicators,
            **file_metrics
        }
        
        return metrics
    
    def _detect_encryption_indicators(self) -> int:
        """Detect potential encryption activity"""
        indicators = 0
        
        # Check for high CPU usage (encryption is CPU-intensive)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > 80:
            indicators += 1
        
        # Check for suspicious process names
        suspicious_names = ["encrypt", "crypt", "ransom", "locker"]
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if any(name in proc_name for name in suspicious_names):
                    indicators += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return indicators
    
    def send_to_kafka(self, metrics: Dict):
        """Send metrics to Kafka"""
        if self.producer:
            try:
                self.producer.send("endpoint_logs", metrics)
                self.producer.flush()
            except Exception as e:
                print(f"❌ Failed to send to Kafka: {e}")
    
    def run(self, interval: int = 5):
        """Run the agent continuously"""
        self.running = True
        print(f"🚀 Endpoint agent started on {self.hostname}")
        print(f"📊 Collecting metrics every {interval} seconds")
        
        try:
            while self.running:
                # Collect and send metrics
                metrics = self.collect_metrics()
                self.send_to_kafka(metrics)
                
                # Print summary
                print(f"📤 Sent metrics: CPU={metrics['process_cpu_percent']:.1f}%, "
                      f"Mem={metrics['process_memory_mb']:.1f}MB, "
                      f"FileOps={metrics['file_operations_per_min']}, "
                      f"NetConns={metrics['network_connections_count']}")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n🛑 Stopping agent...")
            self.stop()
    
    def stop(self):
        """Stop the agent"""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.producer:
            self.producer.close()
        print("✅ Agent stopped")

if __name__ == "__main__":
    agent = EndpointAgent()
    agent.run(interval=5)
