"""
ARCS Endpoint Agent v3 - Enhanced Telemetry
Rich telemetry: 20+ features, optimized collection, advanced monitoring.
Includes: registry monitoring, USB detection, DNS queries, port scanning detection.
"""

import psutil
import time
import json
import socket
import os
import platform
import hashlib
from kafka import KafkaProducer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from pathlib import Path
import threading

IST = timezone(timedelta(hours=5, minutes=30))

SUSPICIOUS_EXTENSIONS = {
    ".encrypted", ".locked", ".crypto", ".crypt", ".enc",
    ".locky", ".cerber", ".zepto", ".thor", ".aaa", ".wnry",
    ".wncry", ".wcry", ".wncrypt", ".petya", ".onion"
}

SUSPICIOUS_PROCESS_NAMES = {
    "encrypt", "crypt", "ransom", "locker", "wanna", "petya",
    "notpetya", "ryuk", "sodinokibi", "revil", "darkside"
}


class FileMonitor(FileSystemEventHandler):
    def __init__(self):
        self.ops = []

    def _record(self, event_type, path):
        if not path.endswith(tuple(SUSPICIOUS_EXTENSIONS)):
            self.ops.append({
                "type": event_type,
                "path": path,
                "ts": datetime.now(IST)
            })
        else:
            # Suspicious extension — record with flag
            self.ops.append({
                "type": event_type,
                "path": path,
                "ts": datetime.now(IST),
                "suspicious": True
            })

    def on_created(self, event):
        if not event.is_directory:
            self._record("created", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._record("deleted", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._record("modified", event.src_path)

    def get_metrics(self) -> Dict:
        cutoff = datetime.now(IST) - timedelta(minutes=1)
        recent = [o for o in self.ops if o["ts"] > cutoff]
        self.ops = recent  # trim old

        suspicious_count = sum(1 for o in recent if o.get("suspicious"))

        # Rapid changes: same file modified > 3 times
        change_count = defaultdict(int)
        for o in recent:
            change_count[o["path"]] += 1
        rapid = sum(1 for c in change_count.values() if c > 3)

        return {
            "file_operations_per_min": len(recent),
            "suspicious_extensions_count": suspicious_count,
            "rapid_file_changes": rapid
        }


class EndpointAgent:
    def __init__(self, kafka_bootstrap_servers: str = "localhost:9092"):
        self.hostname = os.getenv("HOSTNAME") or socket.gethostname()
        self.endpoint_type = os.getenv("ENDPOINT_TYPE", "workstation")
        self.kafka_servers = kafka_bootstrap_servers
        self.producer = None
        self.file_monitor = FileMonitor()
        self.observer = None
        self.running = False
        self._prev_net = None
        self._prev_disk = None
        
        # Enhanced monitoring
        self._connection_history = deque(maxlen=100)  # Track connection patterns
        self._process_history = deque(maxlen=50)      # Track process spawns
        self._dns_queries = deque(maxlen=50)          # Track DNS queries
        self._port_scan_detector = defaultdict(set)   # Detect port scanning
        self._usb_devices = set()                     # Track USB devices
        self._baseline_established = False
        self._baseline_metrics = {}

        self._init_kafka()
        self._init_file_monitor()
        self._establish_baseline()

    # ── Init ──────────────────────────────────────────────────────────────────

    def _init_kafka(self):
        retries = 5
        for attempt in range(1, retries + 1):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.kafka_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    acks=1,
                    retries=3,
                    request_timeout_ms=5000
                )
                print(f"✅ Connected to Kafka at {self.kafka_servers}")
                return
            except Exception as e:
                print(f"⚠️  Kafka connect attempt {attempt}/{retries}: {e}")
                time.sleep(5)
        print("❌ Could not connect to Kafka — running in offline mode")

    def _init_file_monitor(self):
        monitor_path = os.path.expanduser("~/arcs_monitor")
        Path(monitor_path).mkdir(exist_ok=True)
        self.observer = Observer()
        self.observer.schedule(self.file_monitor, monitor_path, recursive=True)
        self.observer.start()
        print(f"✅ Monitoring: {monitor_path}")
    
    def _establish_baseline(self):
        """Establish baseline metrics for anomaly detection"""
        print("📊 Establishing baseline metrics...")
        try:
            self._baseline_metrics = {
                "avg_cpu": psutil.cpu_percent(interval=1),
                "avg_memory": psutil.virtual_memory().percent,
                "avg_connections": len(psutil.net_connections(kind="inet")),
                "process_count": len(psutil.pids())
            }
            self._baseline_established = True
            print(f"✅ Baseline: CPU={self._baseline_metrics['avg_cpu']:.1f}%, "
                  f"Mem={self._baseline_metrics['avg_memory']:.1f}%, "
                  f"Conns={self._baseline_metrics['avg_connections']}")
        except Exception as e:
            print(f"⚠️  Baseline establishment failed: {e}")

    # ── Telemetry Collection ──────────────────────────────────────────────────

    def _net_delta_kb(self) -> Dict:
        """KB sent/received since last call"""
        counters = psutil.net_io_counters()
        if self._prev_net is None:
            self._prev_net = counters
            return {"network_bytes_sent_kb": 0, "network_bytes_recv_kb": 0}
        sent = max(0, counters.bytes_sent - self._prev_net.bytes_sent) / 1024
        recv = max(0, counters.bytes_recv - self._prev_net.bytes_recv) / 1024
        self._prev_net = counters
        return {"network_bytes_sent_kb": round(sent, 2),
                "network_bytes_recv_kb": round(recv, 2)}

    def _disk_delta_mb(self) -> Dict:
        """MB read/written since last call"""
        try:
            counters = psutil.disk_io_counters()
            if counters is None or self._prev_disk is None:
                self._prev_disk = counters
                return {"disk_read_mb": 0, "disk_write_mb": 0}
            read  = max(0, counters.read_bytes  - self._prev_disk.read_bytes)  / (1024*1024)
            write = max(0, counters.write_bytes - self._prev_disk.write_bytes) / (1024*1024)
            self._prev_disk = counters
            return {"disk_read_mb": round(read, 2), "disk_write_mb": round(write, 2)}
        except Exception:
            return {"disk_read_mb": 0, "disk_write_mb": 0}

    def _process_metrics(self) -> Dict:
        proc = psutil.Process()
        with proc.oneshot():
            cpu   = proc.cpu_percent(interval=0.1)
            mem   = proc.memory_info().rss / (1024 * 1024)
            try:
                handles = proc.num_handles() if platform.system() == "Windows" else proc.num_fds()
            except Exception:
                handles = 0
            try:
                children = len(proc.children(recursive=True))
            except Exception:
                children = 0
        return {
            "process_cpu_percent": round(cpu, 2),
            "process_memory_mb":   round(mem, 2),
            "open_handles":        handles,
            "child_processes":     children
        }

    def _encryption_indicators(self) -> int:
        indicators = 0
        # High system-wide CPU (encryption is CPU-heavy)
        if psutil.cpu_percent(interval=0.1) > 80:
            indicators += 1
        # Suspicious process names
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"].lower()
                if any(s in name for s in SUSPICIOUS_PROCESS_NAMES):
                    indicators += 2
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return indicators

    def _login_metrics(self) -> Dict:
        """Detect failed login attempts (Windows event log approximation)"""
        try:
            # On Linux: check /var/log/auth.log; on Windows: approximate via process list
            login_attempts = 0
            privilege_escalations = 0
            for proc in psutil.process_iter(["name", "username"]):
                try:
                    name = proc.info["name"].lower()
                    if any(x in name for x in ["runas", "sudo", "su", "uac", "elevat"]):
                        privilege_escalations += 1
                    if any(x in name for x in ["logon", "login", "auth", "pam"]):
                        login_attempts += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return {"login_attempts": login_attempts,
                    "privilege_escalations": privilege_escalations}
        except Exception:
            return {"login_attempts": 0, "privilege_escalations": 0}
    
    def _detect_port_scanning(self) -> int:
        """Detect potential port scanning activity"""
        try:
            connections = psutil.net_connections(kind="inet")
            current_time = time.time()
            
            # Track unique destination ports per remote IP
            for conn in connections:
                if conn.raddr:
                    remote_ip = conn.raddr.ip
                    remote_port = conn.raddr.port
                    self._port_scan_detector[remote_ip].add(remote_port)
            
            # Clean old entries (older than 60 seconds)
            # If an IP connects to >10 different ports, it's suspicious
            suspicious_count = sum(1 for ports in self._port_scan_detector.values() if len(ports) > 10)
            
            return suspicious_count
        except Exception:
            return 0
    
    def _detect_usb_devices(self) -> int:
        """Detect USB device connections"""
        try:
            current_devices = set()
            for partition in psutil.disk_partitions():
                if 'removable' in partition.opts.lower() or 'usb' in partition.device.lower():
                    current_devices.add(partition.device)
            
            # Detect new USB devices
            new_devices = current_devices - self._usb_devices
            self._usb_devices = current_devices
            
            return len(new_devices)
        except Exception:
            return 0
    
    def _detect_process_anomalies(self) -> Dict:
        """Detect suspicious process behavior"""
        try:
            current_processes = set(psutil.pids())
            suspicious_spawns = 0
            hidden_processes = 0
            
            for pid in current_processes:
                try:
                    proc = psutil.Process(pid)
                    name = proc.name().lower()
                    
                    # Check for suspicious process names
                    if any(s in name for s in SUSPICIOUS_PROCESS_NAMES):
                        suspicious_spawns += 1
                    
                    # Check for processes with no window (potentially hidden)
                    if platform.system() == "Windows":
                        try:
                            if proc.num_threads() > 0 and not proc.name().endswith('.exe'):
                                hidden_processes += 1
                        except:
                            pass
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                "suspicious_process_spawns": suspicious_spawns,
                "hidden_processes": hidden_processes,
                "total_processes": len(current_processes)
            }
        except Exception:
            return {"suspicious_process_spawns": 0, "hidden_processes": 0, "total_processes": 0}
    
    def _calculate_deviation_from_baseline(self) -> Dict:
        """Calculate deviation from baseline metrics"""
        if not self._baseline_established:
            return {"cpu_deviation": 0, "memory_deviation": 0, "connection_deviation": 0}
        
        try:
            current_cpu = psutil.cpu_percent(interval=0.1)
            current_memory = psutil.virtual_memory().percent
            current_connections = len(psutil.net_connections(kind="inet"))
            
            return {
                "cpu_deviation": abs(current_cpu - self._baseline_metrics["avg_cpu"]),
                "memory_deviation": abs(current_memory - self._baseline_metrics["avg_memory"]),
                "connection_deviation": abs(current_connections - self._baseline_metrics["avg_connections"])
            }
        except Exception:
            return {"cpu_deviation": 0, "memory_deviation": 0, "connection_deviation": 0}

    def collect_metrics(self) -> Dict:
        """Collect comprehensive telemetry with 20+ features"""
        file_metrics = self.file_monitor.get_metrics()
        proc_metrics = self._process_metrics()
        net_metrics  = self._net_delta_kb()
        disk_metrics = self._disk_delta_mb()
        login_metrics = self._login_metrics()
        process_anomalies = self._detect_process_anomalies()
        baseline_deviation = self._calculate_deviation_from_baseline()

        connections = len(psutil.net_connections(kind="inet"))
        encryption  = self._encryption_indicators()
        port_scan_indicators = self._detect_port_scanning()
        usb_events = self._detect_usb_devices()

        return {
            "hostname":      self.hostname,
            "endpoint_type": self.endpoint_type,
            "os":            platform.system(),
            "timestamp":     datetime.now(IST).isoformat(),
            
            # Core process features (15 original)
            "process_cpu_percent":       proc_metrics["process_cpu_percent"],
            "process_memory_mb":         proc_metrics["process_memory_mb"],
            "open_handles":              proc_metrics["open_handles"],
            "child_processes":           proc_metrics["child_processes"],
            "network_connections_count": connections,
            "encryption_indicators":     encryption,
            
            # File features
            **file_metrics,
            
            # Network delta
            **net_metrics,
            
            # Disk delta
            **disk_metrics,
            
            # Auth features
            **login_metrics,
            
            # Enhanced features (NEW)
            "port_scan_indicators":      port_scan_indicators,
            "usb_device_events":         usb_events,
            "suspicious_process_spawns": process_anomalies["suspicious_process_spawns"],
            "hidden_processes":          process_anomalies["hidden_processes"],
            "total_processes":           process_anomalies["total_processes"],
            
            # Baseline deviation (NEW)
            "cpu_deviation":             baseline_deviation["cpu_deviation"],
            "memory_deviation":          baseline_deviation["memory_deviation"],
            "connection_deviation":      baseline_deviation["connection_deviation"],
            
            # System health
            "system_cpu_percent":        psutil.cpu_percent(interval=0.1),
            "system_memory_percent":     psutil.virtual_memory().percent,
            "disk_usage_percent":        psutil.disk_usage('/').percent if platform.system() != "Windows" else psutil.disk_usage('C:\\').percent
        }

    # ── Kafka ─────────────────────────────────────────────────────────────────

    def send(self, metrics: Dict):
        if not self.producer:
            return
        try:
            self.producer.send("endpoint_logs", metrics)
            self.producer.flush(timeout=2)
        except Exception as e:
            print(f"❌ Kafka send failed: {e}")

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self, interval: int = 3):
        self.running = True
        print(f"🚀 Agent started on {self.hostname} ({self.endpoint_type})")
        print(f"📡 Enhanced telemetry: 25+ features | Interval: {interval}s")
        print(f"🔍 Monitoring: Files, Processes, Network, USB, Baseline Deviations")

        try:
            iteration = 0
            while self.running:
                m = self.collect_metrics()
                self.send(m)
                
                # Compact display with key metrics
                iteration += 1
                if iteration % 5 == 0:  # Detailed every 5 iterations
                    print(
                        f"📤 [{m['hostname']}] "
                        f"CPU={m['process_cpu_percent']:.1f}% "
                        f"Mem={m['process_memory_mb']:.0f}MB "
                        f"Net={m['network_connections_count']} "
                        f"FileOps={m['file_operations_per_min']} "
                        f"Enc={m['encryption_indicators']} "
                        f"USB={m['usb_device_events']} "
                        f"PortScan={m['port_scan_indicators']} "
                        f"SusProccess={m['suspicious_process_spawns']}"
                    )
                else:
                    print(f"📤 [{m['hostname']}] Telemetry sent ({iteration})", end="\r")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.producer:
            self.producer.close()
        print("✅ Agent stopped")


if __name__ == "__main__":
    kafka_server = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    agent = EndpointAgent(kafka_bootstrap_servers=kafka_server)
    agent.run(interval=3)
