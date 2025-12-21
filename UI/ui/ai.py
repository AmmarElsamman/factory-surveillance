import cv2
import numpy as np
import time
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap

class AIWorker(QThread):
    """Worker thread to handle heavy AI processing without freezing the UI"""
    frame_ready = Signal(QImage, list)

    def __init__(self, ai_system):
        super().__init__()
        self.ai_system = ai_system
        self.running = False
        self.is_paused = False
        self.camera_index = 0  # Default to 0

    def set_camera(self, index):
        """Update the camera index before starting the thread"""
        self.camera_index = index

    def run(self):
        self.running = True
        # Open camera based on the index selected in the UI
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while self.running:
            if self.is_paused:
                time.sleep(0.1) 
                continue

            ret, frame = self.cap.read()
            if not ret:
                continue

            # Process through your AttendanceSystem logic
            processed_frame, results = self.ai_system.process_frame(frame)

            # Convert BGR to RGB for Qt
            rgb_image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            qt_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
            
            # Send the frame back to the UI thread
            self.frame_ready.emit(qt_img, results)

        self.cap.release()

    def stop(self):
        self.running = False
        self.wait()

class AIWidget(QWidget):
    """The actual Tab widget that will appear in your UI"""
    def __init__(self, ai_system_instance):
        super().__init__()
        self.ai_system_instance = ai_system_instance
        self.layout = QVBoxLayout(self)
        
        # 1. Header & Camera Selection Row
        header_layout = QHBoxLayout()
        self.header = QLabel("AI REAL-TIME ATTENDANCE SYSTEM")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: #00d4ff;")
        header_layout.addWidget(self.header)
        
        header_layout.addStretch()
        
        # Camera Dropdown Menu
        self.cam_label = QLabel("Camera Source:")
        self.cam_label.setStyleSheet("color: white; font-weight: bold;")
        self.cam_select = QComboBox()
        self.cam_select.addItems(["Camera 0 (Internal)", "Camera 1 (DroidCam/USB)"])
        self.cam_select.setFixedWidth(200)
        self.cam_select.setStyleSheet("""
            QComboBox {
                background-color: #333;
                color: white;
                border: 1px solid #00d4ff;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        
        header_layout.addWidget(self.cam_label)
        header_layout.addWidget(self.cam_select)
        self.layout.addLayout(header_layout)

        # 2. Video Display Area
        self.video_container = QLabel("Stream Stopped")
        self.video_container.setMinimumSize(800, 600)
        self.video_container.setStyleSheet("""
            background-color: #000000; 
            border: 2px solid #333; 
            border-radius: 10px;
            color: #555;
            font-size: 18px;
        """)
        self.video_container.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.video_container, 1)

        # 3. Control Buttons Layout
        self.controls_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("▶ Start")
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_stop = QPushButton("⏹ Stop")
        
        button_style = "padding: 12px; font-weight: bold; font-size: 14px; min-width: 120px; border-radius: 5px;"
        self.btn_start.setStyleSheet(button_style + "background-color: #2e7d32; color: white;")
        self.btn_pause.setStyleSheet(button_style + "background-color: #f9a825; color: black;")
        self.btn_stop.setStyleSheet(button_style + "background-color: #c62828; color: white;")
        
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        
        self.controls_layout.addWidget(self.btn_start)
        self.controls_layout.addWidget(self.btn_pause)
        self.controls_layout.addWidget(self.btn_stop)
        self.layout.addLayout(self.controls_layout)

        # 4. Status Bar
        self.status_box = QLabel("System Ready")
        self.status_box.setStyleSheet("color: #aaa; font-weight: bold; padding: 10px; background: #222; border-radius: 5px;")
        self.layout.addWidget(self.status_box)

        # 5. Initialize Worker
        self.worker = AIWorker(self.ai_system_instance)
        self.worker.frame_ready.connect(self.update_ui)

        # Connect Button Signals
        self.btn_start.clicked.connect(self.start_attendance)
        self.btn_pause.clicked.connect(self.pause_attendance)
        self.btn_stop.clicked.connect(self.stop_attendance)

    def start_attendance(self):
        if not self.worker.isRunning():
            # Get selected index from dropdown (0 or 1)
            selected_cam = self.cam_select.currentIndex()
            self.worker.set_camera(selected_cam)
            
            self.worker.is_paused = False
            self.worker.start()
            self.cam_select.setEnabled(False) # Lock selection while running
            self.status_box.setText(f"System: Initializing Camera {selected_cam}...")
            self.status_box.setStyleSheet("color: #00ff00; font-weight: bold; padding: 10px; background: #222;")
        else:
            self.worker.is_paused = False # Resume logic
            self.status_box.setText("System: Resumed")
        
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)

    def pause_attendance(self):
        self.worker.is_paused = True
        self.btn_start.setEnabled(True)
        self.btn_start.setText("▶ Resume")
        self.btn_pause.setEnabled(False)
        self.status_box.setText("System: Paused")
        self.status_box.setStyleSheet("color: #f9a825; font-weight: bold; padding: 10px; background: #222;")

    def stop_attendance(self):
        self.worker.stop()
        self.cam_select.setEnabled(True) # Unlock selection
        self.video_container.clear()
        self.video_container.setText("Stream Stopped")
        self.status_box.setText("System: Stopped")
        self.status_box.setStyleSheet("color: #c62828; font-weight: bold; padding: 10px; background: #222;")
        
        self.btn_start.setEnabled(True)
        self.btn_start.setText("▶ Start")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)

    @Slot(QImage, list)
    def update_ui(self, qt_image, results):
        pixmap = QPixmap.fromImage(qt_image)
        self.video_container.setPixmap(pixmap.scaled(
            self.video_container.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        if results:
            self.status_box.setText(f"System: Active - Detecting {len(results)} faces")

    def closeEvent(self, event):
        self.worker.stop()
        super().closeEvent(event)