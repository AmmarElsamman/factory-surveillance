"""
Analytics view - AI rule configuration and results
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QFrame, QTabWidget, QSpinBox,
                               QCheckBox, QSlider, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.utils.components import Card, ChartPlaceholder
from ui.utils.styles import COLORS


class AnalyticsWidget(QWidget):
    """Analytics and AI rule configuration"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Header
        header = QLabel("Analytics & AI Configuration")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        main_layout.addWidget(header)
        
        # Create tabs for different analytics
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget {{ background-color: {COLORS['dark']}; }}
            QTabBar::tab {{ background-color: {COLORS['secondary']}; padding: 8px 20px; color: {COLORS['text']}; }}
            QTabBar::tab:selected {{ background-color: {COLORS['accent']}; color: {COLORS['dark']}; }}
        """)
        
        # PPE Compliance tab
        ppe_scroll = QScrollArea()
        ppe_scroll.setWidgetResizable(True)
        ppe_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        ppe_container = QWidget()
        ppe_layout = QVBoxLayout(ppe_container)
        ppe_layout.setSpacing(16)
        
        # Configuration
        config_card = Card("PPE Configuration")
        
        config_grid = QGridLayout()
        
        config_grid.addWidget(QLabel("Enable Detection:"), 0, 0)
        check_enable = QCheckBox()
        check_enable.setChecked(True)
        config_grid.addWidget(check_enable, 0, 1)
        
        config_grid.addWidget(QLabel("Minimum Confidence:"), 1, 0)
        confidence_spin = QSpinBox()
        confidence_spin.setMinimum(0)
        confidence_spin.setMaximum(100)
        confidence_spin.setValue(85)
        confidence_spin.setSuffix("%")
        config_grid.addWidget(confidence_spin, 1, 1)
        
        config_grid.addWidget(QLabel("Alert on Missing:"), 2, 0)
        alert_combo = QComboBox()
        alert_combo.addItems(["Helmet", "Vest", "Both", "None"])
        config_grid.addWidget(alert_combo, 2, 1)
        
        config_grid.addWidget(QLabel("Detection Zone:"), 3, 0)
        zone_combo = QComboBox()
        zone_combo.addItems(["All Zones", "Zone A", "Zone B", "Zone C"])
        config_grid.addWidget(zone_combo, 3, 1)
        
        config_card.content_layout.addLayout(config_grid)
        
        btn_save_config = QPushButton("💾 Save Configuration")
        config_card.content_layout.addWidget(btn_save_config)
        
        ppe_layout.addWidget(config_card)
        
        # Results
        ppe_layout.addWidget(ChartPlaceholder("PPE Compliance by Zone"))
        ppe_layout.addWidget(ChartPlaceholder("Violation Trends"))
        
        # Statistics
        stats_card = Card("Statistics")
        stats_text = QLabel(
            "Total Detections: 12,456\n"
            "Violations Found: 245 (2%)\n"
            "Average Compliance: 98.2%\n"
            "Most Compliant Zone: Zone A (99.5%)\n"
            "Least Compliant Zone: Zone B (95.3%)"
        )
        stats_text.setStyleSheet(f"color: {COLORS['text_secondary']};")
        stats_card.content_layout.addWidget(stats_text)
        ppe_layout.addWidget(stats_card)
        
        ppe_layout.addStretch()
        ppe_scroll.setWidget(ppe_container)
        tabs.addTab(ppe_scroll, "👷 PPE Compliance")
        
        # Heatmap tab
        heatmap_scroll = QScrollArea()
        heatmap_scroll.setWidgetResizable(True)
        heatmap_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        heatmap_container = QWidget()
        heatmap_layout = QVBoxLayout(heatmap_container)
        
        heatmap_layout.addWidget(ChartPlaceholder("Activity Heatmap"))
        
        heatmap_config = Card("Heatmap Configuration")
        heatmap_config.content_layout.addWidget(QLabel("Time Range:"))
        time_combo = QComboBox()
        time_combo.addItems(["Last Hour", "Last Day", "Last Week", "Last Month"])
        heatmap_config.content_layout.addWidget(time_combo)
        
        heatmap_config.content_layout.addWidget(QLabel("Camera:"))
        cam_combo = QComboBox()
        cam_combo.addItems(["All Cameras", "Camera 1", "Camera 2", "Camera 3"])
        heatmap_config.content_layout.addWidget(cam_combo)
        
        btn_generate = QPushButton("📊 Generate Heatmap")
        heatmap_config.content_layout.addWidget(btn_generate)
        
        heatmap_layout.addWidget(heatmap_config)
        heatmap_layout.addStretch()
        
        heatmap_scroll.setWidget(heatmap_container)
        tabs.addTab(heatmap_scroll, "🔥 Heatmap")
        
        # Crowd/Occupancy tab
        crowd_scroll = QScrollArea()
        crowd_scroll.setWidgetResizable(True)
        crowd_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        crowd_container = QWidget()
        crowd_layout = QVBoxLayout(crowd_container)
        
        crowd_layout.addWidget(ChartPlaceholder("Occupancy Over Time"))
        crowd_layout.addWidget(ChartPlaceholder("Zone Capacity"))
        
        crowd_config = Card("Crowd Configuration")
        crowd_config.content_layout.addWidget(QLabel("Max Occupancy:"))
        occupancy_spin = QSpinBox()
        occupancy_spin.setMinimum(1)
        occupancy_spin.setMaximum(1000)
        occupancy_spin.setValue(150)
        crowd_config.content_layout.addWidget(occupancy_spin)
        
        crowd_config.content_layout.addWidget(QLabel("Alert Threshold (%):"))
        threshold_spin = QSpinBox()
        threshold_spin.setMinimum(0)
        threshold_spin.setMaximum(100)
        threshold_spin.setValue(80)
        crowd_config.content_layout.addWidget(threshold_spin)
        
        btn_update_crowd = QPushButton("⚙️ Update Settings")
        crowd_config.content_layout.addWidget(btn_update_crowd)
        
        crowd_layout.addWidget(crowd_config)
        crowd_layout.addStretch()
        
        crowd_scroll.setWidget(crowd_container)
        tabs.addTab(crowd_scroll, "👥 Crowd/Occupancy")
        
        # Intrusion/Line Crossing tab
        intrusion_scroll = QScrollArea()
        intrusion_scroll.setWidgetResizable(True)
        intrusion_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        intrusion_container = QWidget()
        intrusion_layout = QVBoxLayout(intrusion_container)
        
        intrusion_layout.addWidget(ChartPlaceholder("Intrusion Events"))
        intrusion_layout.addWidget(ChartPlaceholder("Restricted Area Violations"))
        
        intrusion_config = Card("Intrusion Configuration")
        intrusion_config.content_layout.addWidget(QLabel("Enable Intrusion Detection:"))
        check_intrusion = QCheckBox()
        check_intrusion.setChecked(True)
        intrusion_config.content_layout.addWidget(check_intrusion)
        
        intrusion_config.content_layout.addWidget(QLabel("Sensitivity:"))
        sensitivity_slider = QSlider(Qt.Horizontal)
        sensitivity_slider.setMinimum(0)
        sensitivity_slider.setMaximum(100)
        sensitivity_slider.setValue(70)
        intrusion_config.content_layout.addWidget(sensitivity_slider)
        
        intrusion_config.content_layout.addWidget(QLabel("Enable Line Crossing:"))
        check_line = QCheckBox()
        intrusion_config.content_layout.addWidget(check_line)
        
        intrusion_layout.addWidget(intrusion_config)
        intrusion_layout.addStretch()
        
        intrusion_scroll.setWidget(intrusion_container)
        tabs.addTab(intrusion_scroll, "⚠️ Intrusion/Line Crossing")
        
        main_layout.addWidget(tabs)
