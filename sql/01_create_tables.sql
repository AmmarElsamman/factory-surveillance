-- ============================================
-- Factory Surveillance Database Schema
-- ============================================

-- Workers Table
CREATE TABLE workers (
    worker_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    role VARCHAR(100),
    is_authorized BOOLEAN DEFAULT true,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    contact_info JSONB,
    photo_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cameras Table
CREATE TABLE cameras (
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

-- Global Tracks Table
CREATE TABLE global_tracks (
    global_track_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id UUID REFERENCES workers(worker_id),
    current_camera_id VARCHAR(50) REFERENCES cameras(camera_id),
    track_status VARCHAR(20) DEFAULT 'active',
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    confidence_level INTEGER CHECK (confidence_level BETWEEN 0 AND 100),
    is_intruder_suspect BOOLEAN DEFAULT false,
    helmet_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detection Events Table
CREATE TABLE detection_events (
    event_id BIGSERIAL PRIMARY KEY,
    global_track_id UUID REFERENCES global_tracks(global_track_id),
    camera_id VARCHAR(50) REFERENCES cameras(camera_id),
    timestamp TIMESTAMP NOT NULL,
    bounding_box JSONB NOT NULL,
    helmet_detected BOOLEAN,
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    snapshot_url VARCHAR(500),
    local_track_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Worker Embeddings Table
CREATE TABLE worker_embeddings (
    embedding_id BIGSERIAL PRIMARY KEY,
    worker_id UUID REFERENCES workers(worker_id),
    feature_vector vector(512),
    quality_score FLOAT,
    capture_timestamp TIMESTAMP,
    camera_id VARCHAR(50) REFERENCES cameras(camera_id),
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts Table
CREATE TABLE alerts (
    alert_id BIGSERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    global_track_id UUID REFERENCES global_tracks(global_track_id),
    camera_id VARCHAR(50) REFERENCES cameras(camera_id),
    timestamp TIMESTAMP NOT NULL,
    severity VARCHAR(20),
    status VARCHAR(30) DEFAULT 'new',
    description TEXT,
    assigned_to VARCHAR(100),
    resolution_notes TEXT,
    related_events BIGINT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Track Trajectory Table
CREATE TABLE track_trajectory (
    trajectory_id BIGSERIAL PRIMARY KEY,
    global_track_id UUID REFERENCES global_tracks(global_track_id),
    camera_id VARCHAR(50) REFERENCES cameras(camera_id),
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP,
    duration INTERVAL,
    path_sequence INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System Logs Table (for debugging)
CREATE TABLE system_logs (
    log_id BIGSERIAL PRIMARY KEY,
    log_level VARCHAR(20),
    component VARCHAR(100),
    message TEXT,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);