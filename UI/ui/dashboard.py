"""
Dashboard view - Command Center
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.utils.components import StatCard, ChartPlaceholder, EventItem
from ui.utils.styles import COLORS


class DashboardWidget(QWidget):
    """Main dashboard view"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; }}")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header = QLabel("Dashboard - Command Center")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Stats grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(12)
        
        stats_layout.addWidget(StatCard("Active Alerts", "12", "danger"), 0, 0)
        stats_layout.addWidget(StatCard("PPE Compliance", "94%", "success"), 0, 1)
        stats_layout.addWidget(StatCard("Cameras Online", "28/30", "warning"), 0, 2)
        stats_layout.addWidget(StatCard("Entry Success", "1,234", "success"), 0, 3)
        
        layout.addLayout(stats_layout)
        
        # Charts row
        charts_layout = QGridLayout()
        charts_layout.setSpacing(12)
        
        charts_layout.addWidget(ChartPlaceholder("Entry Success vs Denied"), 0, 0)
        charts_layout.addWidget(ChartPlaceholder("Camera Health"), 0, 1)
        charts_layout.addWidget(ChartPlaceholder("Top Incident Zones"), 1, 0)
        charts_layout.addWidget(ChartPlaceholder("Compliance Trend"), 1, 1)
        
        layout.addLayout(charts_layout)
        
        # Critical Events Section
        events_header = QLabel("Last 10 Critical Events")
        events_header_font = QFont()
        events_header_font.setPointSize(12)
        events_header_font.setBold(True)
        events_header.setFont(events_header_font)
        layout.addWidget(events_header)
        
        # Events list
        for i in range(5):
            event = EventItem({
                'title': f'Security Event #{i+1}',
                'details': f'Camera {i+1} - Zone B - No PPE Detected',
                'timestamp': f'2024-01-{15+i} 14:{30+i}:00',
                'severity': ['critical', 'warning', 'info'][i % 3]
            })
            layout.addWidget(event)
        
        # Quick Actions
        actions_header = QLabel("Quick Actions")
        actions_header_font = QFont()
        actions_header_font.setPointSize(12)
        actions_header_font.setBold(True)
        actions_header.setFont(actions_header_font)
        layout.addWidget(actions_header)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        btn_live = QPushButton("🔴 Go to Live")
        btn_live.setMinimumHeight(40)
        btn_live.setCursor(Qt.PointingHandCursor)
        
        btn_alerts = QPushButton("📋 Review Alerts")
        btn_alerts.setMinimumHeight(40)
        btn_alerts.setCursor(Qt.PointingHandCursor)
        
        btn_report = QPushButton("📊 Generate Report")
        btn_report.setMinimumHeight(40)
        btn_report.setCursor(Qt.PointingHandCursor)
        
        actions_layout.addWidget(btn_live)
        actions_layout.addWidget(btn_alerts)
        actions_layout.addWidget(btn_report)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
