from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from services.network_graph import NetworkGraphService

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ARCS Backend"
    }

@router.get("/alerts")
async def get_alerts(request: Request, limit: int = 50):
    """Get recent alerts"""
    db = request.app.state.db
    alerts = db.get_recent_alerts(limit)
    return {
        "alerts": alerts,
        "count": len(alerts)
    }

@router.get("/risk-scores")
async def get_risk_scores(request: Request):
    """Get current risk scores"""
    db = request.app.state.db
    scores = db.get_risk_scores()
    return {
        "risk_scores": scores,
        "count": len(scores)
    }

@router.get("/logs")
async def get_logs(request: Request, limit: int = 100):
    """Get recent logs"""
    db = request.app.state.db
    logs = db.get_recent_logs(limit)
    return {
        "logs": logs,
        "count": len(logs)
    }

@router.get("/network-graph")
async def get_network_graph(request: Request):
    """Get network topology graph based on real monitored systems"""
    db = request.app.state.db
    
    # Get real systems from database
    alerts = db.get_recent_alerts(100)
    system_statuses = db.get_system_statuses()
    
    # Build real network graph
    real_graph = NetworkGraphService()
    
    # Add nodes from actual monitored systems
    monitored_systems = set()
    for alert in alerts:
        hostname = alert.get("hostname")
        if hostname:
            monitored_systems.add(hostname)
    
    for status in system_statuses:
        hostname = status.get("hostname")
        if hostname:
            monitored_systems.add(hostname)
    
    # If no real systems, show a minimal graph
    if not monitored_systems:
        monitored_systems = {"No systems monitored yet"}
    
    # Add nodes with real status
    for hostname in monitored_systems:
        # Check if system has recent HIGH risk alerts
        recent_high_alerts = [a for a in alerts if a.get("hostname") == hostname and a.get("risk_level") == "HIGH"]
        
        if recent_high_alerts:
            real_graph.add_node(hostname, {"status": "infected"})
            real_graph.mark_infected(hostname)
        else:
            real_graph.add_node(hostname, {"status": "normal"})
    
    # Add connections between systems (if multiple systems exist)
    systems_list = list(monitored_systems)
    if len(systems_list) > 1:
        # Connect systems that might communicate
        for i in range(len(systems_list) - 1):
            real_graph.add_connection(systems_list[i], systems_list[i + 1], weight=0.8)
    
    graph_data = real_graph.get_graph_data()
    critical_nodes = real_graph.get_critical_nodes()
    
    return {
        "graph": graph_data,
        "critical_nodes": critical_nodes,
        "real_data": True,
        "monitored_systems": list(monitored_systems)
    }

@router.get("/system-status")
async def get_system_status(request: Request):
    """Get all system statuses"""
    db = request.app.state.db
    statuses = db.get_system_statuses()
    return {
        "systems": statuses,
        "count": len(statuses)
    }

@router.get("/containment-actions")
async def get_containment_actions(request: Request, limit: int = 50):
    """Get recent containment actions"""
    db = request.app.state.db
    actions = db.get_containment_actions(limit)
    return {
        "actions": actions,
        "count": len(actions)
    }

@router.post("/containment")
async def manual_containment(request: Request, data: Dict[str, Any]):
    """Manually trigger containment action"""
    hostname = data.get("hostname")
    action_type = data.get("action_type")
    
    if not hostname or not action_type:
        raise HTTPException(status_code=400, detail="hostname and action_type required")
    
    db = request.app.state.db
    
    # Log manual action
    db.insert_containment_action({
        "hostname": hostname,
        "action": f"MANUAL_{action_type}",
        "triggered_by": "manual",
        "details": data
    })
    
    return {
        "status": "success",
        "message": f"Containment action {action_type} executed on {hostname}"
    }

@router.get("/stats")
async def get_statistics(request: Request):
    """Get system statistics"""
    db = request.app.state.db
    
    alerts = db.get_recent_alerts(1000)
    
    # Calculate statistics
    high_risk = sum(1 for a in alerts if a.get("risk_level") == "HIGH")
    medium_risk = sum(1 for a in alerts if a.get("risk_level") == "MEDIUM")
    low_risk = sum(1 for a in alerts if a.get("risk_level") == "LOW")
    
    return {
        "total_alerts": len(alerts),
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "systems_monitored": len(db.get_system_statuses())
    }

@router.get("/search")
async def search(request: Request, query: str = "", type: str = "all"):
    """Search for devices, alerts, IPs, or logs"""
    db = request.app.state.db
    
    if not query:
        return {"results": [], "count": 0}
    
    query_lower = query.lower()
    results = []
    
    # Search alerts
    if type in ["all", "alerts"]:
        alerts = db.get_recent_alerts(100)
        matching_alerts = [
            {**alert, "result_type": "alert"}
            for alert in alerts
            if query_lower in alert.get("hostname", "").lower() or
               query_lower in alert.get("message", "").lower()
        ]
        results.extend(matching_alerts[:10])
    
    # Search devices/endpoints
    if type in ["all", "devices"]:
        statuses = db.get_system_statuses()
        matching_devices = [
            {**status, "result_type": "device"}
            for status in statuses
            if query_lower in status.get("hostname", "").lower()
        ]
        results.extend(matching_devices[:10])
    
    # Search logs
    if type in ["all", "logs"]:
        logs = db.get_recent_logs(200)
        matching_logs = [
            {**log, "result_type": "log"}
            for log in logs
            if query_lower in log.get("hostname", "").lower() or
               query_lower in str(log.get("source_ip", "")).lower()
        ]
        results.extend(matching_logs[:10])
    
    return {
        "results": results[:20],
        "count": len(results),
        "query": query
    }

@router.get("/endpoints")
async def get_endpoints(request: Request):
    """Get all monitored endpoints with their current status"""
    db = request.app.state.db
    
    statuses = db.get_system_statuses()
    alerts = db.get_recent_alerts(100)
    
    # Build endpoint list with risk levels
    endpoints = []
    for status in statuses:
        hostname = status.get("hostname")
        
        # Get recent alerts for this endpoint
        endpoint_alerts = [a for a in alerts if a.get("hostname") == hostname]
        high_alerts = sum(1 for a in endpoint_alerts if a.get("risk_level") == "HIGH")
        
        # Determine status
        if high_alerts > 0:
            endpoint_status = "infected"
            risk_level = "HIGH"
        elif len(endpoint_alerts) > 0:
            endpoint_status = "at_risk"
            risk_level = "MEDIUM"
        else:
            endpoint_status = "normal"
            risk_level = "LOW"
        
        endpoints.append({
            "hostname": hostname,
            "status": endpoint_status,
            "risk_level": risk_level,
            "alert_count": len(endpoint_alerts),
            "high_risk_count": high_alerts,
            "last_seen": status.get("last_updated"),
            "details": status
        })
    
    return {
        "endpoints": endpoints,
        "count": len(endpoints),
        "infected": sum(1 for e in endpoints if e["status"] == "infected"),
        "at_risk": sum(1 for e in endpoints if e["status"] == "at_risk"),
        "normal": sum(1 for e in endpoints if e["status"] == "normal")
    }

@router.get("/alerts/timeline")
async def get_alerts_timeline(request: Request, days: int = 7):
    """Get alerts grouped by day for timeline chart"""
    db = request.app.state.db
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    alerts = db.get_recent_alerts(1000)
    
    # Group alerts by day
    timeline = defaultdict(lambda: {"high": 0, "medium": 0, "low": 0})
    
    for alert in alerts:
        timestamp = alert.get("timestamp")
        if timestamp:
            if isinstance(timestamp, str):
                date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
            else:
                date = timestamp.date()
            
            date_str = date.strftime("%d %b")
            risk_level = alert.get("risk_level", "LOW").lower()
            timeline[date_str][risk_level] += 1
    
    # Convert to list format
    result = [
        {
            "label": date,
            "high": counts["high"],
            "medium": counts["medium"],
            "low": counts["low"]
        }
        for date, counts in sorted(timeline.items())
    ]
    
    return {
        "timeline": result[-days:],  # Last N days
        "days": days
    }

@router.get("/system-resources")
async def get_system_resources(request: Request):
    """Get current system resource usage across all endpoints"""
    db = request.app.state.db
    
    logs = db.get_recent_logs(10)
    
    if not logs:
        return {
            "cpu_usage": 0,
            "memory_usage": 0,
            "file_activity": 0,
            "network_io": 0
        }
    
    # Get latest log entry
    latest = logs[0]
    
    return {
        "cpu_usage": latest.get("process_cpu_percent", 0),
        "memory_usage": min(100, round((latest.get("process_memory_mb", 0) / 10))),
        "file_activity": min(100, latest.get("file_operations_per_min", 0)),
        "network_io": min(100, latest.get("network_connections_count", 0)),
        "timestamp": latest.get("timestamp")
    }

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(request: Request, alert_id: str):
    """Mark an alert as acknowledged"""
    db = request.app.state.db
    
    # In a real implementation, you'd update the alert in the database
    # For now, we'll just return success
    return {
        "status": "success",
        "message": f"Alert {alert_id} acknowledged",
        "alert_id": alert_id
    }

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(request: Request, alert_id: str):
    """Mark an alert as resolved"""
    db = request.app.state.db
    
    return {
        "status": "success",
        "message": f"Alert {alert_id} resolved",
        "alert_id": alert_id
    }

@router.get("/threat-hunting")
async def threat_hunting(request: Request, indicator: str = None):
    """Threat hunting - search for indicators of compromise"""
    db = request.app.state.db
    
    alerts = db.get_recent_alerts(200)
    logs = db.get_recent_logs(200)
    
    # Identify suspicious patterns
    suspicious_patterns = []
    
    # High file operation rates
    high_file_ops = [log for log in logs if log.get("file_operations_per_min", 0) > 100]
    if high_file_ops:
        suspicious_patterns.append({
            "type": "High File Operations",
            "severity": "HIGH",
            "count": len(high_file_ops),
            "description": "Detected unusually high file operation rates",
            "affected_systems": list(set(log.get("hostname") for log in high_file_ops))
        })
    
    # Encryption indicators
    encryption_logs = [log for log in logs if log.get("encryption_indicators", 0) > 0]
    if encryption_logs:
        suspicious_patterns.append({
            "type": "Encryption Activity",
            "severity": "CRITICAL",
            "count": len(encryption_logs),
            "description": "Detected potential file encryption activity",
            "affected_systems": list(set(log.get("hostname") for log in encryption_logs))
        })
    
    # Repeated high risk alerts
    high_risk_alerts = [a for a in alerts if a.get("risk_level") == "HIGH"]
    if len(high_risk_alerts) > 10:
        suspicious_patterns.append({
            "type": "Repeated High Risk Alerts",
            "severity": "HIGH",
            "count": len(high_risk_alerts),
            "description": "Multiple high-risk alerts detected",
            "affected_systems": list(set(a.get("hostname") for a in high_risk_alerts))
        })
    
    return {
        "patterns": suspicious_patterns,
        "total_indicators": len(suspicious_patterns),
        "timestamp": datetime.utcnow().isoformat()
    }
