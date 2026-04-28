"""
Main application entry point for the Surveillance & Security System UI
"""
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QIcon, QFont, QColor, QLinearGradient, QPalette

# UI Imports
from ui.navigation import NavigationBar
from ui.dashboard import DashboardWidget
from ui.live_monitor import LiveMonitorWidget
from ui.playback import PlaybackWidget
from ui.alerts import AlertsWidget
from ui.people import PeopleWidget
from ui.access_control import AccessControlWidget
from ui.analytics import AnalyticsWidget
from ui.devices import DevicesWidget
from ui.reports import ReportsWidget
from ui.admin_settings import AdminSettingsWidget
from ui.utils.styles import apply_main_stylesheet

# New Tab Imports
from ui.ai import AIWidget
from ui.helmet_vest import HelmetVestWidget

# Load AI face detection module
try:
    from cv.detection.detection_system import AttendanceSystem
except ImportError as e:
    print(f"CRITICAL: Failed to import face_detection.main. Error: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Surveillance & Security System")
        self.setGeometry(100, 100, 1920, 1080)
        
        # Initialize the AI Attendance Engine once to share memory
        self.ai_engine = AttendanceSystem()
        
        apply_main_stylesheet(self)
        
        # Central Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar Navigation
        self.nav_bar = NavigationBar()
        main_layout.addWidget(self.nav_bar)
        
        # Main Content Area (Stacked Widget)
        self.pages = QStackedWidget()
        
        # 2. Instantiate all Tab Widgets
        self.dashboard = DashboardWidget()
        self.live_monitor = LiveMonitorWidget()
        self.ai_attendance = AIWidget(self.ai_engine) 
        self.helmet_vest = HelmetVestWidget()  
        self.playback = PlaybackWidget()
        self.alerts = AlertsWidget()
        self.people = PeopleWidget()
        self.access_control = AccessControlWidget()
        self.analytics = AnalyticsWidget()
        self.devices = DevicesWidget()
        self.reports = ReportsWidget()
        self.admin_settings = AdminSettingsWidget()
        
        # 3. Add to stacked widget (INDICES MUST MATCH navigation.py MENU_ITEMS)
        self.pages.addWidget(self.dashboard)       # Index 0
        self.pages.addWidget(self.live_monitor)    # Index 1
        self.pages.addWidget(self.ai_attendance)   # Index 2
        self.pages.addWidget(self.helmet_vest)     # Index 3
        self.pages.addWidget(self.playback)        # Index 4
        self.pages.addWidget(self.alerts)          # Index 5
        self.pages.addWidget(self.people)          # Index 6
        self.pages.addWidget(self.access_control)  # Index 7
        self.pages.addWidget(self.analytics)       # Index 8
        self.pages.addWidget(self.devices)         # Index 9
        self.pages.addWidget(self.reports)         # Index 10
        self.pages.addWidget(self.admin_settings)  # Index 11
        
        main_layout.addWidget(self.pages, 1)
        
        # Connect navigation signals
        self.nav_bar.navigation_changed.connect(self.on_navigation_changed)
        
        # Set Default Page
        self.pages.setCurrentIndex(0)
        
        # Time Display Logic
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
    
    def on_navigation_changed(self, page_index):
        """Switches the view when a nav button is clicked"""
        self.pages.setCurrentIndex(page_index)
    
    def update_time(self):
        """Updates internal time reference"""
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()