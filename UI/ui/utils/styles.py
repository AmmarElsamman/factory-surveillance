"""
Styles and themes for the application
"""
from PySide6.QtGui import QColor


# Color Palette
COLORS = {
    'primary': '#1e3a5f',      # Deep blue
    'secondary': '#2a5a8f',     # Medium blue
    'accent': '#ff6b6b',        # Red (alerts)
    'success': '#51cf66',       # Green
    'warning': '#ffd93d',       # Yellow
    'danger': '#ff6b6b',        # Red
    'dark': '#0a0e27',          # Dark background
    'light': '#f0f2f5',         # Light background
    'text': '#ffffff',          # White text
    'text_secondary': '#b0bec5', # Secondary text
    'card_bg': '#1a2a47',       # Card background
    'border': '#2a4a6f',        # Border color
}


def apply_main_stylesheet(widget):
    """Apply main stylesheet to the application"""
    stylesheet = f"""
    * {{
        color: {COLORS['text']};
    }}
    
    QMainWindow {{
        background-color: {COLORS['dark']};
    }}
    
    QWidget {{
        background-color: {COLORS['dark']};
        color: {COLORS['text']};
    }}
    
    QScrollBar:vertical {{
        background-color: {COLORS['dark']};
        width: 12px;
        border: none;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['secondary']};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['accent']};
    }}
    
    QScrollBar:horizontal {{
        background-color: {COLORS['dark']};
        height: 12px;
        border: none;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['secondary']};
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QPushButton {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['accent']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['primary']};
    }}
    
    QPushButton#danger {{
        background-color: {COLORS['danger']};
    }}
    
    QPushButton#success {{
        background-color: {COLORS['success']};
    }}
    
    QLineEdit, QTextEdit, QSpinBox, QComboBox {{
        background-color: {COLORS['card_bg']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 2px solid {COLORS['accent']};
    }}
    
    QLabel {{
        color: {COLORS['text']};
    }}
    
    QCheckBox, QRadioButton {{
        color: {COLORS['text']};
        spacing: 5px;
    }}
    
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 3px;
        border: 1px solid {COLORS['border']};
        background-color: {COLORS['card_bg']};
    }}
    
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background-color: {COLORS['accent']};
        border: 1px solid {COLORS['accent']};
    }}
    
    QComboBox::drop-down {{
        border: none;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        width: 0px;
    }}
    """
    
    widget.setStyleSheet(stylesheet)
