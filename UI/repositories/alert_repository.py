"""
Alert data repository for database operations
"""
from typing import List, Optional, Dict, Any, Tuple
import uuid
from datetime import datetime, timedelta
from database import db_manager
from models.alert import Alert

class AlertRepository:
    """Repository for alert database operations"""
    
    @staticmethod
    def get_all_alerts(limit: int = 100) -> List[Alert]:
        """Get all alerts from database"""
        query = """
            SELECT 
                alert_id,
                alert_type,
                global_track_id,
                camera_id,
                timestamp,
                severity,
                status,
                description,
                assigned_to,
                resolution_notes,
                related_events,
                created_at,
                resolved_at
            FROM alerts
            ORDER BY timestamp DESC
            LIMIT %s
        """
        
        results = db_manager.execute_query(query, (limit,))
        alerts = []
        
        for row in results:
            row_dict = dict(row)
            alerts.append(Alert.from_dict(row_dict))
        
        return alerts
    
    @staticmethod
    def get_active_alerts(limit: int = 50) -> List[Alert]:
        """Get active alerts (not resolved/dismissed)"""
        query = """
            SELECT 
                alert_id,
                alert_type,
                global_track_id,
                camera_id,
                timestamp,
                severity,
                status,
                description,
                assigned_to,
                resolution_notes,
                related_events,
                created_at,
                resolved_at
            FROM alerts
            WHERE status NOT IN ('resolved', 'dismissed', 'closed')
            ORDER BY 
                CASE severity
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                    ELSE 5
                END,
                timestamp DESC
            LIMIT %s
        """
        
        results = db_manager.execute_query(query, (limit,))
        alerts = []
        
        for row in results:
            row_dict = dict(row)
            alerts.append(Alert.from_dict(row_dict))
        
        return alerts
    
    @staticmethod
    def get_alert_by_id(alert_id: int) -> Optional[Alert]:
        """Get a specific alert by ID"""
        query = """
            SELECT 
                alert_id,
                alert_type,
                global_track_id,
                camera_id,
                timestamp,
                severity,
                status,
                description,
                assigned_to,
                resolution_notes,
                related_events,
                created_at,
                resolved_at
            FROM alerts
            WHERE alert_id = %s
        """
        
        results = db_manager.execute_query(query, (alert_id,))
        
        if results:
            row_dict = dict(results[0])
            return Alert.from_dict(row_dict)
        
        return None
    
    @staticmethod
    def get_alerts_by_severity(severity: str) -> List[Alert]:
        """Get alerts filtered by severity"""
        query = """
            SELECT 
                alert_id,
                alert_type,
                global_track_id,
                camera_id,
                timestamp,
                severity,
                status,
                description,
                assigned_to,
                resolution_notes,
                related_events,
                created_at,
                resolved_at
            FROM alerts
            WHERE severity = %s
            ORDER BY timestamp DESC
        """
        
        results = db_manager.execute_query(query, (severity,))
        alerts = []
        
        for row in results:
            row_dict = dict(row)
            alerts.append(Alert.from_dict(row_dict))
        
        return alerts
    
    @staticmethod
    def get_alerts_by_type(alert_type: str) -> List[Alert]:
        """Get alerts filtered by type"""
        query = """
            SELECT 
                alert_id,
                alert_type,
                global_track_id,
                camera_id,
                timestamp,
                severity,
                status,
                description,
                assigned_to,
                resolution_notes,
                related_events,
                created_at,
                resolved_at
            FROM alerts
            WHERE alert_type = %s
            ORDER BY timestamp DESC
        """
        
        results = db_manager.execute_query(query, (alert_type,))
        alerts = []
        
        for row in results:
            row_dict = dict(row)
            alerts.append(Alert.from_dict(row_dict))
        
        return alerts
    
    @staticmethod
    def get_alerts_by_status(status: str) -> List[Alert]:
        """Get alerts filtered by status"""
        query = """
            SELECT 
                alert_id,
                alert_type,
                global_track_id,
                camera_id,
                timestamp,
                severity,
                status,
                description,
                assigned_to,
                resolution_notes,
                related_events,
                created_at,
                resolved_at
            FROM alerts
            WHERE status = %s
            ORDER BY timestamp DESC
        """
        
        results = db_manager.execute_query(query, (status,))
        alerts = []
        
        for row in results:
            row_dict = dict(row)
            alerts.append(Alert.from_dict(row_dict))
        
        return alerts
    
    @staticmethod
    def get_alerts_by_camera(camera_id: str) -> List[Alert]:
        """Get alerts filtered by camera"""
        query = """
            SELECT 
                alert_id,
                alert_type,
                global_track_id,
                camera_id,
                timestamp,
                severity,
                status,
                description,
                assigned_to,
                resolution_notes,
                related_events,
                created_at,
                resolved_at
            FROM alerts
            WHERE camera_id = %s
            ORDER BY timestamp DESC
        """
        
        results = db_manager.execute_query(query, (camera_id,))
        alerts = []
        
        for row in results:
            row_dict = dict(row)
            alerts.append(Alert.from_dict(row_dict))
        
        return alerts
    
    @staticmethod
    def get_recent_alerts(hours: int = 24) -> List[Alert]:
        """Get alerts from the last N hours"""
        query = """
            SELECT 
                alert_id,
                alert_type,
                global_track_id,
                camera_id,
                timestamp,
                severity,
                status,
                description,
                assigned_to,
                resolution_notes,
                related_events,
                created_at,
                resolved_at
            FROM alerts
            WHERE timestamp >= NOW() - INTERVAL '%s hours'
            ORDER BY timestamp DESC
        """
        
        results = db_manager.execute_query(query, (hours,))
        alerts = []
        
        for row in results:
            row_dict = dict(row)
            alerts.append(Alert.from_dict(row_dict))
        
        return alerts
    
    @staticmethod
    def get_alert_statistics() -> Dict[str, Any]:
        """Get alert statistics"""
        query = """
            SELECT 
                COUNT(*) as total_alerts,
                COUNT(CASE WHEN status NOT IN ('resolved', 'dismissed', 'closed') THEN 1 END) as active_alerts,
                COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_alerts,
                COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_alerts,
                COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_alerts,
                COUNT(CASE WHEN severity = 'low' THEN 1 END) as low_alerts,
                COUNT(DISTINCT alert_type) as alert_types,
                COUNT(DISTINCT camera_id) as cameras_with_alerts
            FROM alerts
            WHERE timestamp >= NOW() - INTERVAL '24 hours'
        """
        
        results = db_manager.execute_query(query)
        if results and len(results) > 0:
            return dict(results[0])
        return {
            'total_alerts': 0,
            'active_alerts': 0,
            'critical_alerts': 0,
            'high_alerts': 0,
            'medium_alerts': 0,
            'low_alerts': 0,
            'alert_types': 0,
            'cameras_with_alerts': 0
        }
    
    @staticmethod
    def get_alert_counts_by_type() -> List[Dict[str, Any]]:
        """Get alert counts grouped by type"""
        query = """
            SELECT 
                alert_type,
                COUNT(*) as count,
                COUNT(CASE WHEN status NOT IN ('resolved', 'dismissed', 'closed') THEN 1 END) as active_count
            FROM alerts
            WHERE timestamp >= NOW() - INTERVAL '24 hours'
            GROUP BY alert_type
            ORDER BY count DESC
        """
        
        results = db_manager.execute_query(query)
        return [dict(row) for row in results]
    
    @staticmethod
    def update_alert_status(alert_id: int, status: str, assigned_to: Optional[str] = None) -> bool:
        """Update alert status"""
        if assigned_to:
            query = """
                UPDATE alerts 
                SET status = %s, assigned_to = %s, updated_at = CURRENT_TIMESTAMP
                WHERE alert_id = %s
            """
            return db_manager.execute_update(query, (status, assigned_to, alert_id))
        else:
            query = """
                UPDATE alerts 
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE alert_id = %s
            """
            return db_manager.execute_update(query, (status, alert_id))
    
    @staticmethod
    def resolve_alert(alert_id: int, resolution_notes: str) -> bool:
        """Resolve an alert"""
        query = """
            UPDATE alerts 
            SET status = 'resolved', 
                resolution_notes = %s,
                resolved_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE alert_id = %s
        """
        return db_manager.execute_update(query, (resolution_notes, alert_id))
    
    @staticmethod
    def assign_alert(alert_id: int, assigned_to: str) -> bool:
        """Assign an alert to a user"""
        query = """
            UPDATE alerts 
            SET assigned_to = %s, 
                status = 'in_progress',
                updated_at = CURRENT_TIMESTAMP
            WHERE alert_id = %s
        """
        return db_manager.execute_update(query, (assigned_to, alert_id))
    
    @staticmethod
    def create_alert(alert_data: Dict[str, Any]) -> Optional[Alert]:
        """Create a new alert"""
        query = """
            INSERT INTO alerts (
                alert_type, global_track_id, camera_id, timestamp,
                severity, status, description, assigned_to,
                related_events
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """
        
        try:
            results = db_manager.execute_query(
                query,
                (
                    alert_data.get('alert_type'),
                    str(alert_data.get('global_track_id')) if alert_data.get('global_track_id') else None,
                    alert_data.get('camera_id'),
                    alert_data.get('timestamp', datetime.now()),
                    alert_data.get('severity', 'medium'),
                    alert_data.get('status', 'new'),
                    alert_data.get('description'),
                    alert_data.get('assigned_to'),
                    alert_data.get('related_events')
                )
            )
            
            if results:
                row_dict = dict(results[0])
                return Alert.from_dict(row_dict)
        except Exception as e:
            print(f"Error creating alert: {e}")
        
        return None