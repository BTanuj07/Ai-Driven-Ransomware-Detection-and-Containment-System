import json
import asyncio
from kafka import KafkaConsumer
from typing import Dict, Any
from config import config
from services.database import DatabaseService
from ml_engine.detector import AnomalyDetector
from services.risk_scorer import RiskScorer
from services.response_engine import ResponseEngine

class KafkaConsumerService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.detector = AnomalyDetector()
        self.risk_scorer = RiskScorer()
        self.response_engine = ResponseEngine(db_service)
        self.running = False
        self.consumer = None
    
    async def start(self):
        """Start consuming messages from Kafka"""
        self.running = True
        
        # Wait for Kafka to be ready
        await asyncio.sleep(5)
        
        try:
            self.consumer = KafkaConsumer(
                config.KAFKA_TOPICS["endpoint_logs"],
                config.KAFKA_TOPICS["network_logs"],
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='arcs-backend-group'
            )
            
            print(f"✅ Kafka consumer connected to {config.KAFKA_BOOTSTRAP_SERVERS}")
            
            # Process messages
            await self._consume_messages()
            
        except Exception as e:
            print(f"❌ Kafka consumer error: {e}")
            await asyncio.sleep(5)
            if self.running:
                await self.start()
    
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
        """Extract ML features from message"""
        return {
            "file_operations_per_min": message.get("file_operations_per_min", 0),
            "process_cpu_percent": message.get("process_cpu_percent", 0),
            "process_memory_mb": message.get("process_memory_mb", 0),
            "network_connections_count": message.get("network_connections_count", 0),
            "suspicious_extensions_count": message.get("suspicious_extensions_count", 0),
            "rapid_file_changes": message.get("rapid_file_changes", 0),
            "encryption_indicators": message.get("encryption_indicators", 0)
        }
    
    async def stop(self):
        """Stop the consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        print("✅ Kafka consumer stopped")
