"""
Admin/Settings view - System configuration and management
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QLineEdit, QCheckBox, QFrame,
                               QTabWidget, QScrollArea, QSpinBox, QTableWidget,
                               QTableWidgetItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.utils.components import Card
from ui.utils.styles import COLORS


class AdminSettingsWidget(QWidget):
    """Admin settings and configuration"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Header
        header = QLabel("System Settings & Administration")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        main_layout.addWidget(header)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget {{ background-color: {COLORS['dark']}; }}
            QTabBar::tab {{ background-color: {COLORS['secondary']}; padding: 8px 20px; color: {COLORS['text']}; }}
            QTabBar::tab:selected {{ background-color: {COLORS['accent']}; color: {COLORS['dark']}; }}
        """)
        
        # Users & Roles tab
        users_scroll = QScrollArea()
        users_scroll.setWidgetResizable(True)
        users_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        users_container = QWidget()
        users_layout = QVBoxLayout(users_container)
        users_layout.setSpacing(16)
        
        users_header = QLabel("Users & Roles Management")
        users_header_font = QFont()
        users_header_font.setBold(True)
        users_header.setFont(users_header_font)
        users_layout.addWidget(users_header)
        
        # Users table
        users_table = QTableWidget()
        users_table.setColumnCount(5)
        users_table.setHorizontalHeaderLabels(["Username", "Email", "Role", "Status", "Last Login"])
        users_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['card_bg']};
                alternate-background-color: {COLORS['dark']};
                border: 1px solid {COLORS['border']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
                padding: 8px;
                font-weight: bold;
            }}
        """)
        users_table.setAlternatingRowColors(True)
        
        users_data = [
            ("admin", "admin@company.com", "Administrator", "🟢 Active", "2024-01-15 14:35"),
            ("supervisor1", "supervisor1@company.com", "Supervisor", "🟢 Active", "2024-01-15 12:20"),
            ("operator1", "operator1@company.com", "Operator", "🟢 Active", "2024-01-15 08:15"),
            ("analyst1", "analyst1@company.com", "Analyst", "🟢 Active", "2024-01-14 16:45"),
            ("viewer1", "viewer1@company.com", "Viewer", "🟡 Inactive", "2024-01-10 09:30"),
        ]
        
        for row, user in enumerate(users_data):
            for col, value in enumerate(user):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                users_table.setItem(row, col, item)
        
        users_layout.addWidget(users_table)
        
        # User management buttons
        user_btn_layout = QHBoxLayout()
        btn_add_user = QPushButton("➕ Add User")
        btn_edit_user = QPushButton("✏️ Edit")
        btn_delete_user = QPushButton("🗑️ Delete")
        btn_reset_pwd = QPushButton("🔑 Reset Password")
        
        user_btn_layout.addWidget(btn_add_user)
        user_btn_layout.addWidget(btn_edit_user)
        user_btn_layout.addWidget(btn_delete_user)
        user_btn_layout.addWidget(btn_reset_pwd)
        user_btn_layout.addStretch()
        
        users_layout.addLayout(user_btn_layout)
        
        # Roles configuration
        roles_card = Card("Role Permissions")
        roles_layout = QVBoxLayout()
        
        roles_layout.addWidget(QLabel("Select Role:"))
        role_select = QComboBox()
        role_select.addItems(["Administrator", "Supervisor", "Operator", "Analyst", "Viewer"])
        roles_layout.addWidget(role_select)
        
        perms_text = QLabel(
            "Dashboard: ✓\n"
            "Live Monitor: ✓\n"
            "Playback: ✓\n"
            "Alerts: ✓\n"
            "People/ReID: ✓\n"
            "Access Control: ✓\n"
            "Reports: ✓\n"
            "Settings: ✓"
        )
        roles_layout.addWidget(perms_text)
        
        btn_save_roles = QPushButton("💾 Save")
        roles_layout.addWidget(btn_save_roles)
        
        roles_card.content_layout = roles_layout
        users_layout.addWidget(roles_card)
        
        users_layout.addStretch()
        users_scroll.setWidget(users_container)
        tabs.addTab(users_scroll, "👥 Users & Roles")
        
        # Privacy & Retention tab
        privacy_scroll = QScrollArea()
        privacy_scroll.setWidgetResizable(True)
        privacy_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        privacy_container = QWidget()
        privacy_layout = QVBoxLayout(privacy_container)
        privacy_layout.setSpacing(16)
        
        # Data retention
        retention_card = Card("Data Retention Policy")
        
        retention_grid_layout = QVBoxLayout()
        
        retention_grid_layout.addWidget(QLabel("Video Retention:"))
        retention_spinbox = QSpinBox()
        retention_spinbox.setMinimum(1)
        retention_spinbox.setMaximum(365)
        retention_spinbox.setValue(30)
        retention_spinbox.setSuffix(" days")
        retention_grid_layout.addWidget(retention_spinbox)
        
        retention_grid_layout.addWidget(QLabel("Archive Older than:"))
        archive_spinbox = QSpinBox()
        archive_spinbox.setMinimum(7)
        archive_spinbox.setMaximum(365)
        archive_spinbox.setValue(90)
        archive_spinbox.setSuffix(" days")
        retention_grid_layout.addWidget(archive_spinbox)
        
        retention_grid_layout.addWidget(QLabel("Auto-delete Archived:"))
        auto_delete_spinbox = QSpinBox()
        auto_delete_spinbox.setMinimum(30)
        auto_delete_spinbox.setMaximum(730)
        auto_delete_spinbox.setValue(365)
        auto_delete_spinbox.setSuffix(" days")
        retention_grid_layout.addWidget(auto_delete_spinbox)
        
        retention_card.content_layout.addLayout(retention_grid_layout)
        privacy_layout.addWidget(retention_card)
        
        # Privacy settings
        privacy_card = Card("Privacy Settings")
        
        privacy_grid_layout = QVBoxLayout()
        
        check_mask_faces = QCheckBox("Blur Faces Automatically")
        privacy_grid_layout.addWidget(check_mask_faces)
        
        check_encrypt = QCheckBox("Encrypt Video Files")
        check_encrypt.setChecked(True)
        privacy_grid_layout.addWidget(check_encrypt)
        
        check_gdpr = QCheckBox("Enable GDPR Compliance Mode")
        check_gdpr.setChecked(True)
        privacy_grid_layout.addWidget(check_gdpr)
        
        check_audit = QCheckBox("Log All Access Events")
        check_audit.setChecked(True)
        privacy_grid_layout.addWidget(check_audit)
        
        privacy_card.content_layout.addLayout(privacy_grid_layout)
        privacy_layout.addWidget(privacy_card)
        
        privacy_layout.addStretch()
        privacy_scroll.setWidget(privacy_container)
        tabs.addTab(privacy_scroll, "🔒 Privacy & Retention")
        
        # Model Thresholds tab
        model_scroll = QScrollArea()
        model_scroll.setWidgetResizable(True)
        model_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        model_container = QWidget()
        model_layout = QVBoxLayout(model_container)
        model_layout.setSpacing(16)
        
        threshold_card = Card("AI Model Thresholds")
        
        threshold_grid_layout = QVBoxLayout()
        
        threshold_grid_layout.addWidget(QLabel("PPE Detection Confidence:"))
        ppe_threshold = QSpinBox()
        ppe_threshold.setMinimum(0)
        ppe_threshold.setMaximum(100)
        ppe_threshold.setValue(85)
        ppe_threshold.setSuffix("%")
        threshold_grid_layout.addWidget(ppe_threshold)
        
        threshold_grid_layout.addWidget(QLabel("Face Recognition Confidence:"))
        face_threshold = QSpinBox()
        face_threshold.setMinimum(0)
        face_threshold.setMaximum(100)
        face_threshold.setValue(90)
        face_threshold.setSuffix("%")
        threshold_grid_layout.addWidget(face_threshold)
        
        threshold_grid_layout.addWidget(QLabel("Person Detection Confidence:"))
        person_threshold = QSpinBox()
        person_threshold.setMinimum(0)
        person_threshold.setMaximum(100)
        person_threshold.setValue(75)
        person_threshold.setSuffix("%")
        threshold_grid_layout.addWidget(person_threshold)
        
        threshold_card.content_layout.addLayout(threshold_grid_layout)
        model_layout.addWidget(threshold_card)
        
        model_layout.addStretch()
        model_scroll.setWidget(model_container)
        tabs.addTab(model_scroll, "🧠 Model Config")
        
        # Integrations tab
        integrations_scroll = QScrollArea()
        integrations_scroll.setWidgetResizable(True)
        integrations_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        integrations_container = QWidget()
        integrations_layout = QVBoxLayout(integrations_container)
        integrations_layout.setSpacing(16)
        
        # Email integration
        email_card = Card("Email Notifications")
        
        email_grid_layout = QVBoxLayout()
        
        email_grid_layout.addWidget(QLabel("SMTP Server:"))
        smtp_input = QLineEdit()
        smtp_input.setPlaceholderText("smtp.gmail.com")
        email_grid_layout.addWidget(smtp_input)
        
        email_grid_layout.addWidget(QLabel("Email Address:"))
        email_input = QLineEdit()
        email_input.setPlaceholderText("alerts@company.com")
        email_grid_layout.addWidget(email_input)
        
        check_email_alerts = QCheckBox("Enable Email Alerts")
        check_email_alerts.setChecked(True)
        email_grid_layout.addWidget(check_email_alerts)
        
        email_card.content_layout.addLayout(email_grid_layout)
        integrations_layout.addWidget(email_card)
        
        # Webhook integration
        webhook_card = Card("Webhook Integration")
        
        webhook_grid_layout = QVBoxLayout()
        
        webhook_grid_layout.addWidget(QLabel("Webhook URL:"))
        webhook_input = QLineEdit()
        webhook_input.setPlaceholderText("https://api.example.com/alerts")
        webhook_grid_layout.addWidget(webhook_input)
        
        check_webhook = QCheckBox("Enable Webhooks")
        webhook_grid_layout.addWidget(check_webhook)
        
        webhook_card.content_layout.addLayout(webhook_grid_layout)
        integrations_layout.addWidget(webhook_card)
        
        integrations_layout.addStretch()
        integrations_scroll.setWidget(integrations_container)
        tabs.addTab(integrations_scroll, "🔗 Integrations")
        
        # Audit Logs tab
        audit_scroll = QScrollArea()
        audit_scroll.setWidgetResizable(True)
        audit_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        audit_container = QWidget()
        audit_layout = QVBoxLayout(audit_container)
        audit_layout.setSpacing(16)
        
        # Audit logs table
        audit_table = QTableWidget()
        audit_table.setColumnCount(4)
        audit_table.setHorizontalHeaderLabels(["Timestamp", "User", "Action", "Status"])
        audit_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['card_bg']};
                alternate-background-color: {COLORS['dark']};
                border: 1px solid {COLORS['border']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
                padding: 8px;
                font-weight: bold;
            }}
        """)
        audit_table.setAlternatingRowColors(True)
        
        audit_data = [
            ("2024-01-15 14:35:22", "admin", "Viewed Alert #12345", "🟢 Success"),
            ("2024-01-15 14:32:15", "operator1", "Modified Camera Settings", "🟢 Success"),
            ("2024-01-15 14:28:42", "supervisor1", "Generated Report", "🟢 Success"),
            ("2024-01-15 14:25:10", "viewer1", "Accessed Playback", "🟢 Success"),
            ("2024-01-15 14:20:33", "admin", "Updated User Role", "🟢 Success"),
        ]
        
        for row, audit in enumerate(audit_data):
            for col, value in enumerate(audit):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                audit_table.setItem(row, col, item)
        
        audit_layout.addWidget(audit_table)
        
        audit_scroll.setWidget(audit_container)
        tabs.addTab(audit_scroll, "📋 Audit Logs")
        
        main_layout.addWidget(tabs)
