"""
Database connection management with pooling
"""
from contextlib import contextmanager
from typing import Generator
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor


from Utils.logger import get_logger
from config.settings import settings


logger = get_logger(__name__)

class DatabaseConnection:
    """
    Database connection manager
    Singleton pattern
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self._pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.database_host,
                port=settings.database_port,
                database=settings.database_name,
                user=settings.database_user,
                password=settings.database_password,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator:
        """
        Context manager for database connection
        Automatically handles connection cleanup
        """
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)
    
    def close_all(self):
        """Close all connections in the pool"""
        if self._pool:
            self._pool.closeall()
            logger.info("All database connections closed")

db_connection = DatabaseConnection()