"""
Styles and themes for the application based on the Horizon Homes UI
"""
from PySide6.QtGui import QColor

# Color Palette extracted accurately from the image
COLORS = {
    'primary': "#4A4A4A",        # Vibrant Orange (Buttons/Highlights)
    'secondary': "#4A4A4A",      # Muted Grey (Search/Inactive)
    'accent': '#FACC15',         # Accent matches primary orange
    'success': '#4ADE80',        # Bright Green (Trend up)
    'warning': '#FACC15',        # Yellow
    'danger': '#F87171',         # Red (Trend down)
    'dark': "#1E1E1E",           # Deep dark background
    'light': '#FFFFFF',          # Pure White
    'text': '#FFFFFF',           # Main White text
    'text_secondary': '#A3A3A3', # Muted grey text
    'card_bg': "rgba(255, 255, 255, 0.05)", # Transparent Glass effect
    'border': "rgba(255, 255, 255, 0.1)",   # Subtle glass edge
}

def apply_main_stylesheet(widget):
    """Apply Glassmorphism Horizon Homes stylesheet"""
    
    stylesheet = f"""
    /* General Text Styling */
    * {{
        color: {COLORS['text']};
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        outline: none;
    }}
    
    /* Main Background - Using a slight gradient for depth */
    QMainWindow, QWidget {{
        background-color: {COLORS['dark']};
        color: {COLORS['text']};
    }}

    /* Sidebar and Navigation (assuming it's a QFrame or similar) */
    QFrame#navigation {{
        background-color: rgba(0, 0, 0, 0.2);
        border-right: 1px solid {COLORS['border']};
    }}
    
    /* ScrollBar Styling - Slim and modern */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 8px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: rgba(255, 255, 255, 0.2);
    }}
    
    /* Buttons - Glass and Orange styles */
    QPushButton {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 600;
    }}
    
    /* Target the Orange buttons specifically */
    QPushButton#primary, QPushButton#success_action {{
        background-color: {COLORS['primary']};
        border: none;
    }}
    
    QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.15);
    }}
    
    QPushButton#primary:hover {{
        background-color: #FF8562;
    }}
    
    /* Search Bars / Inputs */
    QLineEdit, QTextEdit, QSpinBox, QComboBox {{
        background-color: rgba(255, 255, 255, 0.07);
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 10px;
    }}
    
    QLineEdit:focus {{
        border: 1px solid {COLORS['primary']};
        background-color: rgba(255, 255, 255, 0.1);
    }}
    
    /* The Glass Card Effect */
    QFrame#card, QFrame[objectName^="card"] {{
        background-color: {COLORS['card_bg']};
        border-radius: 18px;
        border: 1px solid {COLORS['border']};
    }}
    
    /* Labels */
    QLabel {{
        background: transparent;
    }}
    
    QLabel#value {{
        font-size: 24px;
        font-weight: bold;
    }}

    /* Checkbox indicators */
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 5px;
        border: 1px solid {COLORS['border']};
        background-color: rgba(255, 255, 255, 0.05);
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary']};
        border: 1px solid {COLORS['primary']};
    }}
    """
    
    widget.setStyleSheet(stylesheet)