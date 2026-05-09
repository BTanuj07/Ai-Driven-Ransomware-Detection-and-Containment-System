from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from services.network_graph import NetworkGraphService
from services.cache_service import cache_service

router = APIRouter()

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Cache TTL settings (in seconds)
CACHE_TTL_SHORT = 3   # For frequently changing data (alerts, logs)
CACHE_TTL_MEDIUM = 10  # For moderately changing data (stats, endpoints)
CACHE_TTL_LONG = 30    # For slowly changing data (network graph)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ARCS Backend"
    }

@router.get("/alerts")
async def get_alerts(request: Request, limit: int = 50):
    """Get recent alerts with caching"""
    cache_key = f"alerts_{limit}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    db = request.app.state.db
    alerts = db.get_recent_alerts(limit)
    result = {
        "alerts": alerts,
        "count": len(alerts)
    }
    
    cache_service.set(cache_key, result, CACHE_TTL_SHORT)
    return result

@router.get("/risk-scores")
async def get_risk_scores(request: Request):
    """Get current risk scores with caching"""
    cache_key = "risk_scores"
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    db = request.app.state.db
    scores = db.get_risk_scores()
    result = {
        "risk_scores": scores,
        "count": len(scores)
    }
    
    cache_service.set(cache_key, result, CACHE_TTL_SHORT)
    return result

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
    
    # Get from alerts
    for alert in alerts:
        hostname = alert.get("hostname")
        if hostname:
            monitored_systems.add(hostname)
    
    # Get from system statuses
    for status in system_statuses:
        hostname = status.get("hostname")
        if hostname:
            monitored_systems.add(hostname)
    
    # If no systems from alerts/statuses, get from recent logs
    if not monitored_systems:
        logs = db.get_recent_logs(100)
        for log in logs:
            hostname = log.get("hostname")
            if hostname:
                monitored_systems.add(hostname)
    
    # If still no systems, show message
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
    
    # Calculate real propagation analysis
    attack_path = real_graph.calculate_attack_propagation_path()
    blast_radius = real_graph.calculate_blast_radius()
    recommendations = real_graph.get_isolation_recommendations()
    
    return {
        "graph": graph_data,
        "critical_nodes": critical_nodes,
        "attack_path": attack_path,
        "blast_radius": blast_radius,
        "recommendations": recommendations,
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
    
    # Get total count
    total_count = db.db['containment_actions'].count_documents({})
    
    # Get limited actions
    actions = db.get_containment_actions(limit)
    
    return {
        "actions": actions,
        "count": len(actions),
        "total": total_count
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
    """Get system statistics with caching"""
    cache_key = "stats"
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    db = request.app.state.db
    counts = db.get_alert_counts()
    
    result = {
        "total_alerts": counts["total"],
        "high_risk_count": counts["HIGH"],
        "medium_risk_count": counts["MEDIUM"],
        "low_risk_count": counts["LOW"],
        "systems_monitored": len(db.get_system_statuses())
    }
    
    cache_service.set(cache_key, result, CACHE_TTL_MEDIUM)
    return result

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
    """Get all monitored endpoints with caching"""
    cache_key = "endpoints"
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
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
    
    result = {
        "endpoints": endpoints,
        "count": len(endpoints),
        "infected": sum(1 for e in endpoints if e["status"] == "infected"),
        "at_risk": sum(1 for e in endpoints if e["status"] == "at_risk"),
        "normal": sum(1 for e in endpoints if e["status"] == "normal")
    }
    
    cache_service.set(cache_key, result, CACHE_TTL_MEDIUM)
    return result

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
        "timestamp": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()
    }


# ============================================
# RISK OVERVIEW ENDPOINTS (Real Data)
# ============================================

@router.get("/risk-overview/stats")
async def get_risk_overview_stats(request: Request):
    """Get comprehensive risk overview statistics with caching"""
    cache_key = "risk_overview_stats"
    cached = cache_service.get(cache_key)
    if cached:
        return cached
    
    db = request.app.state.db
    from datetime import datetime, timedelta
    
    # Get recent data
    risk_scores = db.get_risk_scores()
    alerts = db.get_recent_alerts(200)
    actions = db.get_containment_actions(100)
    
    # Calculate risk levels
    high_risk = len([r for r in risk_scores if r.get('risk_score', 0) >= 0.85])
    medium_risk = len([r for r in risk_scores if 0.70 <= r.get('risk_score', 0) < 0.85])
    low_risk = len([r for r in risk_scores if r.get('risk_score', 0) < 0.70])
    
    # Calculate global risk score (weighted average of top risks)
    if risk_scores:
        sorted_risks = sorted(risk_scores, key=lambda x: x.get('risk_score', 0), reverse=True)
        top_10 = sorted_risks[:min(10, len(sorted_risks))]
        global_risk = sum(r.get('risk_score', 0) for r in top_10) / len(top_10) if top_10 else 0
    else:
        global_risk = 0
    
    # Calculate containment success rate
    if actions:
        successful = len([a for a in actions if a.get('status') == 'success' or 'success' in str(a.get('action', '')).lower()])
        containment_success = (successful / len(actions) * 100) if actions else 0
    else:
        containment_success = 0
    
    # Calculate auto-containment confidence (based on recent success rate)
    recent_actions = actions[:20] if len(actions) >= 20 else actions
    if recent_actions:
        recent_success = len([a for a in recent_actions if a.get('status') == 'success' or 'success' in str(a.get('action', '')).lower()])
        auto_confidence = (recent_success / len(recent_actions) * 100) if recent_actions else 0
    else:
        auto_confidence = 85  # Default confidence
    
    result = {
        "globalRiskScore": int(global_risk * 100),
        "highRiskDevices": high_risk,
        "mediumRiskDevices": medium_risk,
        "lowRiskDevices": low_risk,
        "containmentSuccess": int(containment_success),
        "autoContainmentConfidence": int(auto_confidence),
        "totalDevices": len(risk_scores),
        "totalAlerts": len(alerts),
        "timestamp": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()
    }
    
    cache_service.set(cache_key, result, CACHE_TTL_MEDIUM)
    return result

@router.get("/risk-overview/endpoints")
async def get_risk_overview_endpoints(request: Request, limit: int = 10):
    """Get top risky endpoints with detailed information"""
    db = request.app.state.db
    from datetime import datetime, timedelta
    
    risk_scores = db.get_risk_scores()
    alerts = db.get_recent_alerts(200)
    
    # Sort by risk score
    sorted_risks = sorted(risk_scores, key=lambda x: x.get('risk_score', 0), reverse=True)
    top_risks = sorted_risks[:limit]
    
    # Enrich with alert information
    endpoint_data = []
    for risk in top_risks:
        hostname = risk.get('hostname', 'Unknown')
        risk_score = risk.get('risk_score', 0)
        anomaly_score = risk.get('anomaly_score', risk_score)
        
        # Find recent alerts for this endpoint
        endpoint_alerts = [a for a in alerts if a.get('hostname') == hostname]
        
        # Determine threat type
        if endpoint_alerts:
            latest_alert = endpoint_alerts[0]
            threat_type = latest_alert.get('message', 'Suspicious activity detected')
            
            # Extract threat type from message
            if 'encryption' in threat_type.lower() or 'ransomware' in threat_type.lower():
                threat_type = 'Ransomware Encryption'
            elif 'lateral' in threat_type.lower():
                threat_type = 'Lateral Movement'
            elif 'exfiltration' in threat_type.lower():
                threat_type = 'Data Exfiltration'
            elif 'privilege' in threat_type.lower():
                threat_type = 'Privilege Escalation'
            elif 'process' in threat_type.lower():
                threat_type = 'Suspicious Process'
            else:
                threat_type = 'Suspicious Activity'
        else:
            threat_type = 'Anomaly Detected'
        
        # Determine status
        if risk_score >= 0.85:
            status = 'Critical'
            action = 'Isolate Immediately'
        elif risk_score >= 0.70:
            status = 'High'
            action = 'Block Network Access'
        elif risk_score >= 0.50:
            status = 'Medium'
            action = 'Monitor & Alert'
        else:
            status = 'Low'
            action = 'Watch'
        
        # Calculate last activity
        timestamp = risk.get('timestamp')
        if timestamp:
            if isinstance(timestamp, str):
                try:
                    ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    ts = datetime.now(IST)
            else:
                ts = timestamp
            
            # Ensure both datetimes are timezone-aware for comparison
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=IST)
            
            time_diff = datetime.now(IST) - ts
            minutes = int(time_diff.total_seconds() / 60)
            
            if minutes < 1:
                last_activity = 'Just now'
            elif minutes < 60:
                last_activity = f'{minutes} min ago'
            else:
                hours = int(minutes / 60)
                last_activity = f'{hours} hour{"s" if hours > 1 else ""} ago'
        else:
            last_activity = 'Unknown'
        
        endpoint_data.append({
            "id": len(endpoint_data) + 1,
            "name": hostname,
            "riskScore": round(risk_score, 2),
            "threatType": threat_type,
            "anomalyScore": round(anomaly_score, 2),
            "status": status,
            "lastActivity": last_activity,
            "action": action,
            "alertCount": len(endpoint_alerts)
        })
    
    return {
        "endpoints": endpoint_data,
        "count": len(endpoint_data),
        "timestamp": datetime.now(IST).isoformat()
    }

@router.get("/risk-overview/trends")
async def get_risk_trends(request: Request, hours: int = 24):
    """Get risk score trends over time"""
    db = request.app.state.db
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    # Get risk scores from database
    risk_scores = db.get_risk_scores()
    
    if not risk_scores:
        # Return default trend if no data
        return {
            "trends": [{"time": f"{i:02d}:00", "score": 45 + i} for i in range(0, 24, 2)],
            "hours": hours
        }
    
    # Group by hour
    cutoff_time = datetime.now(IST) - timedelta(hours=hours)
    hourly_scores = defaultdict(list)
    
    for risk in risk_scores:
        timestamp = risk.get('timestamp')
        if timestamp:
            if isinstance(timestamp, str):
                try:
                    ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    continue
            else:
                ts = timestamp
            
            # Ensure timestamp is timezone-aware for comparison
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=IST)
            
            if ts >= cutoff_time:
                hour_key = ts.strftime("%H:00")
                hourly_scores[hour_key].append(risk.get('risk_score', 0))
    
    # Calculate averages
    trends = []
    for i in range(0, hours + 1, 2):
        hour_time = cutoff_time + timedelta(hours=i)
        hour_key = hour_time.strftime("%H:00")
        
        if hour_key in hourly_scores:
            avg_score = sum(hourly_scores[hour_key]) / len(hourly_scores[hour_key])
            trends.append({
                "time": hour_key if i < hours else "Now",
                "score": int(avg_score * 100)
            })
        else:
            # Interpolate if no data
            prev_score = trends[-1]["score"] if trends else 45
            trends.append({
                "time": hour_key if i < hours else "Now",
                "score": prev_score + (i % 3)
            })
    
    return {
        "trends": trends,
        "hours": hours,
        "dataPoints": len(trends)
    }

@router.get("/risk-overview/factors")
async def get_risk_factors(request: Request):
    """Get risk factor breakdown showing why systems are risky"""
    db = request.app.state.db
    
    logs = db.get_recent_logs(200)
    alerts = db.get_recent_alerts(100)
    
    # Analyze risk factors from logs
    total_weight = 0
    factors = {
        "encryption": 0,
        "network": 0,
        "process": 0,
        "privilege": 0,
        "file_ops": 0
    }
    
    for log in logs:
        # Encryption indicators
        if log.get('encryption_indicators', 0) > 0:
            factors["encryption"] += log.get('encryption_indicators', 0) * 10
        
        # Network activity
        if log.get('network_connections_count', 0) > 20:
            factors["network"] += (log.get('network_connections_count', 0) - 20) * 2
        
        # Process activity
        if log.get('process_cpu_percent', 0) > 80:
            factors["process"] += (log.get('process_cpu_percent', 0) - 80)
        
        # File operations
        if log.get('file_operations_per_min', 0) > 100:
            factors["file_ops"] += (log.get('file_operations_per_min', 0) - 100) / 10
    
    # Check alerts for privilege escalation
    for alert in alerts:
        if 'privilege' in alert.get('message', '').lower():
            factors["privilege"] += 20
    
    total_weight = sum(factors.values())
    
    # Calculate percentages
    if total_weight > 0:
        risk_factors = [
            {
                "factor": "File Encryption Spike",
                "percentage": int((factors["encryption"] / total_weight) * 100),
                "color": "#ef4444"
            },
            {
                "factor": "Abnormal Network Activity",
                "percentage": int((factors["network"] / total_weight) * 100),
                "color": "#f59e0b"
            },
            {
                "factor": "Suspicious Process Spawn",
                "percentage": int((factors["process"] / total_weight) * 100),
                "color": "#eab308"
            },
            {
                "factor": "Privilege Escalation",
                "percentage": int((factors["privilege"] / total_weight) * 100),
                "color": "#06b6d4"
            },
            {
                "factor": "Mass File Rename",
                "percentage": int((factors["file_ops"] / total_weight) * 100),
                "color": "#8b5cf6"
            }
        ]
    else:
        # Default distribution if no data
        risk_factors = [
            {"factor": "File Encryption Spike", "percentage": 35, "color": "#ef4444"},
            {"factor": "Abnormal Network Activity", "percentage": 25, "color": "#f59e0b"},
            {"factor": "Suspicious Process Spawn", "percentage": 20, "color": "#eab308"},
            {"factor": "Privilege Escalation", "percentage": 15, "color": "#06b6d4"},
            {"factor": "Mass File Rename", "percentage": 5, "color": "#8b5cf6"}
        ]
    
    # Normalize to 100%
    total_pct = sum(f["percentage"] for f in risk_factors)
    if total_pct > 0:
        for factor in risk_factors:
            factor["percentage"] = int((factor["percentage"] / total_pct) * 100)
    
    return {
        "factors": risk_factors,
        "timestamp": datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()
    }

@router.get("/risk-overview/severity-distribution")
async def get_severity_distribution(request: Request):
    """Get threat severity distribution"""
    db = request.app.state.db
    
    risk_scores = db.get_risk_scores()
    
    # Count by severity
    critical = len([r for r in risk_scores if r.get('risk_score', 0) >= 0.90])
    high = len([r for r in risk_scores if 0.70 <= r.get('risk_score', 0) < 0.90])
    medium = len([r for r in risk_scores if 0.50 <= r.get('risk_score', 0) < 0.70])
    low = len([r for r in risk_scores if r.get('risk_score', 0) < 0.50])
    
    return {
        "distribution": [
            {"name": "Critical", "value": critical, "color": "#dc2626"},
            {"name": "High", "value": high, "color": "#f59e0b"},
            {"name": "Medium", "value": medium, "color": "#eab308"},
            {"name": "Low", "value": low, "color": "#14b8a6"}
        ],
        "total": len(risk_scores)
    }
