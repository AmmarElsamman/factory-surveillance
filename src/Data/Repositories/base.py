"""
Base Repository with common operations
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    """
    Repository interface
    Defines standard CRUD operations
    """
    
    @abstractmethod
    def add(self, entity: T) -> str:
        """Add new entity"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        """Update existing entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete entity"""
        pass
    
    @abstractmethod
    def list_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """List all entities with pagination"""
        pass

class BaseRepository(Generic[T]):
    """
    Base repository implementation with common functionality
    """
    
    def __init__(self, cursor):
        self._cursor = cursor
    
    def _execute(self, query: str, params: tuple = ()):
        """Execute query with error handling"""
        try:
            self._cursor.execute(query, params)
        except Exception as e:
            raise RuntimeError(f"Database query failed: {e}")
    
    def _fetch_one(self):
        """Fetch one result"""
        return self._cursor.fetchone()
    
    def _fetch_all(self):
        """Fetch all results"""
        return self._cursor.fetchall()