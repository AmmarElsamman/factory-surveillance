"""
Sidebar navigation for the Surveillance & Security System
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from utils.styles import COLORS


class NavigationBar(QWidget):
    """Left sidebar navigation — only shows implemented pages"""

    navigation_changed = Signal(int)

    MENU_ITEMS = [
        ("🏠  Dashboard",    0),
        ("🤖  AI Detection", 1),
        ("👥  Workers",      2),
        ("🎥  Cameras",      3),
        ("🚨  Alerts",       4),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(210)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Brand header ──
        brand = QLabel("S3S SYSTEM")
        brand.setAlignment(Qt.AlignCenter)
        brand.setFont(QFont("Segoe UI", 13, QFont.Bold))
        brand.setStyleSheet(f"""
            color: {COLORS['accent']};
            padding: 24px 0px;
            background: transparent;
            border-bottom: 1px solid {COLORS['border']};
            letter-spacing: 2px;
        """)
        layout.addWidget(brand)

        # ── Nav buttons ──
        self.buttons = []
        for label, index in self.MENU_ITEMS:
            btn = QPushButton(label)
            btn.setFixedHeight(48)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(
                lambda checked=False, idx=index: self._on_click(idx)
            )
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch()

        # ── Version label at bottom ──
        version = QLabel("v0.1.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(f"color: {COLORS['text_disabled']}; font-size: 8pt; padding: 12px;")
        layout.addWidget(version)

        # Set default active
        self._set_active(0)

    def _on_click(self, index: int):
        self._set_active(index)
        self.navigation_changed.emit(index)

    def _set_active(self, index: int):
        for btn_idx, btn in enumerate(self.buttons):
            actual_index = self.MENU_ITEMS[btn_idx][1]

            if actual_index == index:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['accent']};
                        color: {COLORS['dark']};
                        border: none;
                        border-left: 4px solid white;
                        text-align: left;
                        padding-left: 20px;
                        font-weight: bold;
                        font-size: 10pt;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLORS['text_secondary']};
                        border: none;
                        border-left: 4px solid transparent;
                        text-align: left;
                        padding-left: 20px;
                        font-weight: normal;
                        font-size: 10pt;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['surface_alt']};
                        color: {COLORS['text']};
                    }}
                """)