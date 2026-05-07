"""
SMS Alert Service using Twilio
Sends SMS notifications for ultra-critical security threats
"""
import os
from datetime import datetime, timedelta
from typing import Dict
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

class SMSAlertService:
    def __init__(self, settings_manager=None):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_phone = os.getenv('TWILIO_PHONE_NUMBER')
        self.settings_manager = settings_manager
        
        try:
            self.client = Client(self.account_sid, self.auth_token) if self.account_sid and self.auth_token else None
            if self.client:
                logger.info("Twilio SMS service initialized")
            else:
                logger.warning("Twilio SMS service not configured - missing credentials")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            self.client = None
        
        # Track sent SMS to prevent duplicates
        self.sent_sms: Dict[str, datetime] = {}
        self.cooldown_period = timedelta(hours=2)  # 2-hour cooldown for SMS (longer than email)
        
        # Ultra-critical threshold (higher than email threshold)
        self.ultra_critical_threshold = 0.90  # Only send SMS for 90%+ risk
        self.ultra_critical_keywords = ['ransomware', 'encryption', 'mass_deletion']
    
    def _get_admin_phone(self) -> str:
        """Get admin phone from settings manager or fallback to env"""
        if self.settings_manager:
            phone = self.settings_manager.get('phoneNumber')
            if phone and phone != '+1 (555) 123-4567':
                return phone
        return os.getenv('ADMIN_PHONE_NUMBER', '+1 (555) 123-4567')
        
    def _is_ultra_critical(self, alert: Dict) -> bool:
        """
        Determine if alert is ultra-critical (requires SMS)
        More strict than email alerts
        """
        risk_score = alert.get('risk_score', 0)
        risk_level = alert.get('risk_level', '').lower()
        attack_type = alert.get('attack_type', '').lower()
        
        # Must have very high risk score
        if risk_score >= self.ultra_critical_threshold:
            return True
        
        # Or explicitly marked as critical with dangerous attack type
        if risk_level == 'critical' and any(keyword in attack_type for keyword in self.ultra_critical_keywords):
            return True
        
        return False
    
    def _generate_sms_key(self, alert: Dict) -> str:
        """Generate unique key for SMS tracking"""
        endpoint = alert.get('endpoint', 'unknown')
        attack_type = alert.get('attack_type', 'unknown')
        return f"{endpoint}:{attack_type}"
    
    def _should_send_sms(self, alert: Dict) -> bool:
        """Check if SMS should be sent"""
        if not self.client:
            logger.warning("Twilio client not initialized")
            return False
        
        # Check if ultra-critical
        if not self._is_ultra_critical(alert):
            logger.info(f"Alert not ultra-critical for SMS: {alert.get('attack_type')}")
            return False
        
        # Check for duplicate
        sms_key = self._generate_sms_key(alert)
        
        if sms_key in self.sent_sms:
            last_sent = self.sent_sms[sms_key]
            time_since_last = datetime.now() - last_sent
            
            if time_since_last < self.cooldown_period:
                logger.info(f"SMS already sent {time_since_last.seconds}s ago, skipping: {sms_key}")
                return False
        
        return True
    
    def _cleanup_old_sms(self):
        """Remove old SMS records from tracking"""
        cutoff_time = datetime.now() - self.cooldown_period
        self.sent_sms = {
            key: timestamp 
            for key, timestamp in self.sent_sms.items() 
            if timestamp > cutoff_time
        }
    
    def _format_sms_message(self, alert: Dict) -> str:
        """
        Format alert into SMS message (160 chars max for single SMS)
        """
        endpoint = alert.get('endpoint', 'Unknown')
        attack_type = alert.get('attack_type', 'Unknown')
        risk_score = alert.get('risk_score', 0)
        
        # Keep it short and urgent
        message = f"🚨 CRITICAL ALERT\n"
        message += f"Endpoint: {endpoint}\n"
        message += f"Threat: {attack_type}\n"
        message += f"Risk: {risk_score:.0%}\n"
        message += f"Action: Containment initiated\n"
        message += f"Check dashboard immediately"
        
        return message
    
    def send_critical_sms(self, alert: Dict) -> bool:
        """
        Send SMS for ultra-critical alert
        Returns True if SMS was sent, False otherwise
        """
        try:
            # Check if SMS should be sent
            if not self._should_send_sms(alert):
                return False
            
            # Get admin phone dynamically from settings
            admin_phone = self._get_admin_phone()
            
            # Cleanup old records
            self._cleanup_old_sms()
            
            # Format message
            message_body = self._format_sms_message(alert)
            
            # Send SMS
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_phone,
                to=admin_phone
            )
            
            if message.sid:
                # Mark SMS as sent
                sms_key = self._generate_sms_key(alert)
                self.sent_sms[sms_key] = datetime.now()
                
                logger.info(f"Critical SMS sent successfully: {sms_key} (SID: {message.sid})")
                return True
            else:
                logger.error("Failed to send SMS - no SID returned")
                return False
                
        except Exception as e:
            logger.error(f"Error sending critical SMS: {str(e)}")
            return False
    
    def send_test_sms(self, phone_number: str = None) -> bool:
        """
        Send test SMS to verify configuration
        """
        try:
            if not self.client:
                logger.error("Twilio client not initialized")
                return False
            
            # Use provided phone or get from settings
            target_phone = phone_number or self._get_admin_phone()
            
            message = self.client.messages.create(
                body="🔔 ARCS Test Alert\nThis is a test message from your ransomware detection system. SMS alerts are working correctly!",
                from_=self.from_phone,
                to=target_phone
            )
            
            logger.info(f"Test SMS sent successfully (SID: {message.sid})")
            return True
            
        except Exception as e:
            logger.error(f"Error sending test SMS: {str(e)}")
            return False


# Note: Create instances with settings_manager when needed
# Example: sms_service = SMSAlertService(settings_manager)
