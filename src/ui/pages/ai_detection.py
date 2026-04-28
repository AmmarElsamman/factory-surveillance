"""
AI Real-Time Detection View
"""
import cv2
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                               QPushButton, QComboBox, QFrame)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap, QFont

from utils.styles import COLORS
from components.cards import Card

class AIWorker(QThread):
    """Thread for non-blocking AI frame processing"""
    frame_ready = Signal(QImage, list)

    def __init__(self, ai_system):
        super().__init__()
        self.ai_system = ai_system
        self.running = False
        self.is_paused = False
        self.camera_index = 0  

    def set_camera(self, index):
        self.camera_index = index

    def run(self):
        self.running = True
        self.cap = cv2.VideoCapture(self.camera_index)
        
        while self.running:
            if self.is_paused:
                self.msleep(100)
                continue

            ret, frame = self.cap.read()
            if not ret: continue

            # Process AI logic
            processed_frame, results = self.ai_system.process_frame(frame)

            # Convert to Qt Format
            rgb_image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            qt_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_ready.emit(qt_img, results)

        self.cap.release()

    def stop(self):
        self.running = False
        self.wait()

class AIWidget(QWidget):
    def __init__(self, ai_system_instance, parent=None):
        super().__init__(parent)
        self.ai_system = ai_system_instance
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # ── Header ──
        header_layout = QHBoxLayout()
        header = QLabel("AI Real-Time Detection")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        self.cam_select = QComboBox()
        self.cam_select.addItems(["Internal Camera (0)", "External Source (1)"])
        self.cam_select.setFixedWidth(200)
        header_layout.addWidget(QLabel("Source:"))
        header_layout.addWidget(self.cam_select)
        main_layout.addLayout(header_layout)

        # ── Video Viewport (Inside a Card) ──
        self.video_card = Card()
        self.video_container = QLabel("Stream Stopped")
        self.video_container.setMinimumSize(800, 500)
        self.video_container.setAlignment(Qt.AlignCenter)
        self.video_container.setStyleSheet(f"background-color: {COLORS['dark']}; border-radius: 6px;")
        
        self.video_card.add_content(self.video_container)
        main_layout.addWidget(self.video_card, 1)

        # ── Controls ──
        controls_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ Start")
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_stop  = QPushButton("⏹ Stop")
        
        # Use Semantic Colors from styles.py
        self.btn_start.setStyleSheet(f"QPushButton {{ background-color: {COLORS['success']}; color: white; border: none; }}")
        self.btn_stop.setStyleSheet(f"QPushButton {{ background-color: {COLORS['danger']}; color: white; border: none; }}")
        
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        
        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_stop)
        main_layout.addLayout(controls_layout)

        # ── Status ──
        self.status_box = QLabel("System Status: Ready")
        self.status_box.setStyleSheet(f"color: {COLORS['text_secondary']}; padding: 10px;")
        main_layout.addWidget(self.status_box)

        # Worker setup
        self.worker = AIWorker(self.ai_system)
        self.worker.frame_ready.connect(self.update_ui)
        
        self.btn_start.clicked.connect(self.start_stream)
        self.btn_pause.clicked.connect(self.pause_stream)
        self.btn_stop.clicked.connect(self.stop_stream)

    def start_stream(self):
        if not self.worker.isRunning():
            self.worker.set_camera(self.cam_select.currentIndex())
            self.worker.is_paused = False
            self.worker.start()
        else:
            self.worker.is_paused = False
            
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.status_box.setText("System Status: Running")

    def pause_stream(self):
        self.worker.is_paused = True
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.status_box.setText("System Status: Paused")

    def stop_stream(self):
        self.worker.stop()
        self.video_container.clear()
        self.video_container.setText("Stream Stopped")
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.status_box.setText("System Status: Stopped")

    @Slot(QImage, list)
    def update_ui(self, qt_image, results):
        if self.worker.isRunning() and not self.worker.is_paused:
            pixmap = QPixmap.fromImage(qt_image)
            self.video_container.setPixmap(pixmap.scaled(
                self.video_container.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            if results:
                self.status_box.setText(f"System Status: Detecting {len(results)} subjects")