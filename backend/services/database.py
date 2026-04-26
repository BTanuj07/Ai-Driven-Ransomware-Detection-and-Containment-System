from pymongo import MongoClient, DESCENDING
from datetime import datetime
from bson import ObjectId
from typing import List, Dict, Any, Optional
from config import config

class DatabaseService:
    def __init__(self):
        try:
            # Use MongoDB URL from config (which loads from .env)
            mongodb_url = config.MONGODB_URL
            print(f"🔗 Connecting to MongoDB...")
            
            self.client = MongoClient(mongodb_url, serverSelectionTimeoutMS=10000)
            # Test connection
            self.client.server_info()
            
            # Check if it's Atlas or local
            if "mongodb.net" in mongodb_url:
                print("✅ Connected to MongoDB Atlas (Cloud)")
            else:
                print("✅ Connected to MongoDB (Local)")
                
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("⚠️ Running without database - data will not be persisted")
            self.client = None
        
        if self.client:
            self.db = self.client[config.MONGODB_DB_NAME]
            
            # Collections
            self.logs = self.db.logs
            self.alerts = self.db.alerts
            self.risk_scores = self.db.risk_scores
            self.system_status = self.db.system_status
            self.containment_actions = self.db.containment_actions
            self.users = self.db.users
            self.settings = self.db.settings
            self.notifications = self.db.notifications
            self.reports = self.db.reports
            self.audit_logs = self.db.audit_logs
            
            self._create_indexes()
        else:
            # Create dummy collections that do nothing
            self.logs = None
            self.alerts = None
            self.risk_scores = None
            self.system_status = None
            self.containment_actions = None
            self.users = None
            self.settings = None
            self.notifications = None
            self.reports = None
            self.audit_logs = None
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        if not self.client:
            return
        try:
            self.logs.create_index([("timestamp", DESCENDING)])
            self.logs.create_index([("hostname", 1)])
            self.alerts.create_index([("timestamp", DESCENDING)])
            self.alerts.create_index([("risk_level", 1)])
            self.risk_scores.create_index([("hostname", 1)])
            self.system_status.create_index([("hostname", 1)])
        except Exception as e:
            print(f"⚠️ Failed to create indexes: {e}")
    
    def insert_log(self, log_data: Dict[str, Any]) -> str:
        """Insert a log entry"""
        if not self.client:
            return "no-db"
        try:
            log_data["timestamp"] = datetime.utcnow()
            result = self.logs.insert_one(log_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"⚠️ Failed to insert log: {e}")
            return "error"
    
    def insert_alert(self, alert_data: Dict[str, Any]) -> str:
        """Insert an alert"""
        if not self.client:
            print("⚠️ No database client - alert not saved")
            return "no-db"
        try:
            alert_data["timestamp"] = datetime.utcnow()
            result = self.alerts.insert_one(alert_data)
            print(f"✅ Alert saved to database: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"⚠️ Failed to insert alert: {e}")
            return "error"
    
    def insert_risk_score(self, risk_data: Dict[str, Any]) -> str:
        """Insert or update risk score"""
        if not self.client:
            return "no-db"
        try:
            risk_data["timestamp"] = datetime.utcnow()
            result = self.risk_scores.insert_one(risk_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"⚠️ Failed to insert risk score: {e}")
            return "error"
    
    def update_system_status(self, hostname: str, status_data: Dict[str, Any]):
        """Update system status"""
        if not self.client:
            return
        try:
            status_data["last_updated"] = datetime.utcnow()
            self.system_status.update_one(
                {"hostname": hostname},
                {"$set": status_data},
                upsert=True
            )
        except Exception as e:
            print(f"⚠️ Failed to update system status: {e}")
    
    def insert_containment_action(self, action_data: Dict[str, Any]) -> str:
        """Log containment action"""
        if not self.client:
            return "no-db"
        try:
            action_data["timestamp"] = datetime.utcnow()
            result = self.containment_actions.insert_one(action_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"⚠️ Failed to insert containment action: {e}")
            return "error"
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        if not self.client:
            return []
        try:
            alerts = self.alerts.find().sort("timestamp", DESCENDING).limit(limit)
            return [self._serialize_doc(alert) for alert in alerts]
        except Exception as e:
            print(f"⚠️ Failed to get alerts: {e}")
            return []
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs"""
        if not self.client:
            return []
        try:
            logs = self.logs.find().sort("timestamp", DESCENDING).limit(limit)
            return [self._serialize_doc(log) for log in logs]
        except Exception as e:
            print(f"⚠️ Failed to get logs: {e}")
            return []
    
    def get_risk_scores(self) -> List[Dict[str, Any]]:
        """Get current risk scores for all systems"""
        if not self.client:
            return []
        try:
            scores = self.risk_scores.find().sort("timestamp", DESCENDING)
            return [self._serialize_doc(score) for score in scores]
        except Exception as e:
            print(f"⚠️ Failed to get risk scores: {e}")
            return []
    
    def get_system_statuses(self) -> List[Dict[str, Any]]:
        """Get all system statuses"""
        if not self.client:
            return []
        try:
            statuses = self.system_status.find()
            return [self._serialize_doc(status) for status in statuses]
        except Exception as e:
            print(f"⚠️ Failed to get system statuses: {e}")
            return []
    
    def get_containment_actions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent containment actions"""
        if not self.client:
            return []
        try:
            actions = self.containment_actions.find().sort("timestamp", DESCENDING).limit(limit)
            return [self._serialize_doc(action) for action in actions]
        except Exception as e:
            print(f"⚠️ Failed to get containment actions: {e}")
            return []
    
    def update_alert_status(self, alert_id: str, status: str, updated_by: str = None) -> bool:
        """Update alert status (Monitoring/Under Review/Contained/Resolved)"""
        if not self.client:
            return False
        try:
            from bson import ObjectId
            update_data = {
                "status": status,
                "status_updated_at": datetime.utcnow()
            }
            if updated_by:
                update_data["updated_by"] = updated_by
            
            result = self.alerts.update_one(
                {"_id": ObjectId(alert_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"⚠️ Failed to update alert status: {e}")
            return False
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get single alert by ID with full details"""
        if not self.client:
            return None
        try:
            from bson import ObjectId
            alert = self.alerts.find_one({"_id": ObjectId(alert_id)})
            return self._serialize_doc(alert) if alert else None
        except Exception as e:
            print(f"⚠️ Failed to get alert: {e}")
            return None
    
    def get_alerts_filtered(self, severity: str = None, start_date: datetime = None, 
                           end_date: datetime = None, endpoint: str = None, 
                           status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get filtered alerts"""
        if not self.client:
            return []
        try:
            query = {}
            if severity:
                query["risk_level"] = severity
            if endpoint:
                query["hostname"] = endpoint
            if status:
                query["status"] = status
            if start_date or end_date:
                query["timestamp"] = {}
                if start_date:
                    query["timestamp"]["$gte"] = start_date
                if end_date:
                    query["timestamp"]["$lte"] = end_date
            
            alerts = self.alerts.find(query).sort("timestamp", DESCENDING).limit(limit)
            return [self._serialize_doc(alert) for alert in alerts]
        except Exception as e:
            print(f"⚠️ Failed to get filtered alerts: {e}")
            return []
    
    def insert_notification(self, notification_data: Dict[str, Any]) -> str:
        """Insert a notification"""
        if not self.client:
            return "no-db"
        try:
            notification_data["timestamp"] = datetime.utcnow()
            notification_data["read"] = False
            result = self.notifications.insert_one(notification_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"⚠️ Failed to insert notification: {e}")
            return "error"
    
    def get_notifications(self, user_id: str = None, unread_only: bool = False, 
                         limit: int = 50) -> List[Dict[str, Any]]:
        """Get notifications"""
        if not self.client:
            return []
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            if unread_only:
                query["read"] = False
            
            notifications = self.notifications.find(query).sort("timestamp", DESCENDING).limit(limit)
            return [self._serialize_doc(notif) for notif in notifications]
        except Exception as e:
            print(f"⚠️ Failed to get notifications: {e}")
            return []
    
    def mark_notification_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        if not self.client:
            return False
        try:
            from bson import ObjectId
            result = self.notifications.update_one(
                {"_id": ObjectId(notification_id)},
                {"$set": {"read": True, "read_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"⚠️ Failed to mark notification as read: {e}")
            return False
    
    def insert_audit_log(self, action: str, user: str, details: Dict[str, Any]) -> str:
        """Insert audit log entry"""
        if not self.client:
            return "no-db"
        try:
            log_data = {
                "action": action,
                "user": user,
                "details": details,
                "timestamp": datetime.utcnow()
            }
            result = self.audit_logs.insert_one(log_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"⚠️ Failed to insert audit log: {e}")
            return "error"
    
    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs"""
        if not self.client:
            return []
        try:
            logs = self.audit_logs.find().sort("timestamp", DESCENDING).limit(limit)
            return [self._serialize_doc(log) for log in logs]
        except Exception as e:
            print(f"⚠️ Failed to get audit logs: {e}")
            return []
    
    def save_report(self, report_data: Dict[str, Any]) -> str:
        """Save generated report"""
        if not self.client:
            return "no-db"
        try:
            report_data["generated_at"] = datetime.utcnow()
            result = self.reports.insert_one(report_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"⚠️ Failed to save report: {e}")
            return "error"
    
    def get_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get saved reports"""
        if not self.client:
            return []
        try:
            reports = self.reports.find().sort("generated_at", DESCENDING).limit(limit)
            return [self._serialize_doc(report) for report in reports]
        except Exception as e:
            print(f"⚠️ Failed to get reports: {e}")
            return []
    
    def get_settings(self) -> Dict[str, Any]:
        """Get system settings"""
        if not self.client:
            return self._get_default_settings()
        try:
            settings = self.settings.find_one({"type": "system"})
            return self._serialize_doc(settings) if settings else self._get_default_settings()
        except Exception as e:
            print(f"⚠️ Failed to get settings: {e}")
            return self._get_default_settings()
    
    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Update system settings"""
        if not self.client:
            return False
        try:
            settings_data["updated_at"] = datetime.utcnow()
            result = self.settings.update_one(
                {"type": "system"},
                {"$set": settings_data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"⚠️ Failed to update settings: {e}")
            return False
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default system settings"""
        return {
            "risk_threshold": {
                "high": 0.8,
                "medium": 0.6,
                "low": 0.3
            },
            "ml_sensitivity": 0.5,
            "auto_response_enabled": True,
            "alert_rules": {
                "file_ops_threshold": 100,
                "encryption_threshold": 1
            },
            "session_timeout": 480,  # 8 hours in minutes
            "password_policy": {
                "min_length": 8,
                "require_uppercase": True,
                "require_numbers": True,
                "require_special": False
            }
        }
    
    def _serialize_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to JSON-serializable dict"""
        if not doc:
            return doc
        
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = self._serialize_dict(value)
            elif hasattr(value, 'item'):  # numpy types
                result[key] = value.item()
            else:
                result[key] = value
        return result
    
    def _serialize_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively serialize nested dicts"""
        result = {}
        for key, value in d.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = self._serialize_dict(value)
            elif hasattr(value, 'item'):  # numpy types
                result[key] = value.item()
            else:
                result[key] = value
        return result
