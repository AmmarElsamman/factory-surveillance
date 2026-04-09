-- ============================================
-- Sample Data for Testing
-- ============================================

-- Insert Sample Cameras
INSERT INTO cameras (
    camera_id,
    location_name,
    zone_type,
    coordinates,
    ip_address,
    status,
    field_of_view,
    installation_date
) VALUES
(
    'CAM-001',
    'Main Gate Entrance',
    'Entrance',
    '{"lat": 30.0444, "lng": 31.2357}',
    '192.168.1.10',
    'online',
    '{"angle": 120, "range_meters": 30}',
    '2024-01-10'
),
(
    'CAM-002',
    'Warehouse Zone A',
    'Warehouse',
    '{"lat": 30.0451, "lng": 31.2362}',
    '192.168.1.11',
    'online',
    '{"angle": 90, "range_meters": 40}',
    '2024-01-12'
),
(
    'CAM-003',
    'Parking Area',
    'Outdoor',
    '{"lat": 30.0438, "lng": 31.2349}',
    '192.168.1.12',
    'offline',
    '{"angle": 140, "range_meters": 50}',
    '2024-01-15'
),
(
    'CAM-004',
    'Control Room',
    'Indoor',
    '{"lat": 30.0449, "lng": 31.2351}',
    '192.168.1.13',
    'online',
    '{"angle": 110, "range_meters": 20}',
    '2024-01-18'
),
(
    'CAM-005',
    'Back Exit',
    'Exit',
    '{"lat": 30.0440, "lng": 31.2370}',
    '192.168.1.14',
    'maintenance',
    '{"angle": 100, "range_meters": 25}',
    '2024-01-20'
);


-- Insert Sample Workers
INSERT INTO workers (
    employee_code,
    full_name,
    department,
    role,
    is_authorized,
    status,
    contact_info
) VALUES
(
    'EMP-001',
    'Ahmed Hassan',
    'Security',
    'Security Officer',
    true,
    'active',
    '{"phone": "+201001112233", "email": "ahmed.hassan@company.com"}'
),
(
    'EMP-002',
    'Mohamed Ali',
    'Operations',
    'Shift Supervisor',
    true,
    'active',
    '{"phone": "+201022233344", "email": "mohamed.ali@company.com"}'
),
(
    'EMP-003',
    'Sara Ibrahim',
    'Administration',
    'HR Specialist',
    false,
    'inactive',
    '{"phone": "+201033344455", "email": "sara.ibrahim@company.com"}'
),
(
    'EMP-004',
    'Omar Youssef',
    'IT',
    'System Administrator',
    true,
    'active',
    '{"phone": "+201044455566", "email": "omar.youssef@company.com"}'
),
(
    'EMP-005',
    'Mona Abdelrahman',
    'Security',
    'Control Room Operator',
    true,
    'active',
    '{"phone": "+201055566677", "email": "mona.abdelrahman@company.com"}'
);
