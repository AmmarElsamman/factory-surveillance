-- ============================================
-- Indexes for Performance
-- ============================================

-- Detection Events Indexes
CREATE INDEX idx_detection_events_timestamp ON detection_events(timestamp DESC);
CREATE INDEX idx_detection_events_camera ON detection_events(camera_id, timestamp DESC);
CREATE INDEX idx_detection_events_track ON detection_events(global_track_id);

-- Global Tracks Indexes
CREATE INDEX idx_global_tracks_worker ON global_tracks(worker_id);
CREATE INDEX idx_global_tracks_status ON global_tracks(track_status);
CREATE INDEX idx_global_tracks_last_seen ON global_tracks(last_seen DESC);
CREATE INDEX idx_global_tracks_camera ON global_tracks(current_camera_id);

-- Alerts Indexes
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX idx_alerts_status ON alerts(status, severity);
CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_camera ON alerts(camera_id, timestamp DESC);

-- Trajectory Indexes
CREATE INDEX idx_trajectory_track ON track_trajectory(global_track_id, entry_time DESC);
CREATE INDEX idx_trajectory_camera ON track_trajectory(camera_id, entry_time DESC);

-- Worker Embeddings Indexes
CREATE INDEX idx_embeddings_worker ON worker_embeddings(worker_id);
CREATE INDEX ON worker_embeddings USING ivfflat (feature_vector vector_cosine_ops);

-- Workers Indexes
CREATE INDEX idx_workers_employee_code ON workers(employee_code);
CREATE INDEX idx_workers_status ON workers(status);