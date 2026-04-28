"""
Alerts view - Event queue and alert management
"""
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QCheckBox, QFrame, QListWidget,
                               QListWidgetItem, QScrollArea, QMessageBox, QInputDialog,
                               QMenu)
from PySide6.QtGui import QAction  
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor
from ui.utils.components import Card, EventItem
from ui.utils.styles import COLORS
import uuid

# Import alert repository
try:
    from repositories.alert_repository import AlertRepository
    from repositories.camera_repository import CameraRepository
    from models.alert import Alert
    DATABASE_ENABLED = True
except ImportError as e:
    print(f"Database import error: {e}")
    DATABASE_ENABLED = False


class AlertsWidget(QWidget):
    """Alert queue and event management"""
    
    # Signal to notify other components when alerts are updated
    alerts_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_selected_alert = None
        self.filters = {
            'severity': ['critical', 'high', 'medium', 'low', 'info'],
            'alert_type': 'all',
            'status': 'all',
            'camera': 'all'
        }
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Left panel - Alert filters
        left_panel = QFrame()
        left_panel.setFixedWidth(220)
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(12)
        
        filter_title = QLabel("Filters")
        filter_title_font = QFont()
        filter_title_font.setBold(True)
        filter_title_font.setPointSize(11)
        filter_title.setFont(filter_title_font)
        left_layout.addWidget(filter_title)
        
        # Severity filter
        left_layout.addWidget(QLabel("Severity:"))
        
        self.check_critical = QCheckBox("🔴 Critical")
        self.check_critical.setChecked(True)
        self.check_critical.stateChanged.connect(self.on_filter_changed)
        left_layout.addWidget(self.check_critical)
        
        self.check_high = QCheckBox("🟠 High")
        self.check_high.setChecked(True)
        self.check_high.stateChanged.connect(self.on_filter_changed)
        left_layout.addWidget(self.check_high)
        
        self.check_medium = QCheckBox("🟡 Medium")
        self.check_medium.setChecked(True)
        self.check_medium.stateChanged.connect(self.on_filter_changed)
        left_layout.addWidget(self.check_medium)
        
        self.check_low = QCheckBox("🔵 Low")
        self.check_low.setChecked(True)
        self.check_low.stateChanged.connect(self.on_filter_changed)
        left_layout.addWidget(self.check_low)
        
        self.check_info = QCheckBox("ℹ️ Info")
        self.check_info.stateChanged.connect(self.on_filter_changed)
        left_layout.addWidget(self.check_info)
        
        left_layout.addSpacing(12)
        
        # Alert type filter
        left_layout.addWidget(QLabel("Alert Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All", "PPE Violation", "Intruder", "Unknown Face", 
                                 "Blacklist", "Camera Offline", "Safety Violation", 
                                 "Unauthorized Area", "Suspicious Behavior"])
        self.type_combo.currentTextChanged.connect(self.on_filter_changed)
        left_layout.addWidget(self.type_combo)
        
        # Camera filter
        left_layout.addWidget(QLabel("Camera:"))
        self.camera_combo = QComboBox()
        self.camera_combo.addItem("All Cameras")
        self.camera_combo.currentTextChanged.connect(self.on_filter_changed)
        left_layout.addWidget(self.camera_combo)
        
        # Status filter
        left_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "New", "Acknowledged", "In Progress", "Resolved", "Dismissed"])
        self.status_combo.currentTextChanged.connect(self.on_filter_changed)
        left_layout.addWidget(self.status_combo)
        
        # Time filter
        left_layout.addWidget(QLabel("Time Range:"))
        self.time_combo = QComboBox()
        self.time_combo.addItems(["Last 24 hours", "Last 7 days", "Last 30 days", "All time"])
        self.time_combo.currentTextChanged.connect(self.on_filter_changed)
        left_layout.addWidget(self.time_combo)
        
        left_layout.addSpacing(16)
        
        btn_clear_filters = QPushButton("Clear Filters")
        btn_clear_filters.setMaximumWidth(150)
        btn_clear_filters.clicked.connect(self.clear_filters)
        left_layout.addWidget(btn_clear_filters)
        
        # Statistics
        left_layout.addSpacing(12)
        left_layout.addWidget(QLabel("Statistics:"))
        self.stats_label = QLabel("Loading...")
        self.stats_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt;")
        left_layout.addWidget(self.stats_label)
        
        left_layout.addStretch()
        
        main_layout.addWidget(left_panel)
        
        # Center panel - Alert list
        center_layout = QVBoxLayout()
        
        # Header with refresh button
        header_layout = QHBoxLayout()
        list_header = QLabel("Alert Queue")
        list_header_font = QFont()
        list_header_font.setPointSize(12)
        list_header_font.setBold(True)
        list_header.setFont(list_header_font)
        header_layout.addWidget(list_header)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_alerts)
        header_layout.addWidget(self.refresh_btn)
        
        self.mark_all_read_btn = QPushButton("✓ Mark All Read")
        self.mark_all_read_btn.clicked.connect(self.mark_all_as_acknowledged)
        header_layout.addWidget(self.mark_all_read_btn)
        
        header_layout.addStretch()
        center_layout.addLayout(header_layout)
        
        # Alert list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; }}")
        
        self.alert_container = QWidget()
        self.alert_layout = QVBoxLayout(self.alert_container)
        self.alert_layout.setSpacing(8)
        
        # Initialize with loading message
        self.initialize_loading_view()
        
        scroll.setWidget(self.alert_container)
        center_layout.addWidget(scroll)
        
        main_layout.addLayout(center_layout, 1)
        
        # Right panel - Alert details and actions
        self.right_panel = QFrame()
        self.right_panel.setFixedWidth(300)
        self.right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(12, 12, 12, 12)
        self.right_layout.setSpacing(12)
        
        # Initialize with no selection view
        self.initialize_no_selection_view()
        
        main_layout.addWidget(self.right_panel)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_alerts)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
        # Load initial data
        if DATABASE_ENABLED:
            self.load_cameras()
            self.load_alerts()
        else:
            self.show_error_message("Database not available")
    
    def initialize_loading_view(self):
        """Initialize loading view"""
        while self.alert_layout.count():
            item = self.alert_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        loading_label = QLabel("Loading alerts...")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt; padding: 40px;")
        self.alert_layout.addWidget(loading_label)
    
    def initialize_no_selection_view(self):
        """Initialize right panel with no selection"""
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        no_selection_label = QLabel("Select an alert to view details")
        no_selection_label.setAlignment(Qt.AlignCenter)
        no_selection_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt; padding: 40px;")
        self.right_layout.addWidget(no_selection_label)
        self.right_layout.addStretch()
    
    def show_error_message(self, message: str):
        """Show error message in UI"""
        error_label = QLabel(f"⚠️ {message}")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 11pt; padding: 40px;")
        
        while self.alert_layout.count():
            item = self.alert_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.alert_layout.addWidget(error_label)
    
    def load_cameras(self):
        """Load cameras for filter dropdown"""
        if not DATABASE_ENABLED:
            return
        
        try:
            cameras = CameraRepository.get_all_cameras()
            current_cameras = [self.camera_combo.itemText(i) for i in range(self.camera_combo.count())]
            self.camera_combo.clear()
            self.camera_combo.addItem("All Cameras")
            
            for camera in cameras:
                display_name = f"{camera.camera_id} - {camera.location_name}"
                if display_name not in current_cameras:
                    self.camera_combo.addItem(display_name)
                    
        except Exception as e:
            print(f"Error loading cameras: {e}")
    
    def load_alerts(self):
        """Load alerts from database"""
        if not DATABASE_ENABLED:
            self.show_error_message("Database connection not available")
            return
        
        try:
            # Get all alerts
            all_alerts = AlertRepository.get_all_alerts(limit=200)
            
            # Update statistics
            stats = AlertRepository.get_alert_statistics()
            if stats:
                stats_text = f"📊 Total (24h): {stats.get('total_alerts', 0)}\n"
                stats_text += f"🚨 Active: {stats.get('active_alerts', 0)}\n"
                stats_text += f"🔴 Critical: {stats.get('critical_alerts', 0)}\n"
                stats_text += f"📹 Cameras: {stats.get('cameras_with_alerts', 0)}"
                self.stats_label.setText(stats_text)
            
            # Filter alerts
            filtered_alerts = self.filter_alerts(all_alerts)
            
            # Populate alerts list
            self.populate_alerts_list(filtered_alerts)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error loading alerts: {error_details}")
            self.show_error_message(f"Failed to load alerts: {str(e)}")
    
    def filter_alerts(self, alerts: list) -> list:
        """Filter alerts based on current filter settings"""
        filtered = []
        
        for alert in alerts:
            # Severity filter
            if alert.severity.lower() not in self.filters['severity']:
                continue
            
            # Alert type filter
            if self.filters['alert_type'] != 'all':
                if self.filters['alert_type'].lower() not in alert.alert_type.lower():
                    # Try to match common variations
                    type_map = {
                        'ppe': 'ppe_violation',
                        'intruder': 'intruder_detected',
                        'unknown': 'unknown_face',
                        'blacklist': 'blacklist_match',
                        'camera': 'camera_offline',
                        'safety': 'safety_violation',
                        'unauthorized': 'unauthorized_area',
                        'suspicious': 'suspicious_behavior'
                    }
                    mapped_type = type_map.get(self.filters['alert_type'].lower().split()[0], '')
                    if mapped_type not in alert.alert_type.lower():
                        continue
            
            # Status filter
            if self.filters['status'] != 'all':
                if self.filters['status'].lower() != alert.status.lower():
                    # Handle variations
                    status_map = {
                        'acknowledged': ['acknowledged', 'read', 'viewed'],
                        'in progress': ['in_progress', 'assigned', 'working'],
                        'resolved': ['resolved', 'closed', 'completed'],
                        'dismissed': ['dismissed', 'ignored']
                    }
                    allowed_statuses = status_map.get(self.filters['status'].lower(), [])
                    if alert.status.lower() not in allowed_statuses:
                        continue
            
            # Camera filter
            if self.filters['camera'] != 'all':
                if alert.camera_id != self.filters['camera']:
                    continue
            
            # Time filter
            if alert.timestamp:
                time_range = self.filters.get('time_range', '24h')
                cutoff_time = self.get_cutoff_time(time_range)
                if alert.timestamp < cutoff_time:
                    continue
            
            filtered.append(alert)
        
        return filtered
    
    def get_cutoff_time(self, time_range: str):
        """Get cutoff time based on time range filter"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        if time_range == 'Last 7 days':
            return now - timedelta(days=7)
        elif time_range == 'Last 30 days':
            return now - timedelta(days=30)
        elif time_range == 'All time':
            return datetime.min
        else:  # Last 24 hours
            return now - timedelta(hours=24)
    
    def populate_alerts_list(self, alerts: list):
        """Populate the alerts list with alert items"""
        # Clear existing content
        while self.alert_layout.count():
            item = self.alert_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not alerts:
            no_alerts_label = QLabel("No alerts found")
            no_alerts_label.setAlignment(Qt.AlignCenter)
            no_alerts_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt; padding: 40px;")
            self.alert_layout.addWidget(no_alerts_label)
            return
        
        # Sort alerts by severity and timestamp
        severity_order = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4, 'info': 5}
        alerts.sort(key=lambda x: (severity_order.get(x.severity.lower(), 6), x.timestamp or datetime.min), reverse=True)
        
        # Create alert items
        for alert in alerts:
            alert_item = self.create_alert_item(alert)
            self.alert_layout.addWidget(alert_item)
        
        self.alert_layout.addStretch()
    
    def create_alert_item(self, alert: Alert) -> EventItem:
        """Create an EventItem widget for an alert"""
        # Create alert data for EventItem
        alert_data = {
            'title': f"{alert.get_severity_emoji()} {alert.get_alert_type_icon()} {alert.alert_type.title()}",
            'details': f"Camera: {alert.camera_id or 'Unknown'} | {alert.description or 'No description'}",
            'timestamp': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S') if alert.timestamp else 'Unknown time',
            'severity': alert.severity.lower(),
            'status': alert.status,
            'camera': alert.camera_id,
            'alert_id': alert.alert_id
        }
        
        # Create EventItem
        event_item = EventItem(alert_data)
        
        # Make it clickable
        event_item.setCursor(Qt.PointingHandCursor)
        event_item.mousePressEvent = lambda e, a=alert: self.on_alert_selected(a)
        
        # Add context menu
        event_item.setContextMenuPolicy(Qt.CustomContextMenu)
        event_item.customContextMenuRequested.connect(
            lambda pos, a=alert: self.show_alert_context_menu(pos, a)
        )
        
        return event_item
    
    def on_alert_selected(self, alert: Alert):
        """Handle alert selection"""
        self.current_selected_alert = alert
        self.update_alert_details(alert)
    
    def update_alert_details(self, alert: Alert):
        """Update right panel with alert details"""
        # Clear existing content
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Alert preview/title
        title_label = QLabel(f"{alert.get_severity_emoji()} {alert.get_alert_type_icon()} {alert.alert_type.title()}")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        self.right_layout.addWidget(title_label)
        
        # Timestamp
        time_label = QLabel(f"🕒 {alert.get_time_ago()}")
        time_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt;")
        self.right_layout.addWidget(time_label)
        
        self.right_layout.addSpacing(12)
        
        # Metadata
        metadata_title = QLabel("Metadata")
        metadata_title_font = QFont()
        metadata_title_font.setBold(True)
        metadata_title.setFont(metadata_title_font)
        self.right_layout.addWidget(metadata_title)
        
        metadata_text = f"""
        Alert ID: #{alert.alert_id}
        Severity: {alert.severity.title()}
        Type: {alert.alert_type.replace('_', ' ').title()}
        Status: {alert.status.title()}
        Camera: {alert.camera_id or 'Unknown'}
        Timestamp: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S') if alert.timestamp else 'Unknown'}
        """
        
        if alert.assigned_to:
            metadata_text += f"\nAssigned to: {alert.assigned_to}"
        
        metadata_label = QLabel(metadata_text)
        metadata_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt; line-height: 1.4;")
        metadata_label.setWordWrap(True)
        self.right_layout.addWidget(metadata_label)
        
        # Description
        if alert.description:
            self.right_layout.addSpacing(8)
            desc_title = QLabel("Description")
            desc_title_font = QFont()
            desc_title_font.setBold(True)
            desc_title.setFont(desc_title_font)
            self.right_layout.addWidget(desc_title)
            
            desc_label = QLabel(alert.description)
            desc_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt; padding: 5px; background-color: {COLORS['dark']}; border-radius: 4px;")
            desc_label.setWordWrap(True)
            self.right_layout.addWidget(desc_label)
        
        # Resolution notes if resolved
        if alert.resolution_notes and alert.status.lower() == 'resolved':
            self.right_layout.addSpacing(8)
            resolution_title = QLabel("Resolution Notes")
            resolution_title_font = QFont()
            resolution_title_font.setBold(True)
            resolution_title.setFont(desc_title_font)
            self.right_layout.addWidget(resolution_title)
            
            resolution_label = QLabel(alert.resolution_notes)
            resolution_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 9pt; padding: 5px; background-color: {COLORS['dark']}; border-radius: 4px;")
            resolution_label.setWordWrap(True)
            self.right_layout.addWidget(resolution_label)
        
        self.right_layout.addSpacing(16)
        
        # Actions
        actions_title = QLabel("Actions")
        actions_title_font = QFont()
        actions_title_font.setBold(True)
        actions_title.setFont(actions_title_font)
        self.right_layout.addWidget(actions_title)
        
        # Create action buttons based on alert status
        if alert.status.lower() == 'new':
            btn_ack = QPushButton("✓ Acknowledge")
            btn_ack.clicked.connect(lambda: self.acknowledge_alert(alert.alert_id))
            self.right_layout.addWidget(btn_ack)
        
        if alert.status.lower() in ['new', 'acknowledged']:
            btn_assign = QPushButton("👤 Assign to me")
            btn_assign.clicked.connect(lambda: self.assign_alert_to_me(alert.alert_id))
            self.right_layout.addWidget(btn_assign)
        
        if alert.status.lower() in ['new', 'acknowledged', 'in_progress']:
            btn_resolve = QPushButton("✅ Mark as Resolved")
            btn_resolve.clicked.connect(lambda: self.resolve_alert(alert.alert_id))
            self.right_layout.addWidget(btn_resolve)
            
            btn_dismiss = QPushButton("❌ Dismiss")
            btn_dismiss.clicked.connect(lambda: self.dismiss_alert(alert.alert_id))
            self.right_layout.addWidget(btn_dismiss)
        
        btn_view_camera = QPushButton("📹 View Camera")
        btn_view_camera.clicked.connect(lambda: self.view_camera_feed(alert.camera_id))
        self.right_layout.addWidget(btn_view_camera)
        
        self.right_layout.addStretch()
    
    def show_alert_context_menu(self, pos, alert: Alert):
        """Show context menu for alert"""
        menu = QMenu(self)
        
        if alert.status.lower() == 'new':
            ack_action = QAction("✓ Acknowledge", self)
            ack_action.triggered.connect(lambda: self.acknowledge_alert(alert.alert_id))
            menu.addAction(ack_action)
        
        if alert.status.lower() in ['new', 'acknowledged']:
            assign_action = QAction("👤 Assign to me", self)
            assign_action.triggered.connect(lambda: self.assign_alert_to_me(alert.alert_id))
            menu.addAction(assign_action)
        
        if alert.status.lower() in ['new', 'acknowledged', 'in_progress']:
            resolve_action = QAction("✅ Mark as Resolved", self)
            resolve_action.triggered.connect(lambda: self.resolve_alert(alert.alert_id))
            menu.addAction(resolve_action)
            
            dismiss_action = QAction("❌ Dismiss", self)
            dismiss_action.triggered.connect(lambda: self.dismiss_alert(alert.alert_id))
            menu.addAction(dismiss_action)
        
        copy_action = QAction("📋 Copy Alert ID", self)
        copy_action.triggered.connect(lambda: self.copy_alert_id(alert.alert_id))
        menu.addAction(copy_action)
        
        menu.exec_(self.mapToGlobal(pos))
    
    def acknowledge_alert(self, alert_id: int):
        """Acknowledge an alert"""
        try:
            success = AlertRepository.update_alert_status(alert_id, 'acknowledged')
            if success:
                QMessageBox.information(self, "Success", "Alert acknowledged")
                self.load_alerts()
                self.alerts_updated.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to acknowledge alert")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to acknowledge alert: {str(e)}")
    
    def assign_alert_to_me(self, alert_id: int):
        """Assign alert to current user"""
        try:
            # In a real app, you would get the current user from authentication
            current_user = "Current User"  # Replace with actual user
            success = AlertRepository.assign_alert(alert_id, current_user)
            if success:
                QMessageBox.information(self, "Success", f"Alert assigned to {current_user}")
                self.load_alerts()
                self.alerts_updated.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to assign alert")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to assign alert: {str(e)}")
    
    def resolve_alert(self, alert_id: int):
        """Resolve an alert with notes"""
        resolution_notes, ok = QInputDialog.getMultiLineText(
            self, "Resolve Alert", "Enter resolution notes:", ""
        )
        
        if ok and resolution_notes:
            try:
                success = AlertRepository.resolve_alert(alert_id, resolution_notes)
                if success:
                    QMessageBox.information(self, "Success", "Alert resolved")
                    self.load_alerts()
                    self.alerts_updated.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to resolve alert")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to resolve alert: {str(e)}")
    
    def dismiss_alert(self, alert_id: int):
        """Dismiss an alert"""
        reply = QMessageBox.question(
            self, "Dismiss Alert", 
            "Are you sure you want to dismiss this alert?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = AlertRepository.update_alert_status(alert_id, 'dismissed')
                if success:
                    QMessageBox.information(self, "Success", "Alert dismissed")
                    self.load_alerts()
                    self.alerts_updated.emit()
                else:
                    QMessageBox.warning(self, "Error", "Failed to dismiss alert")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to dismiss alert: {str(e)}")
    
    def mark_all_as_acknowledged(self):
        """Mark all visible alerts as acknowledged"""
        reply = QMessageBox.question(
            self, "Mark All as Read", 
            "Are you sure you want to mark all visible alerts as acknowledged?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Get current alerts
                all_alerts = AlertRepository.get_all_alerts(limit=200)
                filtered_alerts = self.filter_alerts(all_alerts)
                
                # Acknowledge each new alert
                count = 0
                for alert in filtered_alerts:
                    if alert.status.lower() == 'new':
                        AlertRepository.update_alert_status(alert.alert_id, 'acknowledged')
                        count += 1
                
                if count > 0:
                    QMessageBox.information(self, "Success", f"{count} alerts marked as acknowledged")
                    self.load_alerts()
                    self.alerts_updated.emit()
                else:
                    QMessageBox.information(self, "Info", "No new alerts to acknowledge")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to mark alerts as acknowledged: {str(e)}")
    
    def view_camera_feed(self, camera_id: str):
        """Open camera feed view"""
        if camera_id:
            QMessageBox.information(self, "View Camera", f"Opening feed for camera: {camera_id}")
            # In a real app, you would navigate to camera view
        else:
            QMessageBox.warning(self, "Warning", "No camera information available")
    
    def copy_alert_id(self, alert_id: int):
        """Copy alert ID to clipboard"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(str(alert_id))
        QMessageBox.information(self, "Copied", f"Alert ID {alert_id} copied to clipboard")
    
    def on_filter_changed(self):
        """Handle filter changes"""
        # Update severity filters
        self.filters['severity'] = []
        if self.check_critical.isChecked():
            self.filters['severity'].append('critical')
        if self.check_high.isChecked():
            self.filters['severity'].append('high')
        if self.check_medium.isChecked():
            self.filters['severity'].append('medium')
        if self.check_low.isChecked():
            self.filters['severity'].append('low')
        if self.check_info.isChecked():
            self.filters['severity'].append('info')
        
        # Update alert type filter
        alert_type = self.type_combo.currentText()
        if alert_type == "All":
            self.filters['alert_type'] = 'all'
        else:
            self.filters['alert_type'] = alert_type.lower().replace(' ', '_')
        
        # Update status filter
        status = self.status_combo.currentText()
        if status == "All":
            self.filters['status'] = 'all'
        else:
            self.filters['status'] = status.lower().replace(' ', '_')
        
        # Update camera filter
        camera = self.camera_combo.currentText()
        if camera == "All Cameras":
            self.filters['camera'] = 'all'
        else:
            # Extract camera ID from display text
            camera_id = camera.split(' - ')[0]
            self.filters['camera'] = camera_id
        
        # Update time filter
        self.filters['time_range'] = self.time_combo.currentText()
        
        # Reload alerts with new filters
        self.load_alerts()
    
    def clear_filters(self):
        """Clear all filters"""
        self.check_critical.setChecked(True)
        self.check_high.setChecked(True)
        self.check_medium.setChecked(True)
        self.check_low.setChecked(True)
        self.check_info.setChecked(False)
        self.type_combo.setCurrentIndex(0)
        self.camera_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.time_combo.setCurrentIndex(0)
        
        # Trigger filter update
        self.on_filter_changed()