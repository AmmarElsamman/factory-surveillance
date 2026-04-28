"""
Reusable card components for the Surveillance System UI
"""
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from utils.styles import COLORS


def _hex_to_rgba(hex_color: str, alpha: float = 0.2) -> str:
    """Convert hex color to rgba string"""
    c = QColor(hex_color)
    return f"rgba({c.red()}, {c.green()}, {c.blue()}, {alpha})"


class Card(QFrame):
    """
    Base card component — dark surface with border.
    Use this as a container for any page section.
    """
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        if title:
            title_label = QLabel(title)
            title_font = QFont("Segoe UI", 11)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setStyleSheet(f"color: {COLORS['text']}; background: transparent;")
            layout.addWidget(title_label)

            # Divider line under title
            divider = QFrame()
            divider.setFrameShape(QFrame.HLine)
            divider.setStyleSheet(f"border: none; border-top: 1px solid {COLORS['border']};")
            layout.addWidget(divider)

        # Public layout for subclasses and callers to add content
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout)

    def add_content(self, widget):
        """Add a widget to the card's content area"""
        self.content_layout.addWidget(widget)


class StatCard(QFrame):
    """
    Compact statistics card.
    Shows a label, a large value, and an optional status badge.

    Usage:
        StatCard("Active Workers", "8", status="success")
        StatCard("Cameras Online", "3/5", status="warning")
        StatCard("Critical Alerts", "2", status="danger")
    """

    STATUS_COLORS = {
        "success": COLORS['success'],
        "warning": COLORS['warning'],
        "danger":  COLORS['danger'],
        "info":    COLORS['info'],
        "normal":  COLORS['text_secondary'],
    }

    def __init__(self, label: str = "", value: str = "0",
                 status: str = None, parent=None):
        super().__init__(parent)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # ── Label (muted, small) ──
        label_widget = QLabel(label)
        label_widget.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent; font-size: 9pt;"
        )
        layout.addWidget(label_widget)

        # ── Value + Badge row ──
        row = QHBoxLayout()
        row.setSpacing(8)

        self.value_label = QLabel(str(value))
        value_font = QFont("Segoe UI", 22)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {COLORS['text']}; background: transparent;")
        row.addWidget(self.value_label)

        # ── Status badge (pill) ──
        if status and status in self.STATUS_COLORS:
            pill_color = self.STATUS_COLORS[status]
            badge = QLabel(status.upper())
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(f"""
                background-color: {_hex_to_rgba(pill_color, 0.15)};
                color: {pill_color};
                border: 1px solid {_hex_to_rgba(pill_color, 0.4)};
                border-radius: 8px;
                padding: 2px 10px;
                font-size: 8pt;
                font-weight: bold;
            """)
            row.addWidget(badge)

        row.addStretch()
        layout.addLayout(row)
    
    def update_value(self, text: str):
        """Update the displayed values"""
        self.value_label.setText(str(text))