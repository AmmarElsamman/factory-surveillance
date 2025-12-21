"""
People/ReID view - Face recognition and person tracking
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QLineEdit, QComboBox, QFrame, QGridLayout,
                               QScrollArea, QCheckBox, QTabWidget, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from ui.utils.components import Card, EventItem
from ui.utils.styles import COLORS
import uuid

# Import worker repository
try:
    from repositories.worker_repository import WorkerRepository
    from models.worker import Worker
    DATABASE_ENABLED = True
except ImportError as e:
    print(f"Database import error: {e}")
    DATABASE_ENABLED = False


class PeopleWidget(QWidget):
    """Person ReID and face recognition"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_selected_worker = None
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Header with statistics
        header_layout = QHBoxLayout()
        header = QLabel("Personnel Management")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header_layout.addWidget(header)
        
        # Statistics label
        self.stats_label = QLabel("Loading statistics...")
        self.stats_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt;")
        header_layout.addWidget(self.stats_label, alignment=Qt.AlignRight)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Search section
        search_card = Card("Search & Filter")
        
        search_layout = QHBoxLayout()
        search_layout.setSpacing(12)
        
        # Search by name/ID
        search_layout.addWidget(QLabel("Search:"))
        self.name_search = QLineEdit()
        self.name_search.setPlaceholderText("Search by name or employee code...")
        self.name_search.returnPressed.connect(self.search_workers)
        search_layout.addWidget(self.name_search)
        
        # Department filter
        search_layout.addWidget(QLabel("Department:"))
        self.dept_combo = QComboBox()
        self.dept_combo.addItem("All Departments")
        self.dept_combo.currentTextChanged.connect(self.apply_filters)
        search_layout.addWidget(self.dept_combo)
        
        # Status filter
        search_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All Status", "Active", "Suspended", "Inactive"])
        self.status_combo.currentTextChanged.connect(self.apply_filters)
        search_layout.addWidget(self.status_combo)
        
        # Authorization filter
        search_layout.addWidget(QLabel("Auth:"))
        self.auth_combo = QComboBox()
        self.auth_combo.addItems(["All", "Authorized", "Unauthorized"])
        self.auth_combo.currentTextChanged.connect(self.apply_filters)
        search_layout.addWidget(self.auth_combo)
        
        btn_search = QPushButton("🔍 Search")
        btn_search.clicked.connect(self.search_workers)
        search_layout.addWidget(btn_search)
        
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self.load_workers)
        search_layout.addWidget(btn_refresh)
        
        search_layout.addStretch()
        
        search_card.content_layout.addLayout(search_layout)
        main_layout.addWidget(search_card)
        
        # Results section with tabs
        results_label = QLabel("Personnel Database")
        results_label_font = QFont()
        results_label_font.setPointSize(12)
        results_label_font.setBold(True)
        results_label.setFont(results_label_font)
        main_layout.addWidget(results_label)
        
        # Create tabs for different views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget {{ background-color: {COLORS['dark']}; }}
            QTabBar::tab {{ background-color: {COLORS['secondary']}; padding: 8px 20px; color: {COLORS['text']}; }}
            QTabBar::tab:selected {{ background-color: {COLORS['accent']}; color: {COLORS['dark']}; }}
        """)
        
        # Profile cards view
        self.profiles_scroll = QScrollArea()
        self.profiles_scroll.setWidgetResizable(True)
        self.profiles_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.profiles_container = QWidget()
        self.profiles_grid = QGridLayout(self.profiles_container)
        self.profiles_grid.setSpacing(12)
        
        self.profiles_scroll.setWidget(self.profiles_container)
        self.tabs.addTab(self.profiles_scroll, "👤 Personnel Cards")
        
        # Timeline view (placeholder for now)
        self.timeline_scroll = QScrollArea()
        self.timeline_scroll.setWidgetResizable(True)
        self.timeline_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.timeline_container = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        
        timeline_label = QLabel("Person Timeline (Coming Soon)")
        timeline_label.setAlignment(Qt.AlignCenter)
        timeline_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt; padding: 40px;")
        self.timeline_layout.addWidget(timeline_label)
        
        self.timeline_scroll.setWidget(self.timeline_container)
        self.tabs.addTab(self.timeline_scroll, "📍 Timeline")
        
        # Analytics view
        self.analytics_scroll = QScrollArea()
        self.analytics_scroll.setWidgetResizable(True)
        self.analytics_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.analytics_container = QWidget()
        self.analytics_layout = QVBoxLayout(self.analytics_container)
        
        self.analytics_label = QLabel("Loading analytics...")
        self.analytics_label.setAlignment(Qt.AlignCenter)
        self.analytics_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt; padding: 40px;")
        self.analytics_layout.addWidget(self.analytics_label)
        
        self.analytics_scroll.setWidget(self.analytics_container)
        self.tabs.addTab(self.analytics_scroll, "📊 Analytics")
        
        main_layout.addWidget(self.tabs)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)  # Refresh every 60 seconds
        
        # Load initial data
        if DATABASE_ENABLED:
            self.load_workers()
        else:
            self.show_error_message("Database not available")
    
    def show_error_message(self, message: str):
        """Show error message in UI"""
        error_label = QLabel(f"⚠️ {message}")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 11pt; padding: 40px;")
        
        # Clear existing content
        while self.profiles_grid.count():
            item = self.profiles_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.profiles_grid.addWidget(error_label, 0, 0, 1, 3)
    
    def load_workers(self):
        """Load workers from database"""
        if not DATABASE_ENABLED:
            self.show_error_message("Database connection not available")
            return
        
        try:
            # Get all workers
            workers = WorkerRepository.get_all_workers()
            
            # Update department filter
            departments = WorkerRepository.get_all_departments()
            current_depts = [self.dept_combo.itemText(i) for i in range(self.dept_combo.count())]
            self.dept_combo.clear()
            self.dept_combo.addItem("All Departments")
            
            for dept in departments:
                if dept and dept not in current_depts:
                    self.dept_combo.addItem(dept)
            
            # Update statistics
            stats = WorkerRepository.get_worker_statistics()
            if stats:
                stats_text = f"👥 Total: {stats.get('total_workers', 0)} | "
                stats_text += f"🟢 Active: {stats.get('active_workers', 0)} | "
                stats_text += f"🔴 Suspended: {stats.get('suspended_workers', 0)} | "
                stats_text += f"✅ Authorized: {stats.get('authorized_workers', 0)}"
                self.stats_label.setText(stats_text)
                
                # Update analytics tab
                analytics_text = f"""
                Personnel Statistics:
                --------------------
                👥 Total Workers: {stats.get('total_workers', 0)}
                🟢 Active: {stats.get('active_workers', 0)}
                🔴 Suspended: {stats.get('suspended_workers', 0)}
                ⚫ Inactive: {stats.get('inactive_workers', 0)}
                ✅ Authorized: {stats.get('authorized_workers', 0)}
                ❌ Unauthorized: {stats.get('unauthorized_workers', 0)}
                🏢 Departments: {stats.get('departments_count', 0)}
                """
                self.analytics_label.setText(analytics_text)
            
            # Populate profiles grid
            self.populate_profiles_grid(workers)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error loading workers: {error_details}")
            self.show_error_message(f"Failed to load workers: {str(e)}")
    
    def populate_profiles_grid(self, workers: list):
        """Populate the profiles grid with worker cards"""
        # Clear existing content
        while self.profiles_grid.count():
            item = self.profiles_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not workers:
            no_data_label = QLabel("No workers found in database")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11pt; padding: 40px;")
            self.profiles_grid.addWidget(no_data_label, 0, 0, 1, 3)
            return
        
        # Calculate grid layout
        cols = 3
        for i, worker in enumerate(workers):
            row = i // cols
            col = i % cols
            
            # Create worker card
            worker_card = self.create_worker_card(worker)
            self.profiles_grid.addWidget(worker_card, row, col)
        
        # Add spacer at the bottom
        self.profiles_grid.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 
                                  len(workers) // cols + 1, 0)
    
    def create_worker_card(self, worker: Worker) -> Card:
        """Create a card widget for a worker"""
        # Determine card title based on role
        title = worker.role if worker.role else "Worker"
        
        # Create card
        card = Card(f"{worker.get_status_emoji()} {title}")
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)
        
        # Worker image placeholder (using emoji for now)
        image_frame = QFrame()
        image_frame.setFixedHeight(120)
        image_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
        """)
        
        image_layout = QVBoxLayout(image_frame)
        image_label = QLabel("👤")
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet(f"font-size: 48px; color: {COLORS['text_secondary']};")
        image_layout.addWidget(image_label)
        
        if worker.photo_url:
            photo_label = QLabel("📷 Photo Available")
            photo_label.setAlignment(Qt.AlignCenter)
            photo_label.setStyleSheet(f"font-size: 9pt; color: {COLORS['text_secondary']}; margin-top: 5px;")
            image_layout.addWidget(photo_label)
        
        card_layout.addWidget(image_frame)
        
        # Worker information
        info_text = f"""
        <b>{worker.full_name}
        ID: {worker.employee_code}
        Department: {worker.department or 'N/A'}
        Role: {worker.role or 'N/A'}
        Status: {worker.get_status_emoji()} {worker.status.title()}
        Authorization: {worker.get_authorization_icon()} {'Authorized' if worker.is_authorized else 'Unauthorized'}
        Registered: {worker.registration_date.strftime('%Y-%m-%d') if worker.registration_date else 'N/A'}
        """
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 9pt;
            line-height: 1.4;
            padding: 5px;
        """)
        info_label.setWordWrap(True)
        card_layout.addWidget(info_label)
        
        # Contact info (collapsible)
        if worker.contact_info:
            contact_btn = QPushButton("📞 Contact Info")
            contact_btn.setMaximumHeight(25)
            contact_btn.clicked.connect(lambda checked, w=worker: self.show_contact_info(w))
            card_layout.addWidget(contact_btn)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        # Status toggle button
        if worker.status.lower() == 'active':
            status_btn = QPushButton("🟡 Suspend")
            status_btn.clicked.connect(lambda checked, w=worker: self.toggle_worker_status(w, 'suspended'))
        elif worker.status.lower() == 'suspended':
            status_btn = QPushButton("🟢 Activate")
            status_btn.clicked.connect(lambda checked, w=worker: self.toggle_worker_status(w, 'active'))
        else:
            status_btn = QPushButton("⚪ Set Active")
            status_btn.clicked.connect(lambda checked, w=worker: self.toggle_worker_status(w, 'active'))
        
        status_btn.setMaximumHeight(25)
        actions_layout.addWidget(status_btn)
        
        # Authorization toggle button
        if worker.is_authorized:
            auth_btn = QPushButton("❌ Revoke")
            auth_btn.clicked.connect(lambda checked, w=worker: self.toggle_worker_auth(w, False))
        else:
            auth_btn = QPushButton("✅ Grant")
            auth_btn.clicked.connect(lambda checked, w=worker: self.toggle_worker_auth(w, True))
        
        auth_btn.setMaximumHeight(25)
        actions_layout.addWidget(auth_btn)
        
        card_layout.addLayout(actions_layout)
        
        card.content_layout.addLayout(card_layout)
        return card
    
    def show_contact_info(self, worker: Worker):
        """Show contact information dialog"""
        contact_text = worker.get_contact_info_text()
        QMessageBox.information(self, f"Contact Info - {worker.full_name}", contact_text)
    
    def toggle_worker_status(self, worker: Worker, new_status: str):
        """Toggle worker status"""
        try:
            success = WorkerRepository.update_worker_status(worker.worker_id, new_status)
            if success:
                QMessageBox.information(self, "Success", 
                                       f"Worker {worker.full_name} status updated to {new_status}")
                self.load_workers()  # Refresh the list
            else:
                QMessageBox.warning(self, "Error", "Failed to update worker status")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")
    
    def toggle_worker_auth(self, worker: Worker, is_authorized: bool):
        """Toggle worker authorization"""
        try:
            success = WorkerRepository.update_worker_authorization(worker.worker_id, is_authorized)
            if success:
                status_text = "authorized" if is_authorized else "unauthorized"
                QMessageBox.information(self, "Success", 
                                       f"Worker {worker.full_name} is now {status_text}")
                self.load_workers()  # Refresh the list
            else:
                QMessageBox.warning(self, "Error", "Failed to update authorization")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update authorization: {str(e)}")
    
    def search_workers(self):
        """Search workers based on search term"""
        if not DATABASE_ENABLED:
            return
        
        search_term = self.name_search.text().strip()
        
        try:
            if search_term:
                workers = WorkerRepository.search_workers(search_term)
            else:
                workers = WorkerRepository.get_all_workers()
            
            self.populate_profiles_grid(workers)
            
        except Exception as e:
            QMessageBox.warning(self, "Search Error", f"Failed to search workers: {str(e)}")
    
    def apply_filters(self):
        """Apply filters to worker list"""
        if not DATABASE_ENABLED:
            return
        
        try:
            department_filter = self.dept_combo.currentText()
            status_filter = self.status_combo.currentText()
            auth_filter = self.auth_combo.currentText()
            
            # Start with all workers
            workers = WorkerRepository.get_all_workers()
            
            # Apply filters
            filtered_workers = []
            
            for worker in workers:
                # Department filter
                if department_filter != "All Departments" and worker.department != department_filter:
                    continue
                
                # Status filter
                if status_filter != "All Status":
                    if status_filter.lower() != worker.status.lower():
                        continue
                
                # Authorization filter
                if auth_filter == "Authorized" and not worker.is_authorized:
                    continue
                elif auth_filter == "Unauthorized" and worker.is_authorized:
                    continue
                
                filtered_workers.append(worker)
            
            self.populate_profiles_grid(filtered_workers)
            
        except Exception as e:
            QMessageBox.warning(self, "Filter Error", f"Failed to apply filters: {str(e)}")
    
    def refresh_data(self):
        """Periodic data refresh"""
        if DATABASE_ENABLED:
            self.load_workers()


# Add missing import at the top of the file
from PySide6.QtWidgets import QSpacerItem, QSizePolicy