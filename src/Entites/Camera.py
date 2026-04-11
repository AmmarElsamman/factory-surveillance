"""
Camera Entity
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..enums import CameraStatus

@dataclass
class Camera:
    """
    Camera Entity
    Represents a surveillance camera in the factory
    """
    camera_id: str
    location_name: str
    zone_type: str
    ip_address: str
    coordinates: Optional[dict] = None
    status: CameraStatus = CameraStatus.ACTIVE
    field_of_view: Optional[dict] = None
    installation_date: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update_status(self, new_status: CameraStatus) -> None:
        """Update camera status"""
        self.status = new_status
        self.updated_at = datetime.now()
    