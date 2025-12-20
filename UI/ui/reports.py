"""
Reports view - Reporting and data export
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QCheckBox, QFrame, QDateEdit,
                               QTabWidget, QScrollArea, QGridLayout, QSpinBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from ui.utils.components import Card, ChartPlaceholder
from ui.utils.styles import COLORS


class ReportsWidget(QWidget):
    """Reports generation and export"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Header
        header = QLabel("Reports & Analytics")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        main_layout.addWidget(header)
        
        # Report filters
        filter_card = Card("Report Filters")
        
        filter_layout = QGridLayout()
        
        filter_layout.addWidget(QLabel("Report Type:"), 0, 0)
        report_combo = QComboBox()
        report_combo.addItems(["Daily", "Weekly", "Monthly", "Custom"])
        filter_layout.addWidget(report_combo, 0, 1)
        
        filter_layout.addWidget(QLabel("Start Date:"), 0, 2)
        start_date = QDateEdit()
        start_date.setDate(QDate.currentDate().addDays(-7))
        filter_layout.addWidget(start_date, 0, 3)
        
        filter_layout.addWidget(QLabel("End Date:"), 1, 2)
        end_date = QDateEdit()
        end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(end_date, 1, 3)
        
        filter_layout.addWidget(QLabel("Include:"), 1, 0)
        check_ppe = QCheckBox("PPE Compliance")
        check_ppe.setChecked(True)
        filter_layout.addWidget(check_ppe, 1, 1)
        
        filter_layout.addWidget(QLabel("Site:"), 2, 0)
        site_combo = QComboBox()
        site_combo.addItems(["All Sites", "Site A", "Site B", "Site C"])
        filter_layout.addWidget(site_combo, 2, 1)
        
        check_access = QCheckBox("Access Summary")
        check_access.setChecked(True)
        filter_layout.addWidget(check_access, 2, 2)
        
        check_incidents = QCheckBox("Incident Trends")
        filter_layout.addWidget(check_incidents, 2, 3)
        
        filter_card.content_layout.addLayout(filter_layout)
        
        main_layout.addWidget(filter_card)
        
        # Create tabs for different report types
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget {{ background-color: {COLORS['dark']}; }}
            QTabBar::tab {{ background-color: {COLORS['secondary']}; padding: 8px 20px; color: {COLORS['text']}; }}
            QTabBar::tab:selected {{ background-color: {COLORS['accent']}; color: {COLORS['dark']}; }}
        """)
        
        # PPE Report
        ppe_scroll = QScrollArea()
        ppe_scroll.setWidgetResizable(True)
        ppe_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        ppe_container = QWidget()
        ppe_layout = QVBoxLayout(ppe_container)
        ppe_layout.setSpacing(16)
        
        ppe_layout.addWidget(ChartPlaceholder("PPE Compliance by Zone"))
        ppe_layout.addWidget(ChartPlaceholder("PPE Compliance by Shift"))
        
        ppe_stats = Card("PPE Summary Statistics")
        stats_text = QLabel(
            "Total Events Analyzed: 45,234\n"
            "Violations Detected: 523 (1.16%)\n"
            "Overall Compliance: 98.84%\n\n"
            "Zone Compliance:\n"
            "  Zone A: 99.2%\n"
            "  Zone B: 98.5%\n"
            "  Zone C: 98.1%\n"
            "  Zone D: 99.0%\n\n"
            "Trend: ✓ Improving (+2.3% last month)"
        )
        stats_text.setStyleSheet(f"color: {COLORS['text_secondary']};")
        ppe_stats.content_layout.addWidget(stats_text)
        ppe_layout.addWidget(ppe_stats)
        
        ppe_layout.addStretch()
        ppe_scroll.setWidget(ppe_container)
        tabs.addTab(ppe_scroll, "👷 PPE Compliance")
        
        # Access Report
        access_scroll = QScrollArea()
        access_scroll.setWidgetResizable(True)
        access_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        access_container = QWidget()
        access_layout = QVBoxLayout(access_container)
        access_layout.setSpacing(16)
        
        access_layout.addWidget(ChartPlaceholder("Access Events Over Time"))
        access_layout.addWidget(ChartPlaceholder("Access by Zone"))
        
        access_stats = Card("Access Summary Statistics")
        access_text = QLabel(
            "Total Access Events: 12,456\n"
            "Granted: 12,345 (99.1%)\n"
            "Denied: 111 (0.9%)\n\n"
            "Denied Reasons:\n"
            "  Invalid Credentials: 67\n"
            "  Access Outside Hours: 34\n"
            "  No Authorization: 10\n\n"
            "Average Response Time: 1.2s"
        )
        access_text.setStyleSheet(f"color: {COLORS['text_secondary']};")
        access_stats.content_layout.addWidget(access_text)
        access_layout.addWidget(access_stats)
        
        access_layout.addStretch()
        access_scroll.setWidget(access_container)
        tabs.addTab(access_scroll, "🚪 Access Summary")
        
        # Incident Report
        incident_scroll = QScrollArea()
        incident_scroll.setWidgetResizable(True)
        incident_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        incident_container = QWidget()
        incident_layout = QVBoxLayout(incident_container)
        incident_layout.setSpacing(16)
        
        incident_layout.addWidget(ChartPlaceholder("Incident Trends"))
        incident_layout.addWidget(ChartPlaceholder("Incident Distribution by Type"))
        
        incident_stats = Card("Incident Statistics")
        incident_text = QLabel(
            "Total Incidents: 1,234\n"
            "Critical: 45 (3.6%)\n"
            "Warning: 234 (19.0%)\n"
            "Info: 955 (77.4%)\n\n"
            "Top Incident Types:\n"
            "  PPE Violations: 523\n"
            "  Unknown Faces: 345\n"
            "  Intrusions: 178\n"
            "  Access Denied: 111\n\n"
            "Trend: ↓ Decreasing (-5.2% vs last month)"
        )
        incident_text.setStyleSheet(f"color: {COLORS['text_secondary']};")
        incident_stats.content_layout.addWidget(incident_text)
        incident_layout.addWidget(incident_stats)
        
        incident_layout.addStretch()
        incident_scroll.setWidget(incident_container)
        tabs.addTab(incident_scroll, "⚠️ Incidents")
        
        main_layout.addWidget(tabs, 1)
        
        # Export controls
        export_card = Card("Export Options")
        
        export_layout = QHBoxLayout()
        
        export_layout.addWidget(QLabel("Format:"))
        format_combo = QComboBox()
        format_combo.addItems(["PDF", "Excel (CSV)", "JSON", "PowerPoint"])
        export_layout.addWidget(format_combo)
        
        check_signature = QCheckBox("Digital Signature")
        export_layout.addWidget(check_signature)
        
        export_layout.addStretch()
        
        btn_preview = QPushButton("👁️ Preview")
        export_layout.addWidget(btn_preview)
        
        btn_export = QPushButton("📥 Export Report")
        btn_export.setObjectName("success")
        btn_export.setMinimumWidth(150)
        export_layout.addWidget(btn_export)
        
        btn_schedule = QPushButton("📅 Schedule")
        export_layout.addWidget(btn_schedule)
        
        export_card.content_layout.addLayout(export_layout)
        main_layout.addWidget(export_card)
