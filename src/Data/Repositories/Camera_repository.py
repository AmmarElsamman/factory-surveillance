
from datetime import datetime
from typing import List, Optional

from enums import CameraStatus

from Utils.logger import get_logger

from Entites.Camera import Camera
from .base import BaseRepository, IRepository
import json

logger = get_logger(__name__)

class CameraRepository(BaseRepository[Camera], IRepository[Camera]):
    """
    Repository for Camera Entity
    """
    
    def add(self, camera: Camera) -> str:
        """Add new camera to database"""
        query = """
            INSERT INTO cameras 
            (camera_id, location_name, zone_type, coordinates, ip_address, status,
                field_of_view, installation_date, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING camera_id
        """
        
        self._execute(query, (
            camera.camera_id,
            camera.location_name,
            camera.zone_type,
            json.dumps(camera.coordinates) if camera.coordinates else None,
            camera.ip_address,
            camera.status.value,
            json.dumps(camera.field_of_view) if camera.field_of_view else None,
            camera.installation_date,
            camera.created_at,
            camera.updated_at
        ))
        
        result = self._fetch_one()
        logger.info(f"Camera {camera.camera_id} added to database")
        return result['camera_id']
    
    def get_by_id(self, camera_id: str) -> Optional[Camera]:
        """Get camera by ID"""
        query = """
            SELECT * FROM cameras
            WHERE camera_id = %s
        """
        
        self._execute(query, (camera_id,))
        row = self._fetch_one()
        
        if not row:
            return None
        
        return self._map_to_entity(row)
    
    def update(self, camera: Camera) -> bool:
        """Update camera information"""
        query = """
            UPDATE cameras
            SET location_name = %s,
                zone_type = %s,
                coordinates = %s,
                ip_address = %s,
                status = %s,
                field_of_view = %s,
                installation_date = %s,
                updated_at = %s
            WHERE camera_id = %s
        """
        
        self._execute(query, (
            camera.location_name,
            camera.zone_type,
            json.dumps(camera.coordinates) if camera.coordinates else None,
            camera.ip_address,
            camera.status.value,
            json.dumps(camera.field_of_view) if camera.field_of_view else None,
            camera.installation_date,
            datetime.now(),
            camera.camera_id
        ))
        
        logger.info(f"Camera {camera.camera_id} updated in database")
        return True

    def delete(self, camera_id: str) -> bool:
        """Delete camera from database"""
        query = """
            DELETE FROM cameras
            WHERE camera_id = %s
        """
        
        self._execute(query, (camera_id,))
        logger.info(f"Camera {camera_id} deleted from database")
        return True
    
    def list_all(self, limit = 100, offset = 0) -> List[Camera]:
        """List all cameras with pagination"""
        query = """
            SELECT * FROM cameras
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        
        self._execute(query, (limit, offset))
        rows = self._fetch_all()
        
        return [self._map_to_entity(row) for row in rows]
    
    def get_cameras_by_status(self, status: str) -> List[Camera]:
        """Get cameras by status"""
        query = """
            SELECT * FROM cameras
            WHERE status = %s
            ORDER BY created_at DESC
        """
        
        self._execute(query, (status,))
        rows = self._fetch_all()
        
        return [self._map_to_entity(row) for row in rows]
    
    def get_cameras_by_zone_type(self, zone_type: str) -> List[Camera]:
        """Get cameras by zone type"""
        query = """
            SELECT * FROM cameras
            WHERE zone_type = %s
            ORDER BY created_at DESC
        """
        
        self._execute(query, (zone_type,))
        rows = self._fetch_all()
        
        return [self._map_to_entity(row) for row in rows]
    
    def _map_to_entity(self, row: dict) -> Camera:
        """Map database row to Camera entity"""
        return Camera(
            camera_id=row['camera_id'],
            location_name=row['location_name'],
            zone_type=row['zone_type'],
            coordinates=row['coordinates'],
            ip_address=row['ip_address'],
            status=CameraStatus(row['status']),
            field_of_view=row['field_of_view'],
            installation_date=row['installation_date'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )