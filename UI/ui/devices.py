"""
Devices view - Camera inventory and management
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QFrame, QTableWidget, QTableWidgetItem,
                               QScrollArea, QCheckBox, QSpinBox, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from ui.utils.components import Card
from ui.utils.styles import COLORS
from repositories.camera_repository import CameraRepository
from models.camera import Camera

class DevicesWidget(QWidget):
    """Camera and device inventory management"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_selected_camera = None
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Header with statistics
        header_layout = QHBoxLayout()
        header = QLabel("Cameras")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header_layout.addWidget(header)
        
        # Statistics label
        self.stats_label = QLabel("Loading stats...")
        self.stats_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt;")
        header_layout.addWidget(self.stats_label, alignment=Qt.AlignRight)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Online", "Offline", "Maintenance", "Weak Signal"])
        self.status_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.status_combo)
        
        filter_layout.addWidget(QLabel("Zone:"))
        self.zone_combo = QComboBox()
        self.zone_combo.addItem("All Zones")
        self.zone_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.zone_combo)
        
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self.load_cameras)
        filter_layout.addWidget(btn_refresh)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # Device table
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Updated column count
        self.table.setHorizontalHeaderLabels(["Camera ID", "Name", "Zone", "Status", "IP Address", "Installation Date"])
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['card_bg']};
                alternate-background-color: {COLORS['dark']};
                border: 1px solid {COLORS['border']};
                gridline-color: {COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
        """)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_camera_selected)
        
        scroll.setWidget(self.table)
        main_layout.addWidget(scroll)
        
        # Device details section
        details_title = QLabel("Selected Camera Details")
        details_title_font = QFont()
        details_title_font.setPointSize(12)
        details_title_font.setBold(True)
        details_title.setFont(details_title_font)
        main_layout.addWidget(details_title)
        
        details_scroll = QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.details_container = QWidget()
        self.details_layout = QVBoxLayout(self.details_container)
        
        # Initialize with empty details
        self.initialize_empty_details()
        
        details_scroll.setWidget(self.details_container)
        main_layout.addWidget(details_scroll, 1)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
        # Load initial data
        self.load_cameras()
    
    def initialize_empty_details(self):
        """Initialize empty device details section"""
        # Clear existing layout
        while self.details_layout.count():
            item = self.details_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        empty_label = QLabel("Select a camera to view details")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt; padding: 40px;")
        self.details_layout.addWidget(empty_label)
    
    def load_cameras(self):
        """Load cameras from database"""
        try:
            # Get all cameras
            cameras = CameraRepository.get_all_cameras()
            
            # Get unique zones from repository
            zones = CameraRepository.get_all_zones()
            
            # Update zone filter dropdown
            current_zones = [self.zone_combo.itemText(i) for i in range(self.zone_combo.count())]
            self.zone_combo.clear()
            self.zone_combo.addItem("All Zones")
            
            for zone in zones:
                if zone and zone not in current_zones:
                    self.zone_combo.addItem(zone)
            
            # Update statistics
            stats = CameraRepository.get_camera_stats()
            if stats:
                stats_text = f"📊 Total: {stats.get('total_cameras', 0)} | "
                stats_text += f"🟢 Online: {stats.get('online_cameras', 0)} | "
                stats_text += f"🔴 Offline: {stats.get('offline_cameras', 0)} | "
                stats_text += f"🟡 Maintenance: {stats.get('maintenance_cameras', 0)}"
                if stats.get('weak_signal_cameras', 0) > 0:
                    stats_text += f" | 📶 Weak Signal: {stats.get('weak_signal_cameras', 0)}"
                self.stats_label.setText(stats_text)
            
            # Populate table
            self.table.setRowCount(len(cameras))
            
            for row, camera in enumerate(cameras):
                # Map status to emoji
                status_emoji = self.get_status_emoji(camera.status)
                
                # Format installation date
                install_date = ""
                if camera.installation_date:
                    if isinstance(camera.installation_date, str):
                        install_date = camera.installation_date
                    else:
                        install_date = camera.installation_date.strftime("%Y-%m-%d")
                
                # Create table items
                items = [
                    camera.camera_id,
                    camera.location_name,
                    camera.zone_type or "N/A",
                    f"{status_emoji} {camera.status.title()}",
                    camera.ip_address or "N/A",
                    install_date
                ]
                
                for col, value in enumerate(items):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    # Color coding for status
                    if col == 3:  # Status column
                        if camera.status == 'offline':
                            item.setForeground(Qt.red)
                        elif camera.status in ['maintenance', 'weak_signal']:
                            item.setForeground(Qt.darkYellow)
                        elif camera.status == 'online':
                            item.setForeground(Qt.darkGreen)
                    
                    self.table.setItem(row, col, item)
            
            self.table.resizeColumnsToContents()
            self.table.setMinimumHeight(300)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error details:\n{error_details}")
            QMessageBox.critical(self, "Error", f"Failed to load cameras: {str(e)}")
    
    def get_status_emoji(self, status: str) -> str:
        """Convert status to emoji"""
        status_map = {
            'online': '🟢',
            'offline': '🔴',
            'maintenance': '🟡',
            'weak_signal': '🟡'
        }
        return status_map.get(status.lower(), '⚪')
    
    def apply_filters(self):
        """Apply filters to camera list"""
        status_filter = self.status_combo.currentText()
        zone_filter = self.zone_combo.currentText()
        
        try:
            if status_filter == "All" and zone_filter == "All Zones":
                cameras = CameraRepository.get_all_cameras()
            elif status_filter != "All" and zone_filter == "All Zones":
                status_lower = status_filter.lower().replace(" ", "_")
                cameras = CameraRepository.get_cameras_by_status(status_lower)
            elif status_filter == "All" and zone_filter != "All Zones":
                cameras = CameraRepository.get_cameras_by_zone(zone_filter)
            else:
                # Both filters applied - we need to filter manually
                status_lower = status_filter.lower().replace(" ", "_")
                if zone_filter == "All Zones":
                    cameras = CameraRepository.get_cameras_by_status(status_lower)
                else:
                    all_cameras = CameraRepository.get_all_cameras()
                    cameras = [
                        cam for cam in all_cameras 
                        if cam.status == status_lower and cam.zone_type == zone_filter
                    ]
            
            # Update table with filtered results
            self.table.setRowCount(len(cameras))
            
            for row, camera in enumerate(cameras):
                status_emoji = self.get_status_emoji(camera.status)
                
                items = [
                    camera.camera_id,
                    camera.location_name,
                    camera.zone_type or "N/A",
                    f"{status_emoji} {camera.status.title()}",
                    camera.ip_address or "N/A",
                    camera.installation_date.strftime("%Y-%m-%d") if camera.installation_date else "N/A"
                ]
                
                for col, value in enumerate(items):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    if col == 3:  # Status column
                        if camera.status == 'offline':
                            item.setForeground(Qt.red)
                        elif camera.status == 'maintenance' or camera.status == 'weak_signal':
                            item.setForeground(Qt.yellow)
                        elif camera.status == 'online':
                            item.setForeground(Qt.green)
                    
                    self.table.setItem(row, col, item)
            
            self.table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.warning(self, "Filter Error", f"Failed to apply filters: {str(e)}")
    
    def on_camera_selected(self):
        """Handle camera selection from table"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        camera_id = self.table.item(row, 0).text()
        
        try:
            camera = CameraRepository.get_camera_by_id(camera_id)
            if camera:
                self.current_selected_camera = camera
                self.update_camera_details(camera)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load camera details: {str(e)}")
    
    def update_camera_details(self, camera: Camera):
        """Update device details section with camera information"""
        # Clear existing layout
        while self.details_layout.count():
            item = self.details_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Configuration card
        config_card = Card("Device Configuration")
        config_layout = QVBoxLayout()
        
        # Basic information
        info_text = f"""
        Camera ID: {camera.camera_id}
        Name: {camera.location_name}
        Zone: {camera.zone_type or 'Not assigned'}
        Status: {self.get_status_emoji(camera.status)} {camera.status.title()}
        IP Address: {camera.ip_address or 'Not configured'}
        Installation Date: {camera.installation_date or 'N/A'}
        """
        
        if camera.coordinates:
            lat = camera.coordinates.get('latitude', 'N/A')
            lon = camera.coordinates.get('longitude', 'N/A')
            info_text += f"\nCoordinates: {lat}, {lon}"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; line-height: 1.8;")
        config_layout.addWidget(info_label)
        
        # Field of View information
        if camera.field_of_view:
            fov_title = QLabel("Field of View")
            fov_title_font = QFont()
            fov_title_font.setBold(True)
            fov_title.setFont(fov_title_font)
            config_layout.addWidget(fov_title)
            
            fov_info = f"""
            Angle: {camera.field_of_view.get('angle', 'N/A')}°
            Range: {camera.field_of_view.get('range', 'N/A')} meters
            Direction: {camera.field_of_view.get('direction', 'N/A')}
            """
            
            fov_label = QLabel(fov_info)
            fov_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt;")
            config_layout.addWidget(fov_label)
        
        # Actions section
        actions_title = QLabel("Actions")
        actions_title_font = QFont()
        actions_title_font.setBold(True)
        actions_title.setFont(actions_title_font)
        config_layout.addWidget(actions_title)
        
        actions_layout = QHBoxLayout()
        
        # Status update buttons
        if camera.status != 'online':
            btn_set_online = QPushButton("🟢 Set Online")
            btn_set_online.clicked.connect(lambda: self.update_camera_status(camera.camera_id, 'online'))
            actions_layout.addWidget(btn_set_online)
        
        if camera.status != 'offline':
            btn_set_offline = QPushButton("🔴 Set Offline")
            btn_set_offline.clicked.connect(lambda: self.update_camera_status(camera.camera_id, 'offline'))
            actions_layout.addWidget(btn_set_offline)
        
        if camera.status != 'maintenance':
            btn_set_maintenance = QPushButton("🟡 Set Maintenance")
            btn_set_maintenance.clicked.connect(lambda: self.update_camera_status(camera.camera_id, 'maintenance'))
            actions_layout.addWidget(btn_set_maintenance)
        
        btn_refresh_status = QPushButton("🔄 Refresh Status")
        btn_refresh_status.clicked.connect(self.load_cameras)
        actions_layout.addWidget(btn_refresh_status)
        
        actions_layout.addStretch()
        config_layout.addLayout(actions_layout)
        
        config_card.content_layout = config_layout
        self.details_layout.addWidget(config_card)
        self.details_layout.addStretch()
    
    def update_camera_status(self, camera_id: str, new_status: str):
        """Update camera status in database"""
        try:
            success = CameraRepository.update_camera_status(camera_id, new_status)
            if success:
                QMessageBox.information(self, "Success", f"Camera {camera_id} status updated to {new_status}")
                self.load_cameras()  # Refresh the list
                
                # Update details if this camera is currently selected
                if self.current_selected_camera and self.current_selected_camera.camera_id == camera_id:
                    camera = CameraRepository.get_camera_by_id(camera_id)
                    if camera:
                        self.update_camera_details(camera)
            else:
                QMessageBox.warning(self, "Error", "Failed to update camera status")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")
    
    def refresh_data(self):
        """Periodic data refresh"""
        self.load_cameras()