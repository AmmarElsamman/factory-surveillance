"""
Devices view - Camera inventory and management (API-Driven)
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                               QAbstractItemView, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

from utils.styles import COLORS
from components.cards import Card
from api_client import APIClient

class DevicesWidget(QWidget):
    """Camera and device inventory management"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # ── Header ──
        header_layout = QHBoxLayout()
        header = QLabel("Camera Inventory")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_layout.addWidget(header)
        
        self.stats_label = QLabel("Loading cameras...")
        self.stats_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)
        main_layout.addLayout(header_layout)
        
        # ── Table Card ──
        table_card = Card()
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Location", "Status", "Actions"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        
        # Style the header
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 120)
        
        table_layout.addWidget(self.table)
        table_card.add_content(QWidget()) # Access Card's internal layout
        table_card.content_layout.addLayout(table_layout)
        main_layout.addWidget(table_card)
        
        # ── Footer Actions ──
        footer_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Refresh List")
        btn_refresh.setMinimumHeight(40)
        btn_refresh.clicked.connect(self.load_cameras)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_refresh)
        main_layout.addLayout(footer_layout)

        # Auto-refresh every 30 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_cameras)
        self.timer.start(30000)
        
        QTimer.singleShot(0, self.load_cameras)

    def load_cameras(self):
        """Fetch cameras from API and populate table"""
        try:
            cameras = APIClient.get_cameras()
            print(f"DEBUG: Found {len(cameras)} cameras")
            self.populate_table(cameras)
            self.update_stats(cameras)
        except Exception as e:
            self.stats_label.setText("⚠️ Connection Error")
            print(f"Device Fetch Error: {e}")

    def update_stats(self, cameras):
        total = len(cameras)
        online = len([c for c in cameras if c.get('status') == 'online'])
        self.stats_label.setText(f"Online: {online} / Total: {total}")


    def populate_table(self, cameras):
        # 1. Clear and reset row count
        self.table.setRowCount(0)
        self.table.setRowCount(len(cameras))
        
        for i, cam in enumerate(cameras):
            # ID, Name, Location
            self.table.setItem(i, 0, QTableWidgetItem(str(cam.get('camera_id', 'N/A'))))
            self.table.setItem(i, 1, QTableWidgetItem(cam.get('ip_address', 'Unknown')))
            self.table.setItem(i, 2, QTableWidgetItem(cam.get('location_name', 'General')))
            
            # 2. Fix: Wrap hex string in QColor
            status_raw = cam.get('status', 'offline').lower()
            status_item = QTableWidgetItem(status_raw.upper())
            
            hex_color = COLORS['success'] if status_raw == 'online' else COLORS['danger']
            status_item.setForeground(QColor(hex_color)) # Conversion happens here
            
            self.table.setItem(i, 3, status_item)
            
            # 3. Action Button with safe closure
            btn_manage = QPushButton("Settings")
            btn_manage.setCursor(Qt.PointingHandCursor)
            btn_manage.setStyleSheet(f"background: {COLORS['surface_alt']}; font-size: 8pt;")
            
            # Safe lambda capture using default arguments
            btn_manage.clicked.connect(lambda checked=False, c=cam: self.show_details(c))
            
            self.table.setCellWidget(i, 4, btn_manage)

    def show_details(self, camera):
        QMessageBox.information(self, "Camera Info", 
                                f"Camera: {camera.get('name')}\n"
                                f"Source: {camera.get('source_url', 'N/A')}\n"
                                f"Resolution: {camera.get('resolution', '1080p')}")