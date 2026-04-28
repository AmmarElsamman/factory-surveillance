"""
Dashboard page - Command Center
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QGridLayout, QLabel, QPushButton, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from utils.styles import COLORS
from components.cards import StatCard, Card
from api_client import APIClient


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ── Scroll wrapper ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Page header ──
        header = QLabel("Dashboard")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(header)

        # ── Stats row ──
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        self.card_workers = StatCard("Active Workers", "-", status="success")
        self.card_cameras = StatCard("Cameras Online", "-", status="warning")
        self.card_alerts = StatCard("Active Alerts", "-", status="danger")
        
        stats_row.addWidget(self.card_workers)
        stats_row.addWidget(self.card_cameras)
        stats_row.addWidget(self.card_alerts)

        layout.addLayout(stats_row)

        # ── Quick actions ──
        actions_card = Card("Quick Actions")

        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        btn_live  = QPushButton("🤖  AI Detection")
        btn_live.setMinimumHeight(40)
        btn_live.setCursor(Qt.PointingHandCursor)

        btn_workers = QPushButton("👥  Workers")
        btn_workers.setMinimumHeight(40)
        btn_workers.setCursor(Qt.PointingHandCursor)

        btn_cameras = QPushButton("🎥  Cameras")
        btn_cameras.setMinimumHeight(40)
        btn_cameras.setCursor(Qt.PointingHandCursor)

        actions_row.addWidget(btn_live)
        actions_row.addWidget(btn_workers)
        actions_row.addWidget(btn_cameras)
        actions_row.addStretch()

        actions_widget = QWidget()
        actions_widget.setLayout(actions_row)
        actions_card.add_content(actions_widget)
        layout.addWidget(actions_card)

        layout.addStretch()

        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        self.load_data()

    def load_data(self):
        """Load stats from API and update StatCards"""
        try:
            workers = APIClient.get_workers(status="active")
            self.card_workers.update_value(len(workers))
            
            cameras = APIClient.get_cameras()
            online_cameras = [c for c in cameras if c.get("status") == "online"]
            self.card_cameras.update_value(f"{len(online_cameras)}/{len(cameras)}")
            
            self.card_alerts.update_value("0") #TODO
        
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
        pass