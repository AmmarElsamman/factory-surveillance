-- ============================================
-- Sample Data for Testing
-- ============================================

-- Insert Sample Cameras
INSERT INTO cameras (camera_id, location_name, zone_type, coordinates) VALUES
('CAM_001', 'Main Entrance', 'general', '{"x": 0, "y": 0}'),
('CAM_002', 'Assembly Line A', 'general', '{"x": 50, "y": 20}'),
('CAM_003', 'Assembly Line B', 'general', '{"x": 50, "y": 40}'),
('CAM_004', 'Warehouse', 'restricted', '{"x": 100, "y": 30}'),
('CAM_005', 'Loading Dock', 'general', '{"x": 120, "y": 50}'),
('CAM_006', 'Office Area', 'office', '{"x": 30, "y": 60}');

-- Insert Sample Workers
INSERT INTO workers (employee_code, full_name, department, role) VALUES
('EMP001', 'John Doe', 'Manufacturing', 'Assembly Worker'),
('EMP002', 'Jane Smith', 'Manufacturing', 'Line Supervisor'),
('EMP003', 'Bob Johnson', 'Warehouse', 'Forklift Operator'),
('EMP004', 'Alice Williams', 'Warehouse', 'Inventory Manager'),
('EMP005', 'Charlie Brown', 'Maintenance', 'Technician'),
('EMP006', 'Diana Prince', 'Quality Control', 'Inspector'),
('EMP007', 'Eve Davis', 'Manufacturing', 'Assembly Worker'),
('EMP008', 'Frank Miller', 'Security', 'Guard');

-- Insert Sample Global Tracks (some active workers)
INSERT INTO global_tracks (worker_id, current_camera_id, track_status, first_seen, last_seen, confidence_level, helmet_status) VALUES
(
    (SELECT worker_id FROM workers WHERE employee_code = 'EMP001'),
    'CAM_002',
    'active',
    NOW() - INTERVAL '30 minutes',
    NOW() - INTERVAL '2 minutes',
    95,
    'compliant'
),
(
    (SELECT worker_id FROM workers WHERE employee_code = 'EMP003'),
    'CAM_004',
    'active',
    NOW() - INTERVAL '1 hour',
    NOW() - INTERVAL '1 minute',
    92,
    'violation'
);

-- Insert Sample Detection Events
INSERT INTO detection_events (global_track_id, camera_id, timestamp, bounding_box, helmet_detected, confidence_score, local_track_id)
SELECT 
    gt.global_track_id,
    gt.current_camera_id,
    NOW() - (random() * INTERVAL '30 minutes'),
    json_build_object('x', floor(random() * 1920)::int, 'y', floor(random() * 1080)::int, 'width', 80, 'height', 200)::jsonb,
    random() > 0.3,  -- 70% wearing helmets
    0.85 + (random() * 0.14),  -- confidence between 0.85 and 0.99
    'CAM_' || gt.current_camera_id || '_T' || lpad(floor(random() * 100)::text, 3, '0')
FROM global_tracks gt
CROSS JOIN generate_series(1, 20);  -- 20 detections per track

-- Insert Sample Alerts
INSERT INTO alerts (alert_type, global_track_id, camera_id, timestamp, severity, status, description) VALUES
(
    'helmet_violation',
    (SELECT global_track_id FROM global_tracks WHERE helmet_status = 'violation' LIMIT 1),
    'CAM_004',
    NOW() - INTERVAL '5 minutes',
    'high',
    'new',
    'Worker detected without helmet in warehouse area'
),
(
    'intruder',
    gen_random_uuid(),
    'CAM_001',
    NOW() - INTERVAL '15 minutes',
    'critical',
    'acknowledged',
    'Unidentified person detected at main entrance'
);