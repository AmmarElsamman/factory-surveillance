"""
Unit of Work Pattern
Groups repository operations into atomic transactions
"""
from typing import Optional
from .connection import db_connection

from .Repositories.Worker_repository import WorkerRepository
from .Repositories.Camera_repository import CameraRepository
from .Repositories.WorkerEmbedding_Repository import WorkerEmbeddingRepository
from Utils.logger import get_logger

logger = get_logger(__name__)

class UnitOfWork:
    """
    Unit of Work pattern implementation
    Ensures all repository operations happen in a single transaction
    """
    
    def __init__(self):
        self._connection = None
        self._cursor = None
        self.workers: Optional[WorkerRepository] = None
        self.cameras: Optional[CameraRepository] = None
        self.worker_embeddings: Optional[WorkerEmbeddingRepository] = None
        
    def __enter__(self):
        """Enter context manager"""
        
        self._connection = db_connection._pool.getconn()
        self._cursor = self._connection.cursor()
        
        # * Initialize repositories with the same cursor (same connection / same transaction)
        self.workers = WorkerRepository(self._cursor)
        self.cameras = CameraRepository(self._cursor)
        self.worker_embeddings = WorkerEmbeddingRepository(self._cursor)
        
        logger.debug("UnitOfWork started")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        
        try:
            if exc_type is None:
                # No exception, commit
                self._connection.commit()
                logger.debug("UnitOfWork committed")
            else:
                #Exception occurred, rollback
                self._connection.rollback()
                logger.warning(f"UnitOfWork rolled back due to: {exc_val}")
        finally:
            if self._cursor:
                self._cursor.close()
            if self._connection:
                db_connection._pool.putconn(self._connection)
            logger.debug("UnitOfWork closed")
    
    def commit(self):
        """Explicitly commit transaction"""
        self._connection.commit()
        logger.debug("UnitOfWork explicitly committed")