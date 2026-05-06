"""
Settings Manager - Real-time settings for detection and response
"""

from typing import Dict, Any
from threading import Lock

class SettingsManager:
    """
    Singleton settings manager that provides real-time access to system settings.
    Used by detector, risk scorer, and response engine.
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._settings = self._get_default_settings()
        self._db = None
    
    def set_database(self, db):
        """Set database service for loading settings"""
        self._db = db
        self.reload()
    
    def reload(self):
        """Reload settings from database"""
        if self._db:
            try:
                db_settings = self._db.get_settings()
                # Merge with defaults to ensure all keys exist
                self._settings.update(db_settings)
                print("✅ Settings reloaded from database")
            except Exception as e:
                print(f"⚠️ Failed to reload settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value"""
        return self._settings.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self._settings.copy()
    
    def update(self, settings: Dict[str, Any]):
        """Update settings in memory and database"""
        self._settings.update(settings)
        if self._db:
            self._db.update_settings(settings)
    
    # Convenience methods for common settings
    
    @property
    def anomaly_threshold(self) -> float:
        """Get anomaly detection threshold"""
        return self._settings.get('anomalyThreshold', -0.5)
    
    @property
    def high_risk_threshold(self) -> float:
        """Get HIGH risk classification threshold"""
        return self._settings.get('highRiskThreshold', 0.8)
    
    @property
    def medium_risk_threshold(self) -> float:
        """Get MEDIUM risk classification threshold"""
        return self._settings.get('mediumRiskThreshold', 0.6)
    
    @property
    def low_risk_threshold(self) -> float:
        """Get LOW risk classification threshold"""
        return self._settings.get('lowRiskThreshold', 0.4)
    
    @property
    def false_positive_sensitivity(self) -> float:
        """Get false positive sensitivity"""
        return self._settings.get('falsePositiveSensitivity', 0.65)
    
    @property
    def model_confidence(self) -> float:
        """Get minimum model confidence threshold"""
        return self._settings.get('modelConfidence', 0.85)
    
    @property
    def auto_isolate(self) -> bool:
        """Check if auto-isolation is enabled"""
        return self._settings.get('autoIsolate', True)
    
    @property
    def auto_kill_process(self) -> bool:
        """Check if auto-kill process is enabled"""
        return self._settings.get('autoKillProcess', True)
    
    @property
    def auto_disable_user(self) -> bool:
        """Check if auto-disable user is enabled"""
        return self._settings.get('autoDisableUser', False)
    
    @property
    def require_approval(self) -> bool:
        """Check if admin approval is required"""
        return self._settings.get('requireApproval', True)
    
    @property
    def email_alerts(self) -> bool:
        """Check if email alerts are enabled"""
        return self._settings.get('emailAlerts', True)
    
    @property
    def sms_alerts(self) -> bool:
        """Check if SMS alerts are enabled"""
        return self._settings.get('smsAlerts', False)
    
    @property
    def critical_escalation(self) -> bool:
        """Check if critical escalation is enabled"""
        return self._settings.get('criticalEscalation', True)
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
        return {
            'anomalyThreshold': -0.5,
            'highRiskThreshold': 0.8,
            'mediumRiskThreshold': 0.6,
            'lowRiskThreshold': 0.4,
            'falsePositiveSensitivity': 0.65,
            'modelConfidence': 0.85,
            'autoIsolate': True,
            'autoKillProcess': True,
            'autoDisableUser': False,
            'requireApproval': True,
            'emailAlerts': True,
            'smsAlerts': False,
            'criticalEscalation': True,
            'emailAddress': 'admin@arcs.local',
            'phoneNumber': '+1 (555) 123-4567'
        }


# Global singleton instance
settings_manager = SettingsManager()
