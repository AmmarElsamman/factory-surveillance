"""
Workers Management View - API Driven
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QComboBox, QGridLayout,
                               QScrollArea, QSpacerItem, QSizePolicy, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from utils.styles import COLORS
from components.cards import Card
from api_client import APIClient

class WorkersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_workers = []  # Local cache for snappy filtering
        
        # UI Construction
        self._setup_ui()
        
        # Auto-refresh every 60 seconds
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(60000)
        
        # Initial load
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # ── Header ──
        header_layout = QHBoxLayout()
        title = QLabel("Personnel Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")
        
        self.stats_label = QLabel("Syncing...")
        self.stats_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10pt;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)
        layout.addLayout(header_layout)

        # ── Filter Bar ──
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(12)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by name or employee ID...")
        self.search_box.textChanged.connect(self.apply_filters)
        
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["All Status", "Active", "Suspended", "Inactive"])
        self.status_dropdown.currentTextChanged.connect(self.apply_filters)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self.load_data)

        filter_bar.addWidget(self.search_box, stretch=3)
        filter_bar.addWidget(self.status_dropdown, stretch=1)
        filter_bar.addWidget(refresh_btn)
        layout.addLayout(filter_bar)

        # ── Personnel Grid ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(16)
        self.grid.setContentsMargins(0, 0, 0, 0)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def load_data(self):
        """Fetch workers from APIClient"""
        try:
            self.all_workers = APIClient.get_workers()
            active_count = len([w for w in self.all_workers if w.get('status') == 'active'])
            self.stats_label.setText(f"Total: {len(self.all_workers)} | Active: {active_count}")
            self.apply_filters()
        except Exception as e:
            self.stats_label.setText("⚠️ Connection Error")
            print(f"API Fetch Error: {e}")

    def apply_filters(self):
        """Perform client-side filtering on the cached worker list"""
        query = self.search_box.text().lower()
        status_filter = self.status_dropdown.currentText().lower()

        filtered = []
        for worker in self.all_workers:
            name = worker.get('full_name', '').lower()
            code = worker.get('employee_code', '').lower()
            status = worker.get('status', '').lower()

            if query and (query not in name and query not in code):
                continue
            if status_filter != "all status" and status != status_filter:
                continue
            filtered.append(worker)
        
        self._render_cards(filtered)

    def _render_cards(self, workers):
        """Rebuild the card grid"""
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, worker in enumerate(workers):
            card = self._create_worker_card(worker)
            self.grid.addWidget(card, i // 3, i % 3)

        # Push items to the top
        self.grid.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), 
                          (len(workers) // 3) + 1, 0)

    def _create_worker_card(self, worker: dict) -> Card:
        """Constructs an individual worker card"""
        name = worker.get('full_name', 'Unknown')
        code = worker.get('employee_code', 'N/A')
        status = worker.get('status', 'inactive').capitalize()
        
        card = Card(name)
        vbox = QVBoxLayout()
        
        details = QLabel(f"ID: {code}\nDept: {worker.get('department', 'N/A')}\nStatus: {status}")
        details.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt; line-height: 140%;")
        vbox.addWidget(details)
        
        btn_action = QPushButton("Toggle Status")
        btn_action.setCursor(Qt.PointingHandCursor)
        btn_action.clicked.connect(lambda: self._handle_toggle(code))
        vbox.addWidget(btn_action)
        
        card.content_layout.addLayout(vbox)
        return card

    def _handle_toggle(self, code):
        """Communicate status change to API and refresh UI"""
        try:
            APIClient.toggle_worker_status(code)
            self.load_data()
        except Exception as e:
            QMessageBox.warning(self, "Action Failed", f"Could not update status: {e}")