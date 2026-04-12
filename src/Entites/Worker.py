
"""
Worker Entity
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from enums import WorkerStatus

@dataclass
class Worker:
    """
    Worker Entity
    Represents a registered employee
    """
    employee_code: str
    full_name: str
    worker_id: str = field(default_factory=lambda: str(uuid4()))
    department: Optional[str] = None
    role: Optional[str] = None
    is_authorized: bool = True
    status: WorkerStatus = WorkerStatus.ACTIVE
    registration_date: datetime = field(default_factory=datetime.now)
    contact_info: Optional[dict] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def deactivate(self) -> None:
        """Deactivate worker"""
        self.status = WorkerStatus.INACTIVE
        self.is_authorized = False
        self.updated_at = datetime.now()
    
    def reactivate(self) -> None:
        """Reactivate worker"""
        self.status = WorkerStatus.ACTIVE
        self.is_authorized = True
        self.updated_at = datetime.now()
    
    def update_info(
        self,
        full_name: Optional[str] = None,
        department: Optional[str] = None,
        role: Optional[str] = None
    ) -> None:
        """Update worker information"""
        if full_name:
            self.full_name = full_name
        if department:
            self.department = department
        if role:
            self.role = role
        self.updated_at = datetime.now()