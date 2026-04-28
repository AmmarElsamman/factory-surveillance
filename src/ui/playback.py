"""
Playback view - Video playback and timeline
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QSlider, QSpinBox, QDateEdit, QFrame,
                               QListWidget, QListWidgetItem, QComboBox, QCheckBox)
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QFont
from ui.utils.components import Card
from ui.utils.styles import COLORS


class PlaybackWidget(QWidget):
    """Video playback with timeline and event markers"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Left panel - Camera list
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
        
        left_title = QLabel("Camera List")
        left_title_font = QFont()
        left_title_font.setBold(True)
        left_title.setFont(left_title_font)
        left_layout.addWidget(left_title)
        
        # Date filter
        left_layout.addWidget(QLabel("Date:"))
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        left_layout.addWidget(date_edit)
        
        # Time filter
        left_layout.addWidget(QLabel("Start Time:"))
        time_spinbox = QSpinBox()
        time_spinbox.setMinimum(0)
        time_spinbox.setMaximum(23)
        time_spinbox.setValue(0)
        left_layout.addWidget(time_spinbox)
        
        # Camera filter
        left_layout.addWidget(QLabel("Filter:"))
        filter_combo = QComboBox()
        filter_combo.addItems(["All Cameras", "Zone A", "Zone B", "Zone C"])
        left_layout.addWidget(filter_combo)
        
        # Camera list
        camera_list = QListWidget()
        for i in range(30):
            item = QListWidgetItem(f"Camera {i+1} - Zone {chr(65 + i%3)}")
            camera_list.addItem(item)
        left_layout.addWidget(camera_list)
        
        main_layout.addWidget(left_panel)
        
        # Center panel - Video player and timeline
        center_layout = QVBoxLayout()
        
        # Video player area
        video_player = QFrame()
        video_player.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        video_player.setMinimumHeight(450)
        
        player_layout = QVBoxLayout(video_player)
        player_label = QLabel("📹 Video Player\n(Integrate ffmpeg/OpenCV)")
        player_label.setAlignment(Qt.AlignCenter)
        player_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        player_label_font = QFont()
        player_label_font.setPointSize(12)
        player_label.setFont(player_label_font)
        player_layout.addWidget(player_label)
        
        center_layout.addWidget(video_player)
        
        # Timeline and controls
        timeline_card = Card("Timeline & Event Markers")
        
        # Playback controls
        control_layout = QHBoxLayout()
        
        btn_play = QPushButton("▶️ Play")
        btn_pause = QPushButton("⏸️ Pause")
        btn_stop = QPushButton("⏹️ Stop")
        
        control_layout.addWidget(btn_play)
        control_layout.addWidget(btn_pause)
        control_layout.addWidget(btn_stop)
        control_layout.addStretch()
        
        timeline_card.content_layout.addLayout(control_layout)
        
        # Timeline slider with markers
        timeline_slider = QSlider(Qt.Horizontal)
        timeline_slider.setMinimum(0)
        timeline_slider.setMaximum(100)
        timeline_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {COLORS['secondary']};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['accent']};
                width: 14px;
                margin: -3px 0;
                border-radius: 7px;
            }}
        """)
        
        timeline_card.content_layout.addWidget(timeline_slider)
        
        # Time display
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("00:00:00"))
        time_layout.addStretch()
        time_layout.addWidget(QLabel("Total: 24:00:00"))
        timeline_card.content_layout.addLayout(time_layout)
        
        # Event markers
        markers_label = QLabel("Event Markers:")
        markers_label.setStyleSheet(f"font-weight: bold;")
        timeline_card.content_layout.addWidget(markers_label)
        
        check_helmet = QCheckBox("Helmet Violation")
        check_helmet.setChecked(True)
        timeline_card.content_layout.addWidget(check_helmet)
        
        check_face = QCheckBox("Unknown Face")
        check_face.setChecked(True)
        timeline_card.content_layout.addWidget(check_face)
        
        check_blacklist = QCheckBox("Blacklist Match")
        timeline_card.content_layout.addWidget(check_blacklist)
        
        check_intrusion = QCheckBox("Intrusion/Loitering")
        timeline_card.content_layout.addWidget(check_intrusion)
        
        center_layout.addWidget(timeline_card)
        
        main_layout.addLayout(center_layout, 1)
        
        # Right panel - Clip details
        right_panel = QFrame()
        right_panel.setFixedWidth(280)
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
        
        right_title = QLabel("Clip Details")
        right_title_font = QFont()
        right_title_font.setBold(True)
        right_title.setFont(right_title_font)
        right_layout.addWidget(right_title)
        
        details = QLabel(
            "Camera: Front Gate\n"
            "Date: 2024-01-15\n"
            "Duration: 2m 34s\n"
            "File Size: 125 MB\n"
            "Codec: H.264\n"
            "Resolution: 1080p"
        )
        details.setStyleSheet(f"color: {COLORS['text_secondary']};")
        right_layout.addWidget(details)
        
        # Export controls
        export_title = QLabel("Export")
        export_title_font = QFont()
        export_title_font.setBold(True)
        export_title.setFont(export_title_font)
        right_layout.addWidget(export_title)
        
        check_watermark = QCheckBox("Add Watermark")
        check_watermark.setChecked(True)
        right_layout.addWidget(check_watermark)
        
        check_hash = QCheckBox("Add Hash (Integrity)")
        right_layout.addWidget(check_hash)
        
        btn_export = QPushButton("📥 Export Clip")
        btn_export.setObjectName("success")
        right_layout.addWidget(btn_export)
        
        btn_share = QPushButton("🔗 Share Link")
        right_layout.addWidget(btn_share)
        
        right_layout.addStretch()
        
        main_layout.addWidget(right_panel)
