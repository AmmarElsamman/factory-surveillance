"""
Domain enumerations
"""
from enum import Enum

class TrackStatus(str, Enum):
    ACTIVE = "active"
    LOST = "lost"
    CLOSED = "closed"

class HelmetStatus(str, Enum):
    COMPLIANT = "compliant"
    VIOLATION = "violation"
    UNKNOWN = "unknown"

class AlertType(str, Enum):
    HELMET_VIOLATION = "helmet_violation"
    INTRUDER = "intruder"
    RESTRICTED_ZONE = "restricted_zone"
    LOITERING = "loitering"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class WorkerStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"

class CameraStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class MatchConfidenceLevel(str, Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NO_MATCH = "no_match"