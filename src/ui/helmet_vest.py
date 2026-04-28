import cv2
import time
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QComboBox
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap

# Load helmet and vest detection module
from person_helmet.logic import HelmetVestEngine

class HelmetWorker(QThread):
    frame_ready = Signal(QImage, int, float)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.running = False
        self.is_paused = False
        self.camera_index = 1

    def set_camera_index(self, index):
        self.camera_index = index

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index) 
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

            frame_count += 1
            if frame_count % 10 == 0:
                curr_time = time.time()
                fps = 10 / (curr_time - prev_time)
                prev_time = curr_time

            processed_frame, count = self.engine.process_frame(frame)
            
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
        
        # --- 1. Camera Selection Row ---
        self.cam_layout = QHBoxLayout()
        self.cam_label = QLabel("Camera Source:")
        self.cam_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        
        self.cam_combo = QComboBox()
        self.cam_combo.addItems(["Camera 0 (Internal)", "Camera 1 (External)", "Camera 2 (USB)"])
        self.cam_combo.setCurrentIndex(1)
        self.cam_combo.setStyleSheet("""
            QComboBox {
                background-color: #333;
                color: white;
                border: 1px solid #00ff00;
                padding: 5px;
                border-radius: 3px;
                min-width: 200px;
            }
            QComboBox:disabled {
                background-color: #1a1a1a;
                color: #666;
                border: 1px solid #333;
            }
        """)
        
        self.cam_layout.addWidget(self.cam_label)
        self.cam_layout.addWidget(self.cam_combo)
        self.cam_layout.addStretch()
        self.layout.addLayout(self.cam_layout)

        # --- 2. Video Display ---
        self.video_label = QLabel("Stream Stopped")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.video_label.setMinimumSize(640, 480) 
        self.set_video_label_style(active=False)
        self.layout.addWidget(self.video_label, 1)
        
        # --- 3. Stats Display ---
        self.stats_label = QLabel("Persons: 0 | FPS: 0.0")
        self.stats_label.setStyleSheet("font-size: 18px; color: #00ff00; font-weight: bold; padding: 10px;")
        self.layout.addWidget(self.stats_label)
        
        # --- 4. Control Buttons ---
        self.controls_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ Start")
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_stop = QPushButton("⏹ Stop")
        
        # Apply Enhanced Styles
        self.apply_button_styles()
        
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        
        self.controls_layout.addWidget(self.btn_start)
        self.controls_layout.addWidget(self.btn_pause)
        self.controls_layout.addWidget(self.btn_stop)
        self.controls_layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(self.controls_layout)
        
        # Worker Setup
        self.worker = HelmetWorker(self.engine)
        self.worker.frame_ready.connect(self.update_ui)
        
        # Connect Buttons
        self.btn_start.clicked.connect(self.start_stream)
        self.btn_pause.clicked.connect(self.pause_stream)
        self.btn_stop.clicked.connect(self.stop_stream)

    def set_video_label_style(self, active=True):
        """Helper to toggle the appearance of the video placeholder"""
        color = "white" if active else "#555"
        self.video_label.setStyleSheet(f"""
            QLabel {{
                background: black; 
                border-radius: 10px; 
                border: 2px solid #333; 
                color: {color}; 
                font-size: 18px;
            }}
        """)

    def apply_button_styles(self):
        """Adds hover and pressed states for feedback"""
        common = "padding: 10px; font-weight: bold; font-size: 14px; min-width: 100px; border-radius: 5px;"
        
        self.btn_start.setStyleSheet(f"""
            QPushButton {{ {common} background-color: #2e7d32; color: white; }}
            QPushButton:hover {{ background-color: #388e3c; }}
            QPushButton:pressed {{ background-color: #1b5e20; }}
            QPushButton:disabled {{ background-color: #1a331c; color: #555; }}
        """)
        
        self.btn_pause.setStyleSheet(f"""
            QPushButton {{ {common} background-color: #f9a825; color: black; }}
            QPushButton:hover {{ background-color: #fbc02d; }}
            QPushButton:pressed {{ background-color: #f57f17; }}
            QPushButton:disabled {{ background-color: #443a1a; color: #555; }}
        """)
        
        self.btn_stop.setStyleSheet(f"""
            QPushButton {{ {common} background-color: #c62828; color: white; }}
            QPushButton:hover {{ background-color: #d32f2f; }}
            QPushButton:pressed {{ background-color: #b71c1c; }}
            QPushButton:disabled {{ background-color: #3d1a1a; color: #555; }}
        """)

    def start_stream(self):
        if not self.worker.isRunning():
            selected_index = self.cam_combo.currentIndex()
            self.worker.set_camera_index(selected_index)
            self.worker.is_paused = False
            self.worker.start()
            self.cam_combo.setEnabled(False)
            self.video_label.setText(f"Initializing Camera {selected_index}...")
            self.set_video_label_style(active=True)
        else:
            self.worker.is_paused = False 
        
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.btn_start.setText("▶ Start")

    def pause_stream(self):
        self.worker.is_paused = True
        self.btn_start.setEnabled(True)
        self.btn_start.setText("▶ Resume")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def stop_stream(self):
        if self.worker.isRunning():
            self.worker.stop()
        
        # CRITICAL: Clear the last frame and show the default text
        self.video_label.setPixmap(QPixmap()) # This removes the frozen image
        self.video_label.setText("Stream Stopped")
        self.set_video_label_style(active=False)
        
        self.stats_label.setText("Persons: 0 | FPS: 0.0")
        self.cam_combo.setEnabled(True)
        
        # Reset button states
        self.btn_start.setEnabled(True)
        self.btn_start.setText("▶ Start")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.worker.is_paused = False

    @Slot(QImage, int, float)
    def update_ui(self, img, count, fps):
        # We only update the Pixmap if the worker is actually running and not paused
        if self.worker.isRunning() and not self.worker.is_paused:
            pix = QPixmap.fromImage(img)
            self.video_label.setPixmap(pix.scaled(
                self.video_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            self.stats_label.setText(f"Persons Detected: {count} | System FPS: {fps:.1f}")

    def closeEvent(self, event):
        self.worker.stop()
        super().closeEvent(event)