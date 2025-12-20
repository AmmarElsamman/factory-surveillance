"""
Worker data model
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

@dataclass
class Worker:
    """Worker entity model"""
    worker_id: uuid.UUID
    employee_code: str
    full_name: str
    department: Optional[str] = None
    role: Optional[str] = None
    is_authorized: bool = True
    registration_date: Optional[datetime] = None
    status: str = "active"
    contact_info: Optional[Dict[str, Any]] = None
    photo_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Worker':
        """Create Worker instance from dictionary"""
        worker_id = data.get('worker_id')
        if isinstance(worker_id, str):
            worker_id = uuid.UUID(worker_id)
        
        # Handle contact_info if it's a string
        contact_info = data.get('contact_info')
        if isinstance(contact_info, str):
            try:
                import json
                contact_info = json.loads(contact_info)
            except:
                contact_info = None
        
        return cls(
            worker_id=worker_id,
            employee_code=data.get('employee_code'),
            full_name=data.get('full_name'),
            department=data.get('department'),
            role=data.get('role'),
            is_authorized=bool(data.get('is_authorized', True)),
            registration_date=data.get('registration_date'),
            status=data.get('status', 'active'),
            contact_info=contact_info,
            photo_url=data.get('photo_url'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"{self.full_name} ({self.employee_code})"
    
    def get_status_emoji(self) -> str:
        """Get status emoji for UI"""
        status_map = {
            'active': '🟢',
            'inactive': '⚫',
            'suspended': '🔴',
            'on_leave': '🟡',
            'terminated': '🔴'
        }
        return status_map.get(self.status.lower(), '⚪')
    
    def get_authorization_icon(self) -> str:
        """Get authorization icon"""
        return "✅" if self.is_authorized else "❌"
    
    def get_contact_info_text(self) -> str:
        """Format contact info as text"""
        if not self.contact_info:
            return "No contact info"
        
        info_parts = []
        if 'email' in self.contact_info:
            info_parts.append(f"📧 {self.contact_info['email']}")
        if 'phone' in self.contact_info:
            info_parts.append(f"📞 {self.contact_info['phone']}")
        
        return "\n".join(info_parts) if info_parts else "No contact details"