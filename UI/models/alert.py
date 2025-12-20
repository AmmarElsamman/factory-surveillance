"""
Alert data model
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

@dataclass
class Alert:
    """Alert entity model"""
    alert_id: int
    alert_type: str
    global_track_id: Optional[uuid.UUID] = None
    camera_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    severity: str = "medium"
    status: str = "new"
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    related_events: Optional[List[int]] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Create Alert instance from dictionary"""
        # Handle UUID conversion
        global_track_id = data.get('global_track_id')
        if isinstance(global_track_id, str):
            global_track_id = uuid.UUID(global_track_id)
        
        # Handle related_events if it's a string
        related_events = data.get('related_events')
        if isinstance(related_events, str):
            try:
                # PostgreSQL returns arrays as strings like '{1,2,3}'
                if related_events.startswith('{') and related_events.endswith('}'):
                    related_events = [int(x) for x in related_events[1:-1].split(',') if x.strip()]
                else:
                    related_events = []
            except:
                related_events = []
        
        return cls(
            alert_id=data.get('alert_id'),
            alert_type=data.get('alert_type'),
            global_track_id=global_track_id,
            camera_id=data.get('camera_id'),
            timestamp=data.get('timestamp'),
            severity=data.get('severity', 'medium'),
            status=data.get('status', 'new'),
            description=data.get('description'),
            assigned_to=data.get('assigned_to'),
            resolution_notes=data.get('resolution_notes'),
            related_events=related_events,
            created_at=data.get('created_at'),
            resolved_at=data.get('resolved_at')
        )
    
    def get_severity_emoji(self) -> str:
        """Get emoji for severity level"""
        severity_map = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵',
            'info': 'ℹ️'
        }
        return severity_map.get(self.severity.lower(), '⚪')
    
    def get_status_icon(self) -> str:
        """Get icon for status"""
        status_map = {
            'new': '🆕',
            'acknowledged': '👁️',
            'in_progress': '🔄',
            'resolved': '✅',
            'dismissed': '❌',
            'escalated': '📈'
        }
        return status_map.get(self.status.lower(), '❓')
    
    def get_alert_type_icon(self) -> str:
        """Get icon for alert type"""
        type_map = {
            'ppe_violation': '👷',
            'intruder_detected': '🚨',
            'unknown_face': '👤',
            'blacklist_match': '🚫',
            'camera_offline': '📹',
            'safety_violation': '⚠️',
            'unauthorized_area': '🚧',
            'suspicious_behavior': '👀'
        }
        return type_map.get(self.alert_type.lower(), '📋')
    
    def is_active(self) -> bool:
        """Check if alert is still active (not resolved/dismissed)"""
        return self.status.lower() not in ['resolved', 'dismissed', 'closed']
    
    def get_time_ago(self) -> str:
        """Get human-readable time ago string"""
        if not self.timestamp:
            return "Unknown time"
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        if self.timestamp.tzinfo is None:
            # If timestamp is naive, assume UTC
            alert_time = self.timestamp.replace(tzinfo=timezone.utc)
        else:
            alert_time = self.timestamp
        
        diff = now - alert_time
        
        if diff.days > 0:
            if diff.days == 1:
                return "1 day ago"
            return f"{diff.days} days ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            if hours == 1:
                return "1 hour ago"
            return f"{hours} hours ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            if minutes == 1:
                return "1 minute ago"
            return f"{minutes} minutes ago"
        else:
            return "Just now"