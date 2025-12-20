"""
Camera data repository for database operations
"""
from typing import List, Optional, Dict, Any
from database import db_manager
from models.camera import Camera

class CameraRepository:
    """Repository for camera database operations"""
    
    @staticmethod
    def get_all_cameras() -> List[Camera]:
        """Get all cameras from database"""
        query = """
            SELECT 
                camera_id,
                location_name,
                zone_type,
                coordinates,
                ip_address::text,
                status,
                field_of_view,
                installation_date,
                created_at,
                updated_at
            FROM cameras
            ORDER BY camera_id
        """
        
        results = db_manager.execute_query(query)
        cameras = []
        
        for row in results:
            # row is already a dict from RealDictCursor
            # coordinates and field_of_view are already Python dicts (from JSONB)
            row_dict = dict(row)
            cameras.append(Camera.from_dict(row_dict))
        
        return cameras
    
    @staticmethod
    def get_camera_by_id(camera_id: str) -> Optional[Camera]:
        """Get a specific camera by ID"""
        query = """
            SELECT 
                camera_id,
                location_name,
                zone_type,
                coordinates,
                ip_address::text,
                status,
                field_of_view,
                installation_date,
                created_at,
                updated_at
            FROM cameras
            WHERE camera_id = %s
        """
        
        results = db_manager.execute_query(query, (camera_id,))
        
        if results:
            row_dict = dict(results[0])
            return Camera.from_dict(row_dict)
        
        return None
    
    @staticmethod
    def get_cameras_by_status(status: str) -> List[Camera]:
        """Get cameras filtered by status"""
        query = """
            SELECT 
                camera_id,
                location_name,
                zone_type,
                coordinates,
                ip_address::text,
                status,
                field_of_view,
                installation_date,
                created_at,
                updated_at
            FROM cameras
            WHERE status = %s
            ORDER BY camera_id
        """
        
        results = db_manager.execute_query(query, (status,))
        cameras = []
        
        for row in results:
            row_dict = dict(row)
            cameras.append(Camera.from_dict(row_dict))
        
        return cameras
    
    @staticmethod
    def get_cameras_by_zone(zone: str) -> List[Camera]:
        """Get cameras filtered by zone"""
        query = """
            SELECT 
                camera_id,
                location_name,
                zone_type,
                coordinates,
                ip_address::text,
                status,
                field_of_view,
                installation_date,
                created_at,
                updated_at
            FROM cameras
            WHERE zone_type = %s
            ORDER BY camera_id
        """
        
        results = db_manager.execute_query(query, (zone,))
        cameras = []
        
        for row in results:
            row_dict = dict(row)
            cameras.append(Camera.from_dict(row_dict))
        
        return cameras
    
    @staticmethod
    def update_camera_status(camera_id: str, status: str) -> bool:
        """Update camera status"""
        query = """
            UPDATE cameras 
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE camera_id = %s
        """
        
        return db_manager.execute_update(query, (status, camera_id))
    
    @staticmethod
    def get_camera_stats() -> Dict[str, Any]:
        """Get camera statistics"""
        query = """
            SELECT 
                COUNT(*) as total_cameras,
                COUNT(CASE WHEN status = 'online' THEN 1 END) as online_cameras,
                COUNT(CASE WHEN status = 'offline' THEN 1 END) as offline_cameras,
                COUNT(CASE WHEN status = 'maintenance' THEN 1 END) as maintenance_cameras,
                COUNT(CASE WHEN status = 'weak_signal' THEN 1 END) as weak_signal_cameras,
                COUNT(DISTINCT zone_type) as zones_covered
            FROM cameras
        """
        
        results = db_manager.execute_query(query)
        if results and len(results) > 0:
            return dict(results[0])
        return {
            'total_cameras': 0,
            'online_cameras': 0,
            'offline_cameras': 0,
            'maintenance_cameras': 0,
            'weak_signal_cameras': 0,
            'zones_covered': 0
        }
    
    @staticmethod
    def get_all_zones() -> List[str]:
        """Get all unique zones from database"""
        query = """
            SELECT DISTINCT zone_type 
            FROM cameras 
            WHERE zone_type IS NOT NULL 
            ORDER BY zone_type
        """
        
        results = db_manager.execute_query(query)
        zones = [row['zone_type'] for row in results if row['zone_type']]
        return zones