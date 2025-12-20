"""
Access Control view - Door/gate access management
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QFrame, QListWidget, QListWidgetItem,
                               QScrollArea, QTabWidget, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.utils.components import Card, EventItem
from ui.utils.styles import COLORS


class AccessControlWidget(QWidget):
    """Access control and door management"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Left panel - Doors/Gates list
        left_panel = QFrame()
        left_panel.setFixedWidth(250)
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
        
        left_title = QLabel("Doors & Gates")
        left_title_font = QFont()
        left_title_font.setBold(True)
        left_title_font.setPointSize(11)
        left_title.setFont(left_title_font)
        left_layout.addWidget(left_title)
        
        # Filter by zone
        left_layout.addWidget(QLabel("Zone:"))
        zone_combo = QComboBox()
        zone_combo.addItems(["All Zones", "Entrance", "Exit", "Warehouse", "Office"])
        left_layout.addWidget(zone_combo)
        
        # Filter by status
        left_layout.addWidget(QLabel("Status:"))
        status_combo = QComboBox()
        status_combo.addItems(["All", "Online", "Offline", "Alarm"])
        left_layout.addWidget(status_combo)
        
        # Door list
        door_list = QListWidget()
        doors = [
            ("🚪 Main Entrance - Online", "main_entrance"),
            ("🚪 Side Exit - Online", "side_exit"),
            ("🚪 Warehouse Door 1 - Online", "warehouse_1"),
            ("🚪 Warehouse Door 2 - Offline", "warehouse_2"),
            ("🚪 Office Access - Online", "office"),
            ("🚪 Loading Bay - Online", "loading_bay"),
        ]
        
        for door_name, door_id in doors:
            item = QListWidgetItem(door_name)
            item.setData(Qt.UserRole, door_id)
            door_list.addItem(item)
        
        door_list.itemClicked.connect(lambda item: self._on_door_selected(item))
        left_layout.addWidget(door_list)
        
        main_layout.addWidget(left_panel)
        
        # Center panel - Access events feed
        center_layout = QVBoxLayout()
        
        events_title = QLabel("Access Events Feed")
        events_title_font = QFont()
        events_title_font.setPointSize(12)
        events_title_font.setBold(True)
        events_title.setFont(events_title_font)
        center_layout.addWidget(events_title)
        
        # Events scroll
        events_scroll = QScrollArea()
        events_scroll.setWidgetResizable(True)
        events_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        events_container = QWidget()
        events_layout = QVBoxLayout(events_container)
        events_layout.setSpacing(8)
        
        # Sample access events
        sample_events = [
            {'title': '✓ Access Granted', 'details': 'Main Entrance - Employee ID: EMP1234', 'timestamp': '2024-01-15 14:35:22', 'severity': 'success'},
            {'title': '✓ Access Granted', 'details': 'Office Access - Employee ID: EMP5678', 'timestamp': '2024-01-15 14:32:15', 'severity': 'success'},
            {'title': '❌ Access Denied', 'details': 'Warehouse Door 1 - Invalid credentials', 'timestamp': '2024-01-15 14:28:42', 'severity': 'warning'},
            {'title': '❓ Unknown User', 'details': 'Side Exit - No ID detected', 'timestamp': '2024-01-15 14:25:10', 'severity': 'info'},
            {'title': '✓ Access Granted', 'details': 'Loading Bay - Contractor ID: CNT999', 'timestamp': '2024-01-15 14:20:33', 'severity': 'success'},
            {'title': '⚠️ Multiple Attempts', 'details': 'Main Entrance - 3 failed attempts', 'timestamp': '2024-01-15 14:15:44', 'severity': 'warning'},
        ]
        
        for event in sample_events:
            event_item = EventItem(event)
            events_layout.addWidget(event_item)
        
        events_layout.addStretch()
        events_scroll.setWidget(events_container)
        center_layout.addWidget(events_scroll)
        
        main_layout.addLayout(center_layout, 1)
        
        # Right panel - Policy details
        right_panel = QFrame()
        right_panel.setFixedWidth(300)
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(12)
        
        # Door status
        right_title = QLabel("Selected Door Details")
        right_title_font = QFont()
        right_title_font.setBold(True)
        right_title_font.setPointSize(11)
        right_title.setFont(right_title_font)
        right_layout.addWidget(right_title)
        
        door_details = QLabel(
            "Door: Main Entrance\n"
            "Zone: Entrance\n"
            "Status: 🟢 Online\n"
            "Lock Type: Electronic\n"
            "Last Activity: 14:35:22\n"
            "Access Events (Today): 245"
        )
        door_details.setStyleSheet(f"color: {COLORS['text_secondary']}; line-height: 1.6;")
        right_layout.addWidget(door_details)
        
        # Policy & Schedule
        policy_title = QLabel("Access Policy")
        policy_title_font = QFont()
        policy_title_font.setBold(True)
        policy_title.setFont(policy_title_font)
        right_layout.addWidget(policy_title)
        
        policy_text = QLabel(
            "Weekday: 06:00 - 22:00\n"
            "Weekend: 08:00 - 18:00\n"
            "After-hours: Managers only\n"
            "Holidays: Closed"
        )
        policy_text.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt;")
        right_layout.addWidget(policy_text)
        
        # Anti-tailgating
        check_tailgate = QCheckBox("Anti-Tailgating Enabled")
        check_tailgate.setChecked(True)
        right_layout.addWidget(check_tailgate)
        
        # Control buttons
        btn_unlock = QPushButton("🔓 Unlock")
        btn_unlock.setObjectName("success")
        right_layout.addWidget(btn_unlock)
        
        btn_lock = QPushButton("🔒 Lock")
        right_layout.addWidget(btn_lock)
        
        btn_emergency = QPushButton("🚨 Emergency Open")
        btn_emergency.setObjectName("danger")
        right_layout.addWidget(btn_emergency)
        
        btn_policy = QPushButton("📋 Edit Policy")
        right_layout.addWidget(btn_policy)
        
        right_layout.addStretch()
        
        main_layout.addWidget(right_panel)
    
    def _on_door_selected(self, item):
        """Handle door selection"""
        pass
