"""
Database configuration for PostgreSQL connection
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from typing import Dict, Any, List, Optional
from datetime import date, datetime

class DatabaseManager:
    """PostgreSQL database connection manager"""
    
    def __init__(self):
        # Try to get from environment variables first, then use defaults
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'factory_surveillance_db'),
            'user': os.getenv('DB_USER', 'surveillance_app'),
            'password': os.getenv('DB_PASSWORD', 'djr6w32g')
        }
        
        # Test connection on initialization
        self.test_connection()
        
    def test_connection(self):
        """Test database connection"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            print("Database connection: ✓ OK")
        except Exception as e:
            print(f"Database connection: ✗ FAILED - {e}")
            print(f"Connection params: host={self.connection_params['host']}, "
                  f"db={self.connection_params['database']}, "
                  f"user={self.connection_params['user']}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Cannot connect to database: {e}")
        except Exception as e:
            raise Exception(f"Database error: {e}")
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self, connection=None):
        """Get database cursor with context manager"""
        if connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
            finally:
                cursor.close()
        else:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                try:
                    yield cursor
                finally:
                    cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except psycopg2.ProgrammingError as e:
            print(f"SQL Error in query: {query}")
            print(f"Error: {e}")
            return []
        except Exception as e:
            print(f"Query execution error: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """Execute an INSERT, UPDATE, DELETE query"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Update execution error: {e}")
            return False

# Singleton instance
db_manager = DatabaseManager()


class Camera:
    """Camera data model"""
    def __init__(self, camera_id: str, location_name: str, zone_type: str,
                 coordinates: Optional[Dict[str, Any]] = None,
                 ip_address: Optional[str] = None,
                 status: str = "online",
                 field_of_view: Optional[Dict[str, Any]] = None,
                 installation_date: Optional[date] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.camera_id = camera_id
        self.location_name = location_name
        self.zone_type = zone_type
        self.coordinates = coordinates
        self.ip_address = ip_address
        self.status = status
        self.field_of_view = field_of_view
        self.installation_date = installation_date
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Camera':
        """Create Camera instance from dictionary"""
        # Handle date conversions
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
    
    def __str__(self):
        return f"Camera({self.camera_id}: {self.location_name})"


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