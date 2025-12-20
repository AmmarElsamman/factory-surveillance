"""
Navigation bar for the application
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.utils.styles import COLORS


class NavigationBar(QWidget):
    """Left sidebar navigation"""
    navigation_changed = Signal(int)
    
    # These indices MUST match the order of widgets added to your QStackedWidget
    MENU_ITEMS = [
        ("🏠 Dashboard", 0),
        ("📹 Live Monitor", 1),
        ("🤖 AI Detection", 2),  # New AI Tab
        ("⏱️ Helmet", 3),
        ("⏱️ Playback", 4),      # Playback remains, now at index 3
        ("🚨 Alerts", 5),
        ("👥 People", 6),
        ("🚪 Access Control", 7),
        ("📊 Analytics", 8),
        ("🎥 Cameras", 9),
        ("📋 Reports", 10),
        ("⚙️ Settings", 11),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['primary']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header / Brand Label
        header = QLabel("S3S SYSTEM")
        header_font = QFont("Segoe UI", 14, QFont.Bold)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"padding: 25px; color: {COLORS['accent']}; border: none;")
        layout.addWidget(header)
        
        # Container for buttons to handle spacing
        self.buttons = []
        for label, index in self.MENU_ITEMS:
            btn = QPushButton(label)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            
            # Connect signal: checked is ignored, idx is passed to the handler
            btn.clicked.connect(lambda checked=False, idx=index: self._on_menu_click(idx))
            layout.addWidget(btn)
            self.buttons.append(btn)
        
        # Pushes buttons to the top
        layout.addStretch()
        
        # Set initial active state (Dashboard)
        self._set_active_button(0)
    
    def _on_menu_click(self, index):
        """Handle sidebar button clicks"""
        self._set_active_button(index)
        self.navigation_changed.emit(index)
    
    def _set_active_button(self, index):
        """Apply styling to the currently selected button"""
        for btn_idx, btn in enumerate(self.buttons):
            # Map the iteration index back to the MENU_ITEMS index
            actual_item_index = self.MENU_ITEMS[btn_idx][1]
            
            if actual_item_index == index:
                # Active Button Style
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['accent']};
                        color: {COLORS['dark']};
                        border: none;
                        border-left: 4px solid #FFFFFF;
                        text-align: left;
                        padding-left: 20px;
                        font-weight: bold;
                    }}
                """)
            else:
                # Normal Button Style
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLORS['text']};
                        border: none;
                        text-align: left;
                        padding-left: 24px;
                        font-weight: normal;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['secondary']};
                    }}
                """)