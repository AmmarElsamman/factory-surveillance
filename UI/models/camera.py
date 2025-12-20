"""
Camera data model
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date, datetime

@dataclass
class Camera:
    """Camera entity model"""
    camera_id: str
    location_name: str
    zone_type: str
    coordinates: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    status: str = "online"
    field_of_view: Optional[Dict[str, Any]] = None
    installation_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Camera':
        """Create Camera instance from dictionary"""
        # Handle date conversion if needed
        installation_date = data.get('installation_date')
        if isinstance(installation_date, str):
            try:
                installation_date = datetime.strptime(installation_date, '%Y-%m-%d').date()
            except:
                installation_date = None
        
        return cls(
            camera_id=data.get('camera_id'),
            location_name=data.get('location_name'),
            zone_type=data.get('zone_type'),
            coordinates=data.get('coordinates'),  # Already a dict from psycopg2
            ip_address=data.get('ip_address'),
            status=data.get('status', 'online'),
            field_of_view=data.get('field_of_view'),  # Already a dict from psycopg2
            installation_date=installation_date,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )