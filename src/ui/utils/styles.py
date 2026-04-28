"""
Styles and themes for the Surveillance & Security System
Dark professional palette suited for monitoring dashboards
"""

COLORS = {
    # Backgrounds
    'dark':            '#0D1117',   # Deep dark — main background
    'surface':         '#161B22',   # Slightly lighter — cards, panels
    'surface_alt':     '#1C2128',   # Hover states, alternate rows

    # Accent
    'accent':          '#00B4D8',   # Cyan blue — highlights, active states
    'accent_dim':      '#0077A8',   # Darker cyan — hover on accent

    # Semantic
    'success':         '#3FB950',   # Green — active, compliant, online
    'warning':         '#D29922',   # Amber — warnings, on leave
    'danger':          '#F85149',   # Red — alerts, violations, offline
    'info':            '#58A6FF',   # Blue — informational

    # Text
    'text':            '#E6EDF3',   # Primary white text
    'text_secondary':  '#8B949E',   # Muted grey text
    'text_disabled':   '#484F58',   # Disabled text

    # Borders & Glass
    'border':          '#30363D',   # Subtle border
    'card_bg':         '#161B22',   # Card background
    'glass':           'rgba(255, 255, 255, 0.04)',  # Glass overlay
}


def apply_main_stylesheet(widget):
    """Apply dark surveillance dashboard stylesheet"""
    widget.setStyleSheet(f"""
        /* ── Base ── */
        * {{
            color: {COLORS['text']};
            font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
            outline: none;
        }}

        QMainWindow, QWidget {{
            background-color: {COLORS['dark']};
            color: {COLORS['text']};
        }}

        /* ── Scroll Bars ── */
        QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {COLORS['border']};
            border-radius: 3px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {COLORS['text_secondary']};
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        QScrollBar:horizontal {{
            background: transparent;
            height: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: {COLORS['border']};
            border-radius: 3px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {COLORS['text_secondary']};
        }}

        /* ── Buttons ── */
        QPushButton {{
            background-color: {COLORS['surface_alt']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 10pt;
        }}
        QPushButton:hover {{
            background-color: {COLORS['surface']};
            border-color: {COLORS['accent']};
            color: {COLORS['accent']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['dark']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['surface']};
            color: {COLORS['text_disabled']};
            border-color: {COLORS['border']};
        }}

        /* ── Inputs ── */
        QLineEdit, QTextEdit, QSpinBox {{
            background-color: {COLORS['surface']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 10pt;
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {COLORS['accent']};
        }}

        /* ── ComboBox ── */
        QComboBox {{
            background-color: {COLORS['surface']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 10pt;
        }}
        QComboBox:hover {{
            border-color: {COLORS['accent']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            selection-background-color: {COLORS['accent_dim']};
            color: {COLORS['text']};
        }}

        /* ── Tab Widget ── */
        QTabWidget::pane {{
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            background-color: {COLORS['surface']};
        }}
        QTabBar::tab {{
            background-color: {COLORS['surface_alt']};
            color: {COLORS['text_secondary']};
            border: 1px solid {COLORS['border']};
            padding: 8px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}
        QTabBar::tab:selected {{
            background-color: {COLORS['accent']};
            color: {COLORS['dark']};
            font-weight: bold;
            border-color: {COLORS['accent']};
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {COLORS['surface']};
            color: {COLORS['text']};
        }}

        /* ── Labels ── */
        QLabel {{
            background: transparent;
        }}

        /* ── Scroll Area ── */
        QScrollArea {{
            border: none;
            background: transparent;
        }}

        /* ── Checkbox ── */
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid {COLORS['border']};
            background-color: {COLORS['surface']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLORS['accent']};
            border-color: {COLORS['accent']};
        }}

        /* ── Table ── */
        QTableWidget {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            gridline-color: {COLORS['border']};
            font-size: 10pt;
        }}
        QTableWidget::item {{
            padding: 8px;
        }}
        QTableWidget::item:selected {{
            background-color: {COLORS['accent_dim']};
            color: {COLORS['text']};
        }}
        QHeaderView::section {{
            background-color: {COLORS['surface_alt']};
            color: {COLORS['text_secondary']};
            border: none;
            border-bottom: 1px solid {COLORS['border']};
            padding: 8px;
            font-weight: bold;
            font-size: 9pt;
        }}
    """)