"""
Dashboard page - Command Center
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QScrollArea)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont

from ui.utils.styles import COLORS
from ui.components.cards import StatCard, Card
from ui.api_client import APIClient


class DashboardWidget(QWidget):
    # Signal emitted when a quick action button is clicked
    # The integer is the page index to navigate to
    navigate_to = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

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

        self.card_workers = StatCard("Active Workers", "—", status="success")
        self.card_cameras = StatCard("Cameras Online", "—", status="warning")
        self.card_alerts  = StatCard("Active Alerts",  "—", status="danger")

        stats_row.addWidget(self.card_workers)
        stats_row.addWidget(self.card_cameras)
        stats_row.addWidget(self.card_alerts)
        layout.addLayout(stats_row)

        # ── Quick Actions ──
        actions_card = Card("Quick Actions")

        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        # Page indices must match NavigationBar.MENU_ITEMS
        btn_ai      = QPushButton("🤖  AI Detection")
        btn_workers = QPushButton("👥  Workers")
        btn_cameras = QPushButton("🎥  Cameras")
        btn_alerts  = QPushButton("🚨  Alerts")

        for btn in [btn_ai, btn_workers, btn_cameras, btn_alerts]:
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.PointingHandCursor)

        # Connect each button to emit navigate_to with the correct page index
        btn_ai.clicked.connect(lambda: self.navigate_to.emit(1))
        btn_workers.clicked.connect(lambda: self.navigate_to.emit(2))
        btn_cameras.clicked.connect(lambda: self.navigate_to.emit(3))
        btn_alerts.clicked.connect(lambda: self.navigate_to.emit(4))

        actions_row.addWidget(btn_ai)
        actions_row.addWidget(btn_workers)
        actions_row.addWidget(btn_cameras)
        actions_row.addWidget(btn_alerts)
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

        # Load data after window is shown
        QTimer.singleShot(0, self.load_data)

    def load_data(self):
        """Load stats from API and update StatCards"""
        try:
            workers = APIClient.get_workers(status="active")
            self.card_workers.update_value(len(workers))

            cameras = APIClient.get_cameras()
            online  = [c for c in cameras if c.get("status") == "online"]
            self.card_cameras.update_value(f"{len(online)}/{len(cameras)}")

            self.card_alerts.update_value("0")  # TODO: wire alerts endpoint
        except Exception as e:
            print(f"Dashboard load error: {e}")