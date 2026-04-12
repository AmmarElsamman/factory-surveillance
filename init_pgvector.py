"""Initialize pgvector extension and create tables"""
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

def init_pgvector():
    """Initialize pgvector extension and create embedding table"""
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    
    cursor = conn.cursor()
    
    try:
        # Create pgvector extension
        print("Creating pgvector extension...")
        cursor.execute('CREATE EXTENSION IF NOT EXISTS vector;')
        
        # Create workers table
        print("Creating workers table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workers (
                worker_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                employee_code VARCHAR(50) UNIQUE NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                department VARCHAR(100),
                role VARCHAR(100),
                is_authorized BOOLEAN DEFAULT TRUE,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active',
                contact_info JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        print("Creating cameras table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cameras (
                camera_id VARCHAR(50) PRIMARY KEY,
                location_name VARCHAR(255) NOT NULL,
                zone_type VARCHAR(50),
                coordinates JSONB,
                ip_address INET,
                status VARCHAR(20) DEFAULT 'online',
                field_of_view JSONB,
                installation_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Create embeddings table with pgvector
        print("Creating embeddings table with pgvector...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS worker_embeddings (
                embedding_id BIGSERIAL PRIMARY KEY,
                worker_id UUID REFERENCES workers(worker_id),
                feature_vector vector(512),
                quality_score FLOAT,
                capture_timestamp TIMESTAMP,
                camera_id VARCHAR(50) REFERENCES cameras(camera_id),
                is_primary BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Create indexes for faster queries
        print("Creating indexes...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_worker_embeddings_worker_id 
            ON worker_embeddings(worker_id);
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_workers_employee_code ON workers(employee_code);
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_workers_status ON workers(status);
        ''')
        
        # Create similarity search index (IVFFlat for speed, HNSW for accuracy)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_worker_embeddings_vector 
            ON worker_embeddings USING ivfflat (feature_vector vector_cosine_ops)
            WITH (lists = 100);
        ''')
        
        # Insert sample cameras
        print("Inserting sample cameras...")
        cursor.execute('''
            INSERT INTO cameras (
                camera_id, location_name, zone_type, coordinates, ip_address,
                status, field_of_view, installation_date
            ) VALUES
            ('CAM-001', 'Main Gate Entrance', 'Entrance', '{"lat": 30.0444, "lng": 31.2357}', '192.168.1.10',
             'online', '{"angle": 120, "range_meters": 30}', '2024-01-10'),
            ('CAM-002', 'Warehouse Zone A', 'Warehouse', '{"lat": 30.0451, "lng": 31.2362}', '192.168.1.11',
             'online', '{"angle": 90, "range_meters": 40}', '2024-01-12'),
            ('CAM-003', 'Parking Area', 'Outdoor', '{"lat": 30.0438, "lng": 31.2349}', '192.168.1.12',
             'offline', '{"angle": 140, "range_meters": 50}', '2024-01-15'),
            ('CAM-004', 'Control Room', 'Indoor', '{"lat": 30.0449, "lng": 31.2351}', '192.168.1.13',
             'online', '{"angle": 110, "range_meters": 20}', '2024-01-18'),
            ('CAM-005', 'Back Exit', 'Exit', '{"lat": 30.0440, "lng": 31.2370}', '192.168.1.14',
             'maintenance', '{"angle": 100, "range_meters": 25}', '2024-01-20')
            ON CONFLICT (camera_id) DO NOTHING;
        ''')
        
        # Insert sample workers
        print("Inserting sample workers...")
        cursor.execute('''
            INSERT INTO workers (
                employee_code, full_name, department, role, is_authorized, status, contact_info
            ) VALUES
            ('EMP-001', 'Ahmed Hassan', 'Security', 'Security Officer', true, 'active',
             '{"phone": "+201001112233", "email": "ahmed.hassan@company.com"}'),
            ('EMP-002', 'Mohamed Ali', 'Operations', 'Shift Supervisor', true, 'active',
             '{"phone": "+201022233344", "email": "mohamed.ali@company.com"}'),
            ('EMP-003', 'Sara Ibrahim', 'Administration', 'HR Specialist', false, 'inactive',
             '{"phone": "+201033344455", "email": "sara.ibrahim@company.com"}'),
            ('EMP-004', 'Omar Youssef', 'IT', 'System Administrator', true, 'active',
             '{"phone": "+201044455566", "email": "omar.youssef@company.com"}'),
            ('EMP-005', 'Mona Abdelrahman', 'Security', 'Control Room Operator', true, 'active',
             '{"phone": "+201055566677", "email": "mona.abdelrahman@company.com"}')
            ON CONFLICT (employee_code) DO NOTHING;
        ''')
        
        
        conn.commit()
        print("✅ pgvector setup complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_pgvector()