"""
Live Monitor view - Multi-camera monitoring
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QCheckBox, QGridLayout, QFrame,
                               QScrollArea, QSpinBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.utils.components import CameraGrid, Card
from ui.utils.styles import COLORS


class LiveMonitorWidget(QWidget):
    """Live monitor with multiple camera streams"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Center area with camera grid
        center_layout = QVBoxLayout()
        
        # Grid control bar
        control_bar = QFrame()
        control_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 4px;
            }}
        """)
        control_layout = QHBoxLayout(control_bar)
        control_layout.setContentsMargins(12, 12, 12, 12)
        
        control_layout.addWidget(QLabel("Layout:"))
        layout_combo = QComboBox()
        layout_combo.addItems(["2x2 (4)", "3x3 (9)", "4x4 (16)", "2x3 (6)"])
        layout_combo.currentIndexChanged.connect(self._on_layout_changed)
        control_layout.addWidget(layout_combo)
        
        control_layout.addWidget(QLabel("Stream Quality:"))
        quality_combo = QComboBox()
        quality_combo.addItems(["1080p", "720p", "480p"])
        control_layout.addWidget(quality_combo)
        
        btn_save_layout = QPushButton("💾 Save Layout")
        btn_save_layout.setMaximumWidth(150)
        control_layout.addWidget(btn_save_layout)
        
        control_layout.addStretch()
        
        center_layout.addWidget(control_bar)
        
        # Camera grid
        self.camera_grid = CameraGrid(2, 2)
        center_layout.addWidget(self.camera_grid)
        
        main_layout.addLayout(center_layout, 2)
        
        # Right panel - Camera info and PTZ controls
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
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)
        
        # Selected camera info
        camera_title = QLabel("Selected Camera Info")
        camera_title_font = QFont()
        camera_title_font.setPointSize(11)
        camera_title_font.setBold(True)
        camera_title.setFont(camera_title_font)
        right_layout.addWidget(camera_title)
        
        camera_info = QLabel("Camera: Front Gate\nResolution: 1080p\nFPS: 30\nBitrate: 5 Mbps")
        camera_info.setStyleSheet(f"color: {COLORS['text_secondary']}; line-height: 1.6;")
        right_layout.addWidget(camera_info)
        
        # Stream status
        status_label = QLabel("Stream Status: 🟢 Online")
        status_label.setStyleSheet(f"color: {COLORS['success']};")
        right_layout.addWidget(status_label)
        
        # PTZ Controls
        ptz_title = QLabel("PTZ Controls")
        ptz_title_font = QFont()
        ptz_title_font.setPointSize(11)
        ptz_title_font.setBold(True)
        ptz_title.setFont(ptz_title_font)
        right_layout.addWidget(ptz_title)
        
        # PTZ direction buttons
        ptz_grid = QGridLayout()
        
        btn_up = QPushButton("⬆️")
        btn_left = QPushButton("⬅️")
        btn_right = QPushButton("➡️")
        btn_down = QPushButton("⬇️")
        
        for btn in [btn_up, btn_left, btn_right, btn_down]:
            btn.setFixedSize(40, 40)
        
        ptz_grid.addWidget(btn_up, 0, 1)
        ptz_grid.addWidget(btn_left, 1, 0)
        ptz_grid.addWidget(btn_right, 1, 2)
        ptz_grid.addWidget(btn_down, 2, 1)
        
        right_layout.addLayout(ptz_grid)
        
        # Zoom controls
        right_layout.addWidget(QLabel("Zoom:"))
        zoom_layout = QHBoxLayout()
        btn_zoom_in = QPushButton("🔍+")
        btn_zoom_out = QPushButton("🔍-")
        zoom_layout.addWidget(btn_zoom_in)
        zoom_layout.addWidget(btn_zoom_out)
        right_layout.addLayout(zoom_layout)
        
        # AI Overlay toggles
        overlay_title = QLabel("AI Overlays")
        overlay_title_font = QFont()
        overlay_title_font.setPointSize(11)
        overlay_title_font.setBold(True)
        overlay_title.setFont(overlay_title_font)
        right_layout.addWidget(overlay_title)
        
        check_person = QCheckBox("Person Detection")
        check_person.setChecked(True)
        right_layout.addWidget(check_person)
        
        check_ppe = QCheckBox("Helmet/PPE Detection")
        check_ppe.setChecked(True)
        right_layout.addWidget(check_ppe)
        
        check_face = QCheckBox("Face Match")
        right_layout.addWidget(check_face)
        
        check_reid = QCheckBox("ReID Tag")
        right_layout.addWidget(check_reid)
        
        # Create rule button
        btn_create_rule = QPushButton("📋 Create Rule")
        btn_create_rule.setObjectName("secondary")
        right_layout.addWidget(btn_create_rule)
        
        right_layout.addStretch()
        
        main_layout.addWidget(right_panel)
        
        self.layout_combo = layout_combo
    
    def _on_layout_changed(self, index):
        """Change camera grid layout"""
        layouts = [(2, 2), (3, 3), (4, 4), (2, 3)]
        cols, rows = layouts[index]
        self.camera_grid.set_grid_size(cols, rows)
