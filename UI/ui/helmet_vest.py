import cv2
import time
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from person_helmet.logic import HelmetVestEngine

class HelmetWorker(QThread):
    frame_ready = Signal(QImage, int, float)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.running = False
        self.is_paused = False

    def run(self):
        self.running = True
        # Use Index 1 for DroidCam
        cap = cv2.VideoCapture(0) 
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        prev_time = time.time()
        frame_count = 0
        fps = 0

        while self.running:
            if self.is_paused:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret:
                continue

            # FPS Calculation
            frame_count += 1
            if frame_count % 10 == 0:
                curr_time = time.time()
                fps = 10 / (curr_time - prev_time)
                prev_time = curr_time

            # Process frame using the engine logic
            processed_frame, count = self.engine.process_frame(frame)
            
            # Convert BGR to RGB for Qt display
            rgb_img = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_img.shape
            qt_img = QImage(rgb_img.data, w, h, ch * w, QImage.Format_RGB888)
            
            self.frame_ready.emit(qt_img, count, fps)

        cap.release()

    def stop(self):
        self.running = False
        self.wait()

class HelmetVestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.engine = HelmetVestEngine()
        
        # 1. Video Display
        self.video_label = QLabel("Stream Stopped")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background: black; border-radius: 10px; border: 2px solid #333; color: white; font-size: 18px;")
        
        # 2. Stats Display
        self.stats_label = QLabel("Persons: 0 | FPS: 0.0")
        self.stats_label.setStyleSheet("font-size: 18px; color: #00ff00; font-weight: bold; padding: 10px;")
        
        # 3. Control Buttons
        self.controls_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("▶ Start")
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_stop = QPushButton("⏹ Stop")
        
        # Styling buttons
        button_style = "padding: 10px; font-weight: bold; font-size: 14px; min-width: 100px;"
        self.btn_start.setStyleSheet(button_style + "background-color: #2e7d32; color: white;")
        self.btn_pause.setStyleSheet(button_style + "background-color: #f9a825; color: black;")
        self.btn_stop.setStyleSheet(button_style + "background-color: #c62828; color: white;")
        
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        
        self.controls_layout.addWidget(self.btn_start)
        self.controls_layout.addWidget(self.btn_pause)
        self.controls_layout.addWidget(self.btn_stop)
        self.controls_layout.setAlignment(Qt.AlignCenter)

        # Build Layout
        self.layout.addWidget(self.video_label, 1)
        self.layout.addWidget(self.stats_label)
        self.layout.addLayout(self.controls_layout)
        
        # Worker Setup (Initially not running)
        self.worker = HelmetWorker(self.engine)
        self.worker.frame_ready.connect(self.update_ui)
        
        # Connect Buttons
        self.btn_start.clicked.connect(self.start_stream)
        self.btn_pause.clicked.connect(self.pause_stream)
        self.btn_stop.clicked.connect(self.stop_stream)

    def start_stream(self):
        if not self.worker.isRunning():
            self.worker.is_paused = False
            self.worker.start()
            self.video_label.setText("Initializing Camera...")
        else:
            self.worker.is_paused = False # Resume if it was paused
        
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)

    def pause_stream(self):
        self.worker.is_paused = True
        self.btn_start.setEnabled(True)
        self.btn_start.setText("▶ Resume")
        self.btn_pause.setEnabled(False)

    def stop_stream(self):
        self.worker.stop()
        self.video_label.clear()
        self.video_label.setText("Stream Stopped")
        self.stats_label.setText("Persons: 0 | FPS: 0.0")
        
        self.btn_start.setEnabled(True)
        self.btn_start.setText("▶ Start")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)

    @Slot(QImage, int, float)
    def update_ui(self, img, count, fps):
        self.video_label.setPixmap(QPixmap.fromImage(img).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.stats_label.setText(f"Persons Detected: {count} | System FPS: {fps:.1f}")

    def closeEvent(self, event):
        self.worker.stop()
        super().closeEvent(event)