"""
Main application entry point - Clean API-Driven Architecture
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt

# UI Imports
from components.navigation import NavigationBar
from pages.dashboard import DashboardWidget
from pages.workers import WorkersWidget
from pages.devices import DevicesWidget
from pages.ai_detection import AIWidget
from utils.styles import apply_main_stylesheet
import sys
import os

# Adds the 'src' directory to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from cv.detection.attendance_system import AttendanceSystem # Now this will work

# AI Engine Import
# try:
#     from ..cv.detection.attendance_system import AttendanceSystem
# except ImportError:
#     # Fallback/Mock for environment testing
#     print("WARNING: Faild import of AttendanceSystem")
#     class AttendanceSystem:
#         def process_frame(self, frame): return frame, []

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Surveillance & Security System")
        self.resize(1400, 900)

        # 1. Initialize AI System (used by the AI Detection page)
        self.ai_system = AttendanceSystem()

        # 2. Apply Global Stylesheet (from styles.py)
        apply_main_stylesheet(self)

        # 3. Main Layout Setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar Navigation ──
        self.nav_bar = NavigationBar()
        main_layout.addWidget(self.nav_bar)

        # ── Content Area (Stacked Pages) ──
        self.pages = QStackedWidget()
        
        # Instantiate updated modules
        self.dashboard = DashboardWidget()
        self.ai_detection = AIWidget(self.ai_system)
        self.people = WorkersWidget()
        self.devices = DevicesWidget()

        # Add to stack (Indices must match NavigationBar button order)
        # Assuming: 0: Dashboard, 1: AI, 2: People, 3: Devices
        self.pages.addWidget(self.dashboard)    # Index 0
        self.pages.addWidget(self.ai_detection) # Index 1
        self.pages.addWidget(self.people)       # Index 2
        self.pages.addWidget(self.devices)      # Index 3
        
        main_layout.addWidget(self.pages, 1)

        # 4. Connect Navigation Signals
        self.nav_bar.navigation_changed.connect(self.on_navigation_changed)
        
        # Set default page
        self.pages.setCurrentIndex(0)

    def on_navigation_changed(self, index):
        """Switches the view when sidebar items are clicked"""
        if index < self.pages.count():
            self.pages.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())