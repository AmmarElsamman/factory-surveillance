import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Create and return database connection"""
    return psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        cursor_factory=RealDictCursor  # Returns results as dictionaries
    )

def test_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print("✓ Database connection successful!")
        print(f"PostgreSQL version: {version['version']}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()