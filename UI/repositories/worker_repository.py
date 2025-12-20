"""
Worker data repository for database operations
"""
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from database import db_manager
from models.worker import Worker

class WorkerRepository:
    """Repository for worker database operations"""
    
    @staticmethod
    def get_all_workers() -> List[Worker]:
        """Get all workers from database"""
        query = """
            SELECT 
                worker_id,
                employee_code,
                full_name,
                department,
                role,
                is_authorized,
                registration_date,
                status,
                contact_info,
                photo_url,
                created_at,
                updated_at
            FROM workers
            ORDER BY full_name
        """
        
        results = db_manager.execute_query(query)
        workers = []
        
        for row in results:
            row_dict = dict(row)
            workers.append(Worker.from_dict(row_dict))
        
        return workers
    
    @staticmethod
    def get_worker_by_id(worker_id: uuid.UUID) -> Optional[Worker]:
        """Get a specific worker by ID"""
        query = """
            SELECT 
                worker_id,
                employee_code,
                full_name,
                department,
                role,
                is_authorized,
                registration_date,
                status,
                contact_info,
                photo_url,
                created_at,
                updated_at
            FROM workers
            WHERE worker_id = %s
        """
        
        results = db_manager.execute_query(query, (str(worker_id),))
        
        if results:
            row_dict = dict(results[0])
            return Worker.from_dict(row_dict)
        
        return None
    
    @staticmethod
    def get_worker_by_employee_code(employee_code: str) -> Optional[Worker]:
        """Get a specific worker by employee code"""
        query = """
            SELECT 
                worker_id,
                employee_code,
                full_name,
                department,
                role,
                is_authorized,
                registration_date,
                status,
                contact_info,
                photo_url,
                created_at,
                updated_at
            FROM workers
            WHERE employee_code = %s
        """
        
        results = db_manager.execute_query(query, (employee_code,))
        
        if results:
            row_dict = dict(results[0])
            return Worker.from_dict(row_dict)
        
        return None
    
    @staticmethod
    def search_workers(search_term: str) -> List[Worker]:
        """Search workers by name or employee code"""
        query = """
            SELECT 
                worker_id,
                employee_code,
                full_name,
                department,
                role,
                is_authorized,
                registration_date,
                status,
                contact_info,
                photo_url,
                created_at,
                updated_at
            FROM workers
            WHERE full_name ILIKE %s OR employee_code ILIKE %s
            ORDER BY full_name
        """
        
        search_pattern = f"%{search_term}%"
        results = db_manager.execute_query(query, (search_pattern, search_pattern))
        workers = []
        
        for row in results:
            row_dict = dict(row)
            workers.append(Worker.from_dict(row_dict))
        
        return workers
    
    @staticmethod
    def get_workers_by_department(department: str) -> List[Worker]:
        """Get workers filtered by department"""
        query = """
            SELECT 
                worker_id,
                employee_code,
                full_name,
                department,
                role,
                is_authorized,
                registration_date,
                status,
                contact_info,
                photo_url,
                created_at,
                updated_at
            FROM workers
            WHERE department = %s
            ORDER BY full_name
        """
        
        results = db_manager.execute_query(query, (department,))
        workers = []
        
        for row in results:
            row_dict = dict(row)
            workers.append(Worker.from_dict(row_dict))
        
        return workers
    
    @staticmethod
    def get_workers_by_status(status: str) -> List[Worker]:
        """Get workers filtered by status"""
        query = """
            SELECT 
                worker_id,
                employee_code,
                full_name,
                department,
                role,
                is_authorized,
                registration_date,
                status,
                contact_info,
                photo_url,
                created_at,
                updated_at
            FROM workers
            WHERE status = %s
            ORDER BY full_name
        """
        
        results = db_manager.execute_query(query, (status,))
        workers = []
        
        for row in results:
            row_dict = dict(row)
            workers.append(Worker.from_dict(row_dict))
        
        return workers
    
    @staticmethod
    def get_workers_by_authorization(is_authorized: bool) -> List[Worker]:
        """Get workers filtered by authorization status"""
        query = """
            SELECT 
                worker_id,
                employee_code,
                full_name,
                department,
                role,
                is_authorized,
                registration_date,
                status,
                contact_info,
                photo_url,
                created_at,
                updated_at
            FROM workers
            WHERE is_authorized = %s
            ORDER BY full_name
        """
        
        results = db_manager.execute_query(query, (is_authorized,))
        workers = []
        
        for row in results:
            row_dict = dict(row)
            workers.append(Worker.from_dict(row_dict))
        
        return workers
    
    @staticmethod
    def get_worker_statistics() -> Dict[str, Any]:
        """Get worker statistics"""
        query = """
            SELECT 
                COUNT(*) as total_workers,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_workers,
                COUNT(CASE WHEN status = 'suspended' THEN 1 END) as suspended_workers,
                COUNT(CASE WHEN status = 'inactive' THEN 1 END) as inactive_workers,
                COUNT(CASE WHEN is_authorized = true THEN 1 END) as authorized_workers,
                COUNT(CASE WHEN is_authorized = false THEN 1 END) as unauthorized_workers,
                COUNT(DISTINCT department) as departments_count
            FROM workers
        """
        
        results = db_manager.execute_query(query)
        if results and len(results) > 0:
            return dict(results[0])
        return {
            'total_workers': 0,
            'active_workers': 0,
            'suspended_workers': 0,
            'inactive_workers': 0,
            'authorized_workers': 0,
            'unauthorized_workers': 0,
            'departments_count': 0
        }
    
    @staticmethod
    def get_all_departments() -> List[str]:
        """Get all unique departments from database"""
        query = """
            SELECT DISTINCT department 
            FROM workers 
            WHERE department IS NOT NULL 
            ORDER BY department
        """
        
        results = db_manager.execute_query(query)
        departments = [row['department'] for row in results if row['department']]
        return departments
    
    @staticmethod
    def create_worker(worker_data: Dict[str, Any]) -> Optional[Worker]:
        """Create a new worker"""
        query = """
            INSERT INTO workers (
                employee_code, full_name, department, role, 
                is_authorized, status, contact_info, photo_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
            RETURNING *
        """
        
        try:
            results = db_manager.execute_query(
                query,
                (
                    worker_data.get('employee_code'),
                    worker_data.get('full_name'),
                    worker_data.get('department'),
                    worker_data.get('role'),
                    worker_data.get('is_authorized', True),
                    worker_data.get('status', 'active'),
                    worker_data.get('contact_info'),
                    worker_data.get('photo_url')
                )
            )
            
            if results:
                row_dict = dict(results[0])
                return Worker.from_dict(row_dict)
        except Exception as e:
            print(f"Error creating worker: {e}")
        
        return None
    
    @staticmethod
    def update_worker_status(worker_id: uuid.UUID, status: str) -> bool:
        """Update worker status"""
        query = """
            UPDATE workers 
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE worker_id = %s
        """
        
        return db_manager.execute_update(query, (status, str(worker_id)))
    
    @staticmethod
    def update_worker_authorization(worker_id: uuid.UUID, is_authorized: bool) -> bool:
        """Update worker authorization status"""
        query = """
            UPDATE workers 
            SET is_authorized = %s, updated_at = CURRENT_TIMESTAMP
            WHERE worker_id = %s
        """
        
        return db_manager.execute_update(query, (is_authorized, str(worker_id)))