import json
import asyncio
from kafka import KafkaConsumer
from typing import Dict, Any
from config import config
from services.database import DatabaseService
from ml_engine.detector import AnomalyDetector
from services.risk_scorer import RiskScorer
from services.response_engine import ResponseEngine
from services.email_alerts import EmailAlertService
from services.sms_alerts import SMSAlertService
from services.settings_manager import settings_manager

class KafkaConsumerService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.detector = AnomalyDetector()
        self.risk_scorer = RiskScorer()
        self.response_engine = ResponseEngine(db_service)
        
        # Initialize alert services with settings manager
        self.email_service = EmailAlertService(settings_manager)
        self.sms_service = SMSAlertService(settings_manager)
        
        self.running = False
        self.consumer = None
    
    async def start(self):
        """Start consuming messages from Kafka"""
        self.running = True
        
        # Wait for Kafka to be ready
        await asyncio.sleep(5)
        
        try:
            loop = asyncio.get_running_loop()
            self.consumer = await loop.run_in_executor(None, self._create_consumer)
            
            print(f"✅ Kafka consumer connected to {config.KAFKA_BOOTSTRAP_SERVERS}")
            
            # Process messages
            await self._consume_messages()
            
        except Exception as e:
            print(f"❌ Kafka consumer error: {e}")
            await asyncio.sleep(5)
            if self.running:
                await self.start()

    def _create_consumer(self):
        """Create Kafka consumer off the main event loop so API requests stay responsive."""
        return KafkaConsumer(
            config.KAFKA_TOPICS["endpoint_logs"],
            config.KAFKA_TOPICS["network_logs"],
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='arcs-backend-group',
            request_timeout_ms=15000,
            session_timeout_ms=10000,
            api_version_auto_timeout_ms=3000,
            consumer_timeout_ms=1000
        )
    
    async def _consume_messages(self):
        """Process incoming messages"""
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Get messages with timeout
                messages = await loop.run_in_executor(
                    None,
                    lambda: self.consumer.poll(timeout_ms=1000)
                )
                
                for topic_partition, records in messages.items():
                    for record in records:
                        await self._process_message(record.value)
                
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                await asyncio.sleep(1)
    
    async def _process_message(self, message: Dict[str, Any]):
        """Process a single message through the detection pipeline"""
        try:
            # Store log
            self.db_service.insert_log(message)
            
            # Extract features
            features = self._extract_features(message)
            
            # Detect anomaly
            is_anomaly, anomaly_score = self.detector.predict(features)
            
            if is_anomaly:
                # Calculate risk score
                risk_level, risk_score = self.risk_scorer.calculate_risk(
                    message, anomaly_score
                )
                
                # Store risk score
                self.db_service.insert_risk_score({
                    "hostname": message.get("hostname"),
                    "risk_level": risk_level,
                    "risk_score": risk_score,
                    "anomaly_score": anomaly_score,
                    "features": features
                })
                
                # Create alert
                alert = {
                    "hostname": message.get("hostname"),
                    "endpoint": message.get("hostname"),  # Add endpoint field for email
                    "attack_type": self._determine_attack_type(message),  # Determine attack type
                    "risk_level": risk_level,
                    "risk_score": float(risk_score),  # Ensure it's a float
                    "anomaly_score": float(anomaly_score),  # Ensure it's a float
                    "message": f"Suspicious activity detected on {message.get('hostname')}",
                    "details": {
                        "file_operations_per_min": int(message.get("file_operations_per_min", 0)),
                        "process_cpu_percent": float(message.get("process_cpu_percent", 0)),
                        "process_memory_mb": float(message.get("process_memory_mb", 0)),
                        "network_connections_count": int(message.get("network_connections_count", 0)),
                        "suspicious_extensions_count": int(message.get("suspicious_extensions_count", 0)),
                        "rapid_file_changes": int(message.get("rapid_file_changes", 0)),
                        "encryption_indicators": int(message.get("encryption_indicators", 0))
                    }
                }
                self.db_service.insert_alert(alert)
                
                print(f"🚨 ALERT: {risk_level} risk on {message.get('hostname')} (score: {risk_score:.2f})")
                
                # Send email for critical alerts
                if risk_level in ["HIGH", "CRITICAL"] or risk_score >= 0.85:
                    email_sent = self.email_service.send_critical_alert(alert)
                    if email_sent:
                        print(f"📧 Critical alert email sent for {message.get('hostname')}")
                
                # Send SMS for ultra-critical alerts (risk >= 0.90)
                if risk_score >= 0.90 or (risk_level == "CRITICAL" and "ransomware" in alert.get("attack_type", "").lower()):
                    sms_sent = self.sms_service.send_critical_sms(alert)
                    if sms_sent:
                        print(f"📱 Ultra-critical SMS alert sent for {message.get('hostname')}")
                
                # Execute response if high risk
                if risk_level == "HIGH" and config.HIGH_RISK_AUTO_RESPONSE:
                    await self.response_engine.execute_containment(
                        message.get("hostname"),
                        risk_level,
                        message
                    )
        
        except Exception as e:
            print(f"❌ Error in message processing: {e}")
    
    def _extract_features(self, message: Dict[str, Any]) -> Dict[str, float]:
        """Extract all 15 ML features from message"""
        return {
            "file_operations_per_min":   message.get("file_operations_per_min", 0),
            "process_cpu_percent":        message.get("process_cpu_percent", 0),
            "process_memory_mb":          message.get("process_memory_mb", 0),
            "network_connections_count":  message.get("network_connections_count", 0),
            "suspicious_extensions_count":message.get("suspicious_extensions_count", 0),
            "rapid_file_changes":         message.get("rapid_file_changes", 0),
            "encryption_indicators":      message.get("encryption_indicators", 0),
            "disk_read_mb":               message.get("disk_read_mb", 0),
            "disk_write_mb":              message.get("disk_write_mb", 0),
            "open_handles":               message.get("open_handles", 0),
            "child_processes":            message.get("child_processes", 0),
            "network_bytes_sent_kb":      message.get("network_bytes_sent_kb", 0),
            "network_bytes_recv_kb":      message.get("network_bytes_recv_kb", 0),
            "login_attempts":             message.get("login_attempts", 0),
            "privilege_escalations":      message.get("privilege_escalations", 0),
        }
    
    def _determine_attack_type(self, message: Dict[str, Any]) -> str:
        """Determine the type of attack based on indicators"""
        encryption_indicators = message.get("encryption_indicators", 0)
        rapid_file_changes = message.get("rapid_file_changes", 0)
        suspicious_extensions = message.get("suspicious_extensions_count", 0)
        file_ops = message.get("file_operations_per_min", 0)
        network_connections = message.get("network_connections_count", 0)
        
        # Ransomware indicators
        if encryption_indicators > 0 or suspicious_extensions > 5:
            return "Ransomware Encryption"
        
        # Mass file operations
        if rapid_file_changes > 50 or file_ops > 100:
            return "Mass File Modification"
        
        # Lateral movement
        if network_connections > 20:
            return "Lateral Movement"
        
        # Default
        return "Suspicious Activity"
    
    async def stop(self):
        """Stop the consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        print("✅ Kafka consumer stopped")
