"""
Configuration file for S3S System
"""

# Application Settings
APP_TITLE = "Surveillance & Security System"
APP_VERSION = "1.0.0"
DEFAULT_WINDOW_WIDTH = 1920
DEFAULT_WINDOW_HEIGHT = 1080
MINIMUM_WINDOW_WIDTH = 1280
MINIMUM_WINDOW_HEIGHT = 720

# Camera Settings
DEFAULT_CAMERA_GRID_COLS = 2
DEFAULT_CAMERA_GRID_ROWS = 2
DEFAULT_STREAM_QUALITY = "1080p"
DEFAULT_STREAM_FPS = 30
DEFAULT_STREAM_BITRATE = 5000  # Kbps

# AI Model Settings
PPE_DETECTION_CONFIDENCE = 85  # Percentage
FACE_RECOGNITION_CONFIDENCE = 90  # Percentage
PERSON_DETECTION_CONFIDENCE = 75  # Percentage

# Data Retention
VIDEO_RETENTION_DAYS = 30
ARCHIVE_AFTER_DAYS = 90
AUTO_DELETE_AFTER_DAYS = 365

# Database Settings
DB_TYPE = "sqlite"  # or "postgresql", "mysql"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "s3s_system"
DB_USER = "s3s_admin"
DB_PASSWORD = ""

# API Settings
API_HOST = "localhost"
API_PORT = 8000
API_TIMEOUT = 30  # seconds
API_PROTOCOL = "http"  # or "https"

# RTSP Stream Settings
RTSP_TIMEOUT = 10  # seconds
RTSP_RETRIES = 3
RTSP_PROTOCOL = "rtsp"  # or "rtsps" for SSL

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "logs/s3s.log"
LOG_MAX_SIZE = 10485760  # 10 MB
LOG_BACKUP_COUNT = 5

# Email Integration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True
SENDER_EMAIL = "alerts@company.com"
SENDER_PASSWORD = ""
ALERT_RECIPIENTS = ["supervisor@company.com", "admin@company.com"]

# Webhook Integration
WEBHOOK_ENABLED = False
WEBHOOK_URL = "https://api.example.com/alerts"
WEBHOOK_TIMEOUT = 10  # seconds
WEBHOOK_RETRY_COUNT = 3

# UI Theme
THEME = "dark"  # or "light"
PRIMARY_COLOR = "#1e3a5f"
SECONDARY_COLOR = "#2a5a8f"
ACCENT_COLOR = "#ff6b6b"
SUCCESS_COLOR = "#51cf66"
WARNING_COLOR = "#ffd93d"
DANGER_COLOR = "#ff6b6b"

# Privacy & Compliance
ENABLE_GDPR_MODE = True
ENABLE_FACE_BLUR = False
ENABLE_ENCRYPTION = True
ENABLE_AUDIT_LOGGING = True

# Advanced Settings
ENABLE_DEBUG_MODE = False
ENABLE_PERFORMANCE_MONITORING = False
CACHE_SIZE_MB = 512
MAX_CONCURRENT_STREAMS = 16
CONNECTION_POOL_SIZE = 20

# Notification Settings
ENABLE_EMAIL_ALERTS = True
ENABLE_DESKTOP_NOTIFICATIONS = True
ENABLE_SOUND_ALERTS = True
ALERT_RETRY_INTERVAL = 300  # seconds

# System Limits
MAX_UPLOAD_FILE_SIZE = 104857600  # 100 MB
MAX_EXPORT_ROWS = 100000
MAX_SEARCH_RESULTS = 10000
API_RATE_LIMIT = 1000  # Requests per hour

# Default Time Zones
DEFAULT_TIMEZONE = "UTC"
DISPLAY_24_HOUR = True

# Feature Flags
FEATURE_FACIAL_RECOGNITION = True
FEATURE_PPE_DETECTION = True
FEATURE_INTRUSION_DETECTION = True
FEATURE_LICENSE_PLATE_RECOGNITION = False  # Not implemented
FEATURE_CROWD_MONITORING = True
FEATURE_HEATMAPS = True
FEATURE_ADVANCED_ANALYTICS = True

# Integration Endpoints
CAMERA_MANAGEMENT_API = "http://localhost:8001"
ML_SERVICE_API = "http://localhost:8002"
STORAGE_API = "http://localhost:8003"
AUTH_SERVICE_API = "http://localhost:8004"
NOTIFICATION_SERVICE_API = "http://localhost:8005"
