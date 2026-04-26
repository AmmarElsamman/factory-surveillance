from datetime import datetime
from typing import List, Optional
from .base import BaseRepository
from .base import IRepository
from Entites.Worker import Worker
from Utils.logger import get_logger
from enums import WorkerStatus
import json

logger = get_logger(__name__)
class WorkerRepository(BaseRepository[Worker], IRepository[Worker]):
    """
    Repository for Worker Entity
    """
    
    def add(self, worker: Worker) -> str:
        """Add new worker to database"""
        query = """
            INSERT INTO workers 
            (worker_id, employee_code, full_name, department, role,
             is_authorized, registration_date, status, contact_info, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING worker_id
        """
        
        
        self._execute(query, (
            worker.worker_id,
            worker.employee_code,
            worker.full_name,
            worker.department,
            worker.role,
            worker.is_authorized,
            worker.registration_date,
            worker.status.value,
            json.dumps(worker.contact_info) if worker.contact_info else None,
            worker.created_at,
            worker.updated_at
        ))
        
        result = self._fetch_one()
        logger.info(f"Worker {worker.employee_code} added to database")
        return  result['worker_id']
    
    def get_by_id(self, worker_id: str) -> Optional[Worker]:
        """Get worker by ID"""
        
        query = """
            SELECT * FROM workers
            WHERE worker_id = %s
        """
        
        self._execute(query, (worker_id,))
        row = self._fetch_one()
        
        if not row:
            return None
        
        return self._map_to_entity(row)
    
    def get_by_employee_code(self, employee_code: str) -> Optional[Worker]:
        """Get worker by employee code"""
        
        query = """
            SELECT * FROM workers
            WHERE employee_code = %s
        """
        
        self._execute(query, (employee_code,))
        row = self._fetch_one()
        
        if not row:
            return None
        
        return self._map_to_entity(row)
    
    def update(self, worker: Worker) -> bool:
        """Update existing worker"""
        
        
        query = """
            UPDATE workers
            SET employee_code = %s,
                full_name = %s,
                department = %s,
                role = %s,
                is_authorized = %s,
                status = %s,
                contact_info = %s,
                updated_at = %s
            WHERE worker_id = %s
        """
        
        self._execute(query,(
            worker.employee_code,
            worker.full_name,
            worker.department,
            worker.role,
            worker.is_authorized,
            worker.status.value,
            json.dumps(worker.contact_info) if worker.contact_info else None,
            datetime.now(),
        ))
        
        logger.info(f"Worker {worker.worker_id} updated")
        return True
    
    def delete(self, worker_id: str) -> bool:
        """Delete worker (delete by deactivating)"""
        
        query = """
            UPDATE workers
            SET status = 'inactive',
                is_authorized = false
            WHERE worker_id = %s
        """
        
        self._execute(query, (worker_id,))
        return True
    
    def list_all(self, limit: int = 20, offset: int = 0) -> List[Worker]:
        """List all workers with pagination"""
        
        query = """
            SELECT * FROM workers
            ORDER BY full_name
            LIMIT %s OFFSET %s
        """
        
        self._execute(query, (limit, offset))
        rows = self._fetch_all()
        
        return [self._map_to_entity(row) for row in rows]
    
    def find_active_workers(self) -> List[Worker]:
        """Find all active workers"""
        
        query = """
            SELECT * FROM workers
            WHERE status = 'active'
            ORDER BY full_name
        """
        self._execute(query)
        rows = self._fetch_all()
        
        return [self._map_to_entity(row) for row in rows]
    
    def find_by_department(self, department: str) -> List[Worker]:
        """Find workers by department"""
        
        query = """
            SELECT * FROM workers
            WHERE department = %s
            ORDER BY full_name
        """
        
        self._execute(query, (department,))
        rows = self._fetch_all()
        
        return [self._map_to_entity(row) for row in rows]
    
    def find_by_status(self, status: WorkerStatus) -> List[Worker]:
        """Find workers by status"""
        
        query = """
            SELECT * FROM workers
            WHERE status = %s
            ORDER BY full_name
        """
        
        self._execute(query, (status,))
        rows = self._fetch_all()
        
        return [self._map_to_entity(row) for row in rows]
    
    def _map_to_entity(self, row: dict) -> Worker:
        """Map database row to Worker entity"""
        
        return Worker(
            worker_id=row['worker_id'],
            employee_code=row['employee_code'],
            full_name=row['full_name'],
            department=row['department'],
            role=row['role'],
            is_authorized=row['is_authorized'],
            status=WorkerStatus(row['status']),
            registration_date=row['registration_date'],
            contact_info=row['contact_info'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    

        
        
        