"""
Email Alert Service using SendGrid
Sends email notifications only for critical alerts with deduplication
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Set
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging

logger = logging.getLogger(__name__)

class EmailAlertService:
    def __init__(self, settings_manager=None):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('ALERT_FROM_EMAIL', 'alerts@arcs-security.com')
        self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key) if self.api_key else None
        self.settings_manager = settings_manager
        
        # Track sent alerts to prevent duplicates
        self.sent_alerts: Dict[str, datetime] = {}
        self.cooldown_period = timedelta(hours=1)  # Don't resend same alert within 1 hour
        
        # Critical alert thresholds
        self.critical_threshold = 0.85  # Risk score threshold for email alerts
        self.critical_keywords = ['ransomware', 'encryption', 'mass_deletion', 'lateral_movement']
    
    def _get_admin_email(self) -> str:
        """Get admin email from settings manager or fallback to env"""
        if self.settings_manager:
            email = self.settings_manager.get('emailAddress')
            if email and email != 'admin@arcs.local':
                return email
        return os.getenv('ADMIN_EMAIL', 'admin@arcs.local')
        
    def _is_critical_alert(self, alert: Dict) -> bool:
        """
        Determine if alert is critical enough to send email
        """
        risk_score = alert.get('risk_score', 0)
        risk_level = alert.get('risk_level', '').lower()
        attack_type = alert.get('attack_type', '').lower()
        
        # Check if risk score is above critical threshold
        if risk_score >= self.critical_threshold:
            return True
        
        # Check if risk level is explicitly marked as critical
        if risk_level == 'critical':
            return True
        
        # Check for critical attack types
        if any(keyword in attack_type for keyword in self.critical_keywords):
            return True
        
        return False
    
    def _generate_alert_key(self, alert: Dict) -> str:
        """
        Generate unique key for alert to track duplicates
        """
        endpoint = alert.get('endpoint', 'unknown')
        attack_type = alert.get('attack_type', 'unknown')
        return f"{endpoint}:{attack_type}"
    
    def _should_send_email(self, alert: Dict) -> bool:
        """
        Check if email should be sent (critical + not duplicate)
        """
        # First check if alert is critical
        if not self._is_critical_alert(alert):
            logger.info(f"Alert not critical enough for email: {alert.get('attack_type')}")
            return False
        
        # Check for duplicate within cooldown period
        alert_key = self._generate_alert_key(alert)
        
        if alert_key in self.sent_alerts:
            last_sent = self.sent_alerts[alert_key]
            time_since_last = datetime.now() - last_sent
            
            if time_since_last < self.cooldown_period:
                logger.info(f"Alert already sent {time_since_last.seconds}s ago, skipping: {alert_key}")
                return False
        
        return True
    
    def _cleanup_old_alerts(self):
        """
        Remove old alerts from tracking to prevent memory buildup
        """
        cutoff_time = datetime.now() - self.cooldown_period
        self.sent_alerts = {
            key: timestamp 
            for key, timestamp in self.sent_alerts.items() 
            if timestamp > cutoff_time
        }
    
    def _format_email_content(self, alert: Dict) -> str:
        """
        Format alert data into HTML email content
        """
        endpoint = alert.get('endpoint', 'Unknown')
        attack_type = alert.get('attack_type', 'Unknown')
        risk_score = alert.get('risk_score', 0)
        risk_level = alert.get('risk_level', 'Unknown')
        timestamp = alert.get('timestamp', datetime.now().isoformat())
        details = alert.get('details', 'No additional details')
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ background-color: #ffffff; border-radius: 8px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 20px; border-radius: 8px 8px 0 0; margin: -30px -30px 20px -30px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .alert-badge {{ display: inline-block; padding: 8px 16px; background-color: #dc2626; color: white; border-radius: 4px; font-weight: bold; margin: 10px 0; }}
                .info-row {{ padding: 12px 0; border-bottom: 1px solid #e5e7eb; }}
                .info-label {{ font-weight: bold; color: #374151; display: inline-block; width: 140px; }}
                .info-value {{ color: #1f2937; }}
                .critical {{ color: #dc2626; font-weight: bold; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb; color: #6b7280; font-size: 12px; }}
                .action-button {{ display: inline-block; padding: 12px 24px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 CRITICAL SECURITY ALERT</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">ARCS - Autonomous Ransomware Containment System</p>
                </div>
                
                <div class="alert-badge">IMMEDIATE ACTION REQUIRED</div>
                
                <div class="info-row">
                    <span class="info-label">Endpoint:</span>
                    <span class="info-value critical">{endpoint}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Attack Type:</span>
                    <span class="info-value critical">{attack_type}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Risk Score:</span>
                    <span class="info-value critical">{risk_score:.2f}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Risk Level:</span>
                    <span class="info-value critical">{risk_level.upper()}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Detected At:</span>
                    <span class="info-value">{timestamp}</span>
                </div>
                
                <div class="info-row" style="border-bottom: none;">
                    <span class="info-label">Details:</span>
                    <span class="info-value">{details}</span>
                </div>
                
                <a href="http://localhost:3000" class="action-button">View Dashboard →</a>
                
                <div class="footer">
                    <p><strong>Automated Response:</strong> System has initiated containment protocols.</p>
                    <p>This is an automated alert from ARCS. Do not reply to this email.</p>
                    <p>To manage alert settings, log in to the ARCS dashboard.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def send_critical_alert(self, alert: Dict) -> bool:
        """
        Send email for critical alert if conditions are met
        Returns True if email was sent, False otherwise
        """
        try:
            # Check if email alerts are enabled in settings
            if self.settings_manager and not self.settings_manager.get('emailAlerts', True):
                logger.info("Email alerts disabled in settings, skipping email")
                return False
            
            # Get admin email dynamically from settings
            admin_email = self._get_admin_email()
            
            # Check if SendGrid is configured
            if not self.sg or not self.api_key or not admin_email:
                logger.warning("Email service not configured - missing credentials")
                return False
            
            # Check if email should be sent
            if not self._should_send_email(alert):
                return False
            
            # Cleanup old alerts periodically
            self._cleanup_old_alerts()
            
            # Prepare email
            subject = f"🚨 CRITICAL ALERT: {alert.get('attack_type', 'Security Threat')} on {alert.get('endpoint', 'Unknown')}"
            html_content = self._format_email_content(alert)
            
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(admin_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            # Send email
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                # Mark alert as sent
                alert_key = self._generate_alert_key(alert)
                self.sent_alerts[alert_key] = datetime.now()
                
                logger.info(f"Critical alert email sent successfully: {alert_key}")
                return True
            else:
                logger.error(f"Failed to send email. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending critical alert email: {str(e)}")
            return False
    
    def send_daily_summary(self, summary_data: Dict) -> bool:
        """
        Send daily summary email (optional feature)
        """
        try:
            # Get admin email dynamically from settings
            admin_email = self._get_admin_email()
            
            subject = f"ARCS Daily Security Summary - {datetime.now().strftime('%Y-%m-%d')}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Daily Security Summary</h2>
                <p><strong>Total Alerts:</strong> {summary_data.get('total_alerts', 0)}</p>
                <p><strong>Critical Alerts:</strong> {summary_data.get('critical_alerts', 0)}</p>
                <p><strong>Threats Contained:</strong> {summary_data.get('contained_threats', 0)}</p>
                <p><strong>Endpoints Monitored:</strong> {summary_data.get('total_endpoints', 0)}</p>
                <hr>
                <p style="color: #666; font-size: 12px;">ARCS - Autonomous Ransomware Containment System</p>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(admin_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.sg.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {str(e)}")
            return False


# Note: Create instances with settings_manager when needed
# Example: email_service = EmailAlertService(settings_manager)
