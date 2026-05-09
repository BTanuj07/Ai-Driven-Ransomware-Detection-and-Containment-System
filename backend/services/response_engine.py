from typing import Dict, Any, List
from datetime import datetime
from services.database import DatabaseService
from services.settings_manager import settings_manager

class ResponseEngine:
    """Automated Security Orchestration and Response (SOAR)"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
    
    async def execute_containment(
        self,
        hostname: str,
        risk_level: str,
        details: Dict[str, Any]
    ) -> List[str]:
        """
        Execute automated containment actions based on settings
        Returns list of actions taken
        """
        actions_taken = []
        
        # Check if approval is required
        if settings_manager.require_approval:
            print(f"⏸️ Containment for {hostname} requires admin approval")
            action = "PENDING_APPROVAL: Awaiting admin authorization"
            actions_taken.append(action)
            
            # Log the pending approval as a containment action
            self.db_service.insert_containment_action({
                "hostname": hostname,
                "risk_level": risk_level,
                "action": action,
                "details": details
            })
            
            return actions_taken
        
        print(f"🛡️ Executing containment for {hostname} (Risk: {risk_level})")
        
        if risk_level == "HIGH":
            # Action 1: Kill malicious process (if enabled)
            if settings_manager.auto_kill_process and "process_id" in details:
                action = self._kill_process(hostname, details["process_id"])
                actions_taken.append(action)
            
            # Action 2: Block suspicious IPs
            if "suspicious_ips" in details:
                for ip in details["suspicious_ips"]:
                    action = self._block_ip(hostname, ip)
                    actions_taken.append(action)
            
            # Action 3: Isolate machine (if enabled)
            if settings_manager.auto_isolate:
                action = self._isolate_machine(hostname)
                actions_taken.append(action)
            
            # Action 4: Disable user account (if enabled)
            if settings_manager.auto_disable_user and "username" in details:
                action = self._disable_user(hostname, details["username"])
                actions_taken.append(action)
        
        elif risk_level == "MEDIUM":
            # Less aggressive actions for medium risk
            if settings_manager.auto_kill_process and "process_id" in details:
                action = self._kill_process(hostname, details["process_id"])
                actions_taken.append(action)
        
        # Log all actions
        for action in actions_taken:
            self.db_service.insert_containment_action({
                "hostname": hostname,
                "risk_level": risk_level,
                "action": action,
                "details": details
            })
        
        # Update system status
        self.db_service.update_system_status(hostname, {
            "status": "contained" if risk_level == "HIGH" else "monitored",
            "risk_level": risk_level,
            "last_action": actions_taken[-1] if actions_taken else None
        })
        
        return actions_taken
    
    def _kill_process(self, hostname: str, process_id: int) -> str:
        """Simulate killing a malicious process"""
        action = f"KILL_PROCESS: Terminated process {process_id} on {hostname}"
        print(f"  ✓ {action}")
        return action
    
    def _block_ip(self, hostname: str, ip_address: str) -> str:
        """Simulate blocking an IP address"""
        action = f"BLOCK_IP: Blocked {ip_address} on {hostname}"
        print(f"  ✓ {action}")
        return action
    
    def _isolate_machine(self, hostname: str) -> str:
        """Simulate network isolation"""
        action = f"ISOLATE: Network isolation enabled for {hostname}"
        print(f"  ✓ {action}")
        return action
    
    def _disable_user(self, hostname: str, username: str) -> str:
        """Simulate disabling user account"""
        action = f"DISABLE_USER: Account {username} disabled on {hostname}"
        print(f"  ✓ {action}")
        return action
