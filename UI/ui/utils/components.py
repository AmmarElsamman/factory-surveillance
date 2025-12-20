"""
Reusable UI components
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGridLayout, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QLinearGradient, QPainter, QPixmap
from ui.utils.styles import COLORS


class Card(QFrame):
    """Reusable card widget"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        self.setFrameShape(QFrame.StyledPanel)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        if title:
            title_label = QLabel(title)
            title_font = QFont()
            title_font.setPointSize(12)
            title_font.setBold(True)
            title_label.setFont(title_font)
            layout.addWidget(title_label)
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.content_layout)
    
    def add_content(self, widget):
        """Add widget to card content"""
        self.content_layout.addWidget(widget)
    
    def set_content_layout(self, layout):
        """Set custom layout for card content"""
        # Clear existing content layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add the new layout
        self.layout().addLayout(layout)


class ExpandableCard(Card):
    """Card with expandable/collapsible content"""
    def __init__(self, title="", expanded=True, parent=None):
        super().__init__(parent)
        
        # Header with expand button
        self.header_widget = QWidget()
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.expand_btn = QPushButton("▼" if expanded else "▶")
        self.expand_btn.setFixedSize(24, 24)
        self.expand_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-color: transparent;
                color: {COLORS['text_secondary']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: {COLORS['accent']};
            }}
        """)
        self.expand_btn.clicked.connect(self.toggle_expand)
        header_layout.addWidget(self.expand_btn)
        
        self.layout().insertWidget(0, self.header_widget)
        
        # Content container (can be shown/hidden)
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 12, 0, 0)
        self.layout().insertWidget(1, self.content_container)
        
        self.expanded = expanded
        self.content_container.setVisible(expanded)
    
    def toggle_expand(self):
        """Toggle expanded state"""
        self.expanded = not self.expanded
        self.content_container.setVisible(self.expanded)
        self.expand_btn.setText("▼" if self.expanded else "▶")
    
    def add_content(self, widget):
        """Add widget to card content"""
        self.content_layout.addWidget(widget)


class StatCard(Card):
    """Statistics card with value and label"""
    def __init__(self, label="", value="0", status="normal", parent=None):
        super().__init__(parent=parent)
        
        value_label = QLabel(str(value))
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignCenter)
        
        label_widget = QLabel(label)
        label_font = QFont()
        label_font.setPointSize(10)
        label_widget.setFont(label_font)
        label_widget.setAlignment(Qt.AlignCenter)
        label_widget.setStyleSheet(f"color: {COLORS['text_secondary']};")
        
        # Set color based on status
        if status == "danger":
            value_label.setStyleSheet(f"color: {COLORS['danger']};")
        elif status == "success":
            value_label.setStyleSheet(f"color: {COLORS['success']};")
        elif status == "warning":
            value_label.setStyleSheet(f"color: {COLORS['warning']};")
        
        self.content_layout.addWidget(value_label)
        self.content_layout.addWidget(label_widget)


class TrendStatCard(Card):
    """Statistics card with trend indicators"""
    def __init__(self, label="", value="0", trend=0, trend_period="vs last week", parent=None):
        super().__init__(parent=parent)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(4)
        
        # Value with trend indicator
        value_layout = QHBoxLayout()
        
        value_label = QLabel(str(value))
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_layout.addWidget(value_label)
        
        # Trend indicator
        if trend != 0:
            trend_icon = "📈" if trend > 0 else "📉"
            trend_label = QLabel(f"{trend_icon} {abs(trend)}%")
            trend_label.setStyleSheet(f"""
                color: {'#4CAF50' if trend > 0 else '#F44336'};
                font-size: 10pt;
                font-weight: bold;
            """)
            value_layout.addWidget(trend_label)
        
        value_layout.addStretch()
        main_layout.addLayout(value_layout)
        
        # Label
        label_widget = QLabel(label)
        label_font = QFont()
        label_font.setPointSize(10)
        label_widget.setFont(label_font)
        label_widget.setStyleSheet(f"color: {COLORS['text_secondary']};")
        main_layout.addWidget(label_widget)
        
        # Trend period
        if trend != 0:
            period_label = QLabel(trend_period)
            period_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 8pt;")
            main_layout.addWidget(period_label)
        
        self.content_layout.addLayout(main_layout)


class ChartPlaceholder(Card):
    """Placeholder for charts"""
    def __init__(self, title="Chart", parent=None):
        super().__init__(title, parent)
        
        placeholder = QLabel("📊 Chart Placeholder\n(Integrate matplotlib/pyqtgraph)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet(f"color: {COLORS['text_secondary']}; padding: 40px;")
        placeholder_font = QFont()
        placeholder_font.setPointSize(11)
        placeholder.setFont(placeholder_font)
        
        self.content_layout.addWidget(placeholder)


class EventItem(QFrame):
    """Event/Alert list item with enhanced features"""
    clicked = Signal(dict)
    context_menu_requested = Signal(object, dict)  # Signal for context menu
    
    def __init__(self, event_data=None, parent=None):
        super().__init__(parent)
        self.event_data = event_data or {}
        self.alert_id = self.event_data.get('alert_id')
        self.setCursor(Qt.PointingHandCursor)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-left: 4px solid {self._get_status_color()};
                border-radius: 4px;
                padding: 12px;
                margin: 4px 0px;
            }}
            QFrame:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Header with severity icon and title
        header_layout = QHBoxLayout()
        
        # Severity icon
        severity = self.event_data.get('severity', 'info')
        severity_icon = QLabel(self._get_severity_emoji(severity))
        severity_icon.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(severity_icon)
        
        # Title
        title = QLabel(self.event_data.get('title', 'Event'))
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Status badge (for alerts)
        if 'status' in self.event_data:
            status_badge = QLabel(f" • {self.event_data['status'].title()}")
            status_badge.setStyleSheet(f"""
                color: {self._get_status_color(self.event_data['status'])};
                font-size: 9pt;
                font-weight: bold;
            """)
            header_layout.addWidget(status_badge)
        
        layout.addLayout(header_layout)
        
        # Details
        details = QLabel(self.event_data.get('details', ''))
        details.setStyleSheet(f"color: {COLORS['text_secondary']};")
        details_font = QFont()
        details_font.setPointSize(9)
        details.setFont(details_font)
        details.setWordWrap(True)
        layout.addWidget(details)
        
        # Footer with timestamp and camera info
        footer_layout = QHBoxLayout()
        
        # Timestamp
        timestamp = QLabel(self.event_data.get('timestamp', ''))
        timestamp.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 8pt;")
        footer_layout.addWidget(timestamp)
        
        footer_layout.addStretch()
        
        # Camera info (if available)
        if 'camera' in self.event_data:
            camera_label = QLabel(f"📹 {self.event_data['camera']}")
            camera_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 8pt;")
            footer_layout.addWidget(camera_label)
        
        layout.addLayout(footer_layout)
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)
    
    def _get_status_color(self, status=None):
        """Get color based on status or severity"""
        if status:
            # For alert status
            status_map = {
                'new': COLORS['danger'],
                'acknowledged': COLORS['warning'],
                'in_progress': COLORS['primary'],
                'resolved': COLORS['success'],
                'dismissed': COLORS['text_secondary']
            }
            return status_map.get(status.lower(), COLORS['accent'])
        else:
            # For severity
            severity = self.event_data.get('severity', 'info')
            if severity == 'critical':
                return COLORS['danger']
            elif severity == 'warning':
                return COLORS['warning']
            elif severity == 'success':
                return COLORS['success']
            return COLORS['accent']
    
    def _get_severity_emoji(self, severity):
        """Get emoji for severity level"""
        severity_map = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵',
            'info': 'ℹ️'
        }
        return severity_map.get(severity.lower(), '⚪')
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.event_data)
        super().mousePressEvent(event)
    
    def on_context_menu(self, pos):
        """Handle context menu request"""
        self.context_menu_requested.emit(pos, self.event_data)


class StatusBadge(QLabel):
    """Status badge for alerts/workers"""
    def __init__(self, status="new", severity="medium", parent=None):
        super().__init__(parent)
        self.status = status.lower()
        self.severity = severity.lower()
        
        self.update_display()
    
    def update_display(self):
        """Update badge display"""
        # Map status to display text and color
        status_map = {
            'new': ('New', COLORS['danger']),
            'acknowledged': ('Acknowledged', COLORS['warning']),
            'in_progress': ('In Progress', COLORS['primary']),
            'resolved': ('Resolved', COLORS['success']),
            'dismissed': ('Dismissed', COLORS['text_secondary']),
            'active': ('Active', COLORS['success']),
            'inactive': ('Inactive', COLORS['text_secondary']),
            'suspended': ('Suspended', COLORS['danger']),
            'on_leave': ('On Leave', COLORS['warning'])
        }
        
        text, color = status_map.get(self.status, ('Unknown', COLORS['accent']))
        
        self.setText(text)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color}20;
                color: {color};
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 9pt;
                font-weight: bold;
            }}
        """)
        self.setAlignment(Qt.AlignCenter)
    
    def set_status(self, status):
        """Update status"""
        self.status = status.lower()
        self.update_display()


class WorkerProfileCard(Card):
    """Card for displaying worker profile information"""
    profile_clicked = Signal(dict)
    
    def __init__(self, worker_data=None, parent=None):
        super().__init__("", parent)
        self.worker_data = worker_data or {}
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Header with name and status
        header_layout = QHBoxLayout()
        
        # Worker icon/avatar
        avatar_label = QLabel("👤")
        avatar_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(avatar_label)
        
        # Name and ID
        name_layout = QVBoxLayout()
        name_label = QLabel(self.worker_data.get('full_name', 'Unknown Worker'))
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(11)
        name_label.setFont(name_font)
        name_layout.addWidget(name_label)
        
        id_label = QLabel(f"ID: {self.worker_data.get('employee_code', 'N/A')}")
        id_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt;")
        name_layout.addWidget(id_label)
        
        header_layout.addLayout(name_layout)
        header_layout.addStretch()
        
        # Status indicator
        status = self.worker_data.get('status', 'active')
        status_label = QLabel(self._get_status_emoji(status))
        status_label.setToolTip(f"Status: {status.title()}")
        status_label.setStyleSheet("font-size: 16px;")
        header_layout.addWidget(status_label)
        
        layout.addLayout(header_layout)
        
        # Details grid
        details_grid = QGridLayout()
        details_grid.setSpacing(4)
        
        # Department
        details_grid.addWidget(QLabel("Department:"), 0, 0)
        dept_label = QLabel(self.worker_data.get('department', 'N/A'))
        dept_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        details_grid.addWidget(dept_label, 0, 1)
        
        # Role
        details_grid.addWidget(QLabel("Role:"), 1, 0)
        role_label = QLabel(self.worker_data.get('role', 'N/A'))
        role_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        details_grid.addWidget(role_label, 1, 1)
        
        # Authorization
        details_grid.addWidget(QLabel("Auth:"), 0, 2)
        auth_status = self.worker_data.get('is_authorized', False)
        auth_label = QLabel("✅" if auth_status else "❌")
        auth_label.setStyleSheet(f"color: {'#4CAF50' if auth_status else '#F44336'}; font-size: 14px;")
        auth_label.setToolTip("Authorized" if auth_status else "Unauthorized")
        details_grid.addWidget(auth_label, 0, 3)
        
        # Registration date
        if 'registration_date' in self.worker_data:
            details_grid.addWidget(QLabel("Registered:"), 1, 2)
            reg_label = QLabel(self.worker_data.get('registration_date', 'N/A'))
            reg_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            details_grid.addWidget(reg_label, 1, 3)
        
        layout.addLayout(details_grid)
        
        # Contact info (if available)
        if 'contact_info' in self.worker_data:
            contact_layout = QVBoxLayout()
            contact_label = QLabel("📞 Contact:")
            contact_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt; font-weight: bold;")
            contact_layout.addWidget(contact_label)
            
            contact_text = ""
            contact_info = self.worker_data['contact_info']
            if isinstance(contact_info, dict):
                if 'email' in contact_info:
                    contact_text += f"📧 {contact_info['email']}\n"
                if 'phone' in contact_info:
                    contact_text += f"📞 {contact_info['phone']}"
            
            if contact_text:
                contact_details = QLabel(contact_text.strip())
                contact_details.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 8pt;")
                contact_details.setWordWrap(True)
                contact_layout.addWidget(contact_details)
            
            layout.addLayout(contact_layout)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        view_btn = QPushButton("View")
        view_btn.setMaximumHeight(25)
        view_btn.clicked.connect(lambda: self.profile_clicked.emit(self.worker_data))
        actions_layout.addWidget(view_btn)
        
        # Quick status toggle (if authorized)
        if self.worker_data.get('is_authorized', False):
            suspend_btn = QPushButton("Suspend")
            suspend_btn.setMaximumHeight(25)
            suspend_btn.setObjectName("warning")
            actions_layout.addWidget(suspend_btn)
        else:
            authorize_btn = QPushButton("Authorize")
            authorize_btn.setMaximumHeight(25)
            authorize_btn.setObjectName("success")
            actions_layout.addWidget(authorize_btn)
        
        layout.addLayout(actions_layout)
        
        self.content_layout.addLayout(layout)
    
    def _get_status_emoji(self, status):
        """Get emoji for worker status"""
        status_map = {
            'active': '🟢',
            'inactive': '⚫',
            'suspended': '🔴',
            'on_leave': '🟡',
            'terminated': '🔴'
        }
        return status_map.get(status.lower(), '⚪')
    
    def mousePressEvent(self, event):
        """Handle click on card"""
        if event.button() == Qt.LeftButton:
            self.profile_clicked.emit(self.worker_data)
        super().mousePressEvent(event)


class CameraGrid(QWidget):
    """Grid layout for camera displays"""
    camera_clicked = Signal(str)  # Signal emitted when camera is clicked
    
    def __init__(self, cols=2, rows=2, parent=None):
        super().__init__(parent)
        self.cols = cols
        self.rows = rows
        self.camera_widgets = {}
        
        layout = QGridLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for i in range(rows):
            for j in range(cols):
                self.create_camera_widget(layout, i, j, f"Camera {i*cols + j + 1}")
    
    def create_camera_widget(self, layout, row, col, camera_id):
        """Create a camera widget at specified position"""
        camera_widget = QFrame()
        camera_widget.setObjectName(camera_id)
        camera_widget.setCursor(Qt.PointingHandCursor)
        camera_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            QFrame:hover {{
                background-color: {COLORS['secondary']};
                border-color: {COLORS['accent']};
            }}
        """)
        camera_widget.setMinimumHeight(300)
        
        camera_layout = QVBoxLayout(camera_widget)
        
        # Camera header
        header_layout = QHBoxLayout()
        
        camera_label = QLabel(camera_id)
        camera_label.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold;")
        header_layout.addWidget(camera_label)
        
        status_label = QLabel("⚫")
        status_label.setStyleSheet("font-size: 12px;")
        status_label.setToolTip("Status: Unknown")
        header_layout.addWidget(status_label)
        
        header_layout.addStretch()
        camera_layout.addLayout(header_layout)
        
        # Camera feed placeholder
        feed_placeholder = QLabel("📹 Live Feed")
        feed_placeholder.setAlignment(Qt.AlignCenter)
        feed_placeholder.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                background-color: {COLORS['dark']};
                border-radius: 2px;
                padding: 20px;
                margin: 5px;
            }}
        """)
        camera_layout.addWidget(feed_placeholder, 1)
        
        # Camera info
        info_label = QLabel("Resolution: 1920x1080\nFPS: 30")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 8pt;")
        camera_layout.addWidget(info_label)
        
        # Store widget reference
        self.camera_widgets[camera_id] = {
            'widget': camera_widget,
            'status_label': status_label,
            'feed_label': feed_placeholder,
            'info_label': info_label
        }
        
        # Connect click event
        camera_widget.mousePressEvent = lambda e, cam_id=camera_id: self.on_camera_clicked(cam_id)
        
        layout.addWidget(camera_widget, row, col)
    
    def on_camera_clicked(self, camera_id):
        """Handle camera click"""
        self.camera_clicked.emit(camera_id)
    
    def set_grid_size(self, cols, rows):
        """Change grid size"""
        # Clear existing layout
        for i in reversed(range(self.layout().count())): 
            widget = self.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        self.camera_widgets.clear()
        self.cols = cols
        self.rows = rows
        
        # Create new grid
        for i in range(rows):
            for j in range(cols):
                camera_id = f"Camera {i*cols + j + 1}"
                self.create_camera_widget(self.layout(), i, j, camera_id)
    
    def update_camera_status(self, camera_id, status, location=None, resolution=None, fps=None):
        """Update camera status and information"""
        if camera_id in self.camera_widgets:
            camera_data = self.camera_widgets[camera_id]
            
            # Update status
            status_icons = {
                'online': '🟢',
                'offline': '🔴',
                'weak_signal': '🟡',
                'maintenance': '🟠'
            }
            
            status_icon = status_icons.get(status.lower(), '⚫')
            camera_data['status_label'].setText(status_icon)
            camera_data['status_label'].setToolTip(f"Status: {status.title()}")
            
            # Update camera label if location is provided
            if location:
                camera_label = camera_data['widget'].layout().itemAt(0).layout().itemAt(0).widget()
                camera_label.setText(f"{camera_id} - {location}")
            
            # Update info if resolution/fps provided
            if resolution or fps:
                info_text = ""
                if resolution:
                    info_text += f"Resolution: {resolution}\n"
                if fps:
                    info_text += f"FPS: {fps}"
                camera_data['info_label'].setText(info_text)
    
    def add_camera_feed(self, camera_id, image_path=None):
        """Add camera feed image (placeholder for actual video feed)"""
        if camera_id in self.camera_widgets:
            camera_data = self.camera_widgets[camera_id]
            
            if image_path:
                # Load and display image
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        camera_data['feed_label'].size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    camera_data['feed_label'].setPixmap(scaled_pixmap)
                    camera_data['feed_label'].setScaledContents(True)
            else:
                # Reset to placeholder
                camera_data['feed_label'].setText("📹 Live Feed")


class AlertSummaryCard(Card):
    """Card for displaying alert summary"""
    def __init__(self, alert_stats=None, parent=None):
        super().__init__("Alert Summary", parent)
        self.alert_stats = alert_stats or {}
        
        # Create grid layout for statistics
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Critical alerts
        critical_card = StatCard(
            "Critical Alerts",
            str(self.alert_stats.get('critical_alerts', 0)),
            "danger"
        )
        grid_layout.addWidget(critical_card, 0, 0)
        
        # High alerts
        high_card = StatCard(
            "High Alerts", 
            str(self.alert_stats.get('high_alerts', 0)),
            "warning"
        )
        grid_layout.addWidget(high_card, 0, 1)
        
        # Active alerts
        active_card = StatCard(
            "Active Alerts",
            str(self.alert_stats.get('active_alerts', 0)),
            "warning"
        )
        grid_layout.addWidget(active_card, 1, 0)
        
        # Total alerts (24h)
        total_card = StatCard(
            "Total (24h)",
            str(self.alert_stats.get('total_alerts', 0)),
            "normal"
        )
        grid_layout.addWidget(total_card, 1, 1)
        
        self.content_layout.addLayout(grid_layout)
        
        # Add refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_stats)
        self.content_layout.addWidget(refresh_btn)
    
    def refresh_stats(self):
        """Refresh alert statistics"""
        # This would typically emit a signal to refresh data
        print("Refreshing alert statistics...")
    
    def update_stats(self, new_stats):
        """Update displayed statistics"""
        self.alert_stats.update(new_stats)
        # Here you would update the individual stat cards
        # For simplicity, we'll just note that stats were updated
        print("Alert stats updated")


class QuickActionsCard(Card):
    """Card for quick actions"""
    action_triggered = Signal(str)  # Signal emitted when action is triggered
    
    def __init__(self, title="Quick Actions", parent=None):
        super().__init__(title, parent)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Define actions with icons and colors
        actions = [
            ("🔄 Refresh All", "refresh_all", COLORS['primary']),
            ("📊 View Reports", "view_reports", COLORS['success']),
            ("⚙️ Settings", "settings", COLORS['warning']),
            ("🆘 Emergency", "emergency", COLORS['danger']),
            ("📁 Export Data", "export_data", COLORS['accent']),
            ("🖨️ Print", "print", COLORS['text_secondary']),
            ("📈 Analytics", "analytics", COLORS['primary']),
            ("👥 Manage Users", "manage_users", COLORS['success'])
        ]
        
        for i, (label, action_id, color) in enumerate(actions):
            row = i // 2
            col = i % 2
            
            btn = QPushButton(label)
            btn.setObjectName(action_id)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color}20;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 6px;
                    padding: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color}30;
                    border-color: {color};
                }}
                QPushButton:pressed {{
                    background-color: {color}40;
                }}
            """)
            btn.clicked.connect(lambda checked, a_id=action_id: self.on_action_clicked(a_id))
            
            grid_layout.addWidget(btn, row, col)
        
        self.content_layout.addLayout(grid_layout)
    
    def on_action_clicked(self, action_id):
        """Handle action button click"""
        self.action_triggered.emit(action_id)


class SearchBar(QFrame):
    """Search bar component"""
    search_requested = Signal(str)
    filter_changed = Signal(dict)
    
    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Search input
        self.search_input = QPushButton("🔍 " + placeholder)
        self.search_input.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 16px;
                text-align: left;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
                border-color: {COLORS['accent']};
            }}
        """)
        self.search_input.clicked.connect(self.show_search_dialog)
        layout.addWidget(self.search_input, 1)
        
        # Filter button
        self.filter_btn = QPushButton("⚙️ Filters")
        self.filter_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
                border-color: {COLORS['accent']};
            }}
        """)
        self.filter_btn.clicked.connect(self.show_filter_dialog)
        layout.addWidget(self.filter_btn)
    
    def show_search_dialog(self):
        """Show search dialog (placeholder)"""
        from PySide6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Search", "Enter search term:")
        if ok and text:
            self.search_requested.emit(text)
            self.search_input.setText(f"🔍 {text}")
    
    def show_filter_dialog(self):
        """Show filter dialog (placeholder)"""
        print("Showing filter dialog...")
        # In a real implementation, this would show a filter dialog
        # and emit filter_changed signal with filter parameters


class LoadingSpinner(QLabel):
    """Loading spinner component"""
    def __init__(self, size=40, parent=None):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        
        # Create simple text spinner
        self.spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.current_frame = 0
        
        self.setStyleSheet(f"color: {COLORS['accent']}; font-size: {size//2}px;")
        self.setText(self.spinner_frames[0])
        
        # Start animation
        self.timer = self.startTimer(100)
    
    def timerEvent(self, event):
        """Update spinner animation"""
        self.current_frame = (self.current_frame + 1) % len(self.spinner_frames)
        self.setText(self.spinner_frames[self.current_frame])
    
    def start(self):
        """Start spinner animation"""
        self.show()
        if not self.timer:
            self.timer = self.startTimer(100)
    
    def stop(self):
        """Stop spinner animation"""
        self.hide()
        if self.timer:
            self.killTimer(self.timer)
            self.timer = None