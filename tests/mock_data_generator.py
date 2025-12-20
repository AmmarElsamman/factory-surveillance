import random
import uuid
from datetime import datetime, timedelta
import json
import numpy as np

# ---------------------------
# Utility Functions
# ---------------------------

def rand_dt(minutes_back=60):
    now = datetime.now()
    return now - timedelta(minutes=random.randint(1, minutes_back))

def random_bbox():
    x = random.randint(100, 1500)
    y = random.randint(100, 800)
    w = random.randint(60, 120)
    h = random.randint(160, 260)
    return {"x": x, "y": y, "width": w, "height": h}

def random_embedding(dim=512):
    """Generate a unit-normalized embedding for realistic ReID."""
    v = np.random.randn(dim)
    v = v / np.linalg.norm(v)
    return v.tolist()

# ----------------------------------
# Mock Workers
# ----------------------------------

def generate_workers(n=10):
    names = ["Omar", "Alaa", "Youssef", "Karim", "Mostafa",
             "Hassan", "Ibrahim", "Mahmoud", "Fares", "Adham"]
    
    workers = []
    for i in range(n):
        wid = uuid.uuid4()
        workers.append({
            "worker_id": str(wid),
            "employee_code": f"EMP-{1000+i}",
            "full_name": random.choice(names) + " " + random.choice(["Ali", "Hamed", "Salem", "Younes"]),
            "department": random.choice(["Production", "Packaging", "Maintenance", "QC", "Warehouse"]),
            "role": random.choice(["Engineer", "Technician", "Supervisor", "Operator"]),
            "is_authorized": random.choice([True, True, True, False]),
            "registration_date": rand_dt().isoformat(),
            "status": random.choice(["active", "inactive"]),
            "contact_info": {"phone": f"+2010{random.randint(10000000,99999999)}"},
            "photo_url": "",
        })
    return workers

# ----------------------------------
# Mock Cameras
# ----------------------------------

def generate_cameras():
    return [
        {"camera_id": "CAM_001", "location_name": "Entrance A", "zone_type": "entry"},
        {"camera_id": "CAM_002", "location_name": "Production Line 1", "zone_type": "production"},
        {"camera_id": "CAM_003", "location_name": "Warehouse North", "zone_type": "storage"},
        {"camera_id": "CAM_004", "location_name": "Packing Area", "zone_type": "packing"},
    ]

# ----------------------------------
# Mock Global Tracks
# ----------------------------------

def generate_global_tracks(workers, num_tracks=20):
    tracks = []

    for _ in range(num_tracks):
        w = random.choice(workers)
        track_id = uuid.uuid4()
        cam = random.choice(["CAM_001", "CAM_002", "CAM_003", "CAM_004"])
        first = rand_dt()
        last = first + timedelta(seconds=random.randint(4, 40))

        tracks.append({
            "global_track_id": str(track_id),
            "worker_id": w["worker_id"] if random.random() > 0.15 else None,  # 15% intruder probability
            "current_camera_id": cam,
            "track_status": "active",
            "first_seen": first.isoformat(),
            "last_seen": last.isoformat(),
            "confidence_level": random.randint(40, 99),
            "is_intruder_suspect": random.choice([False, False, True]),
            "helmet_status": random.choice(["wearing", "not_wearing", "unknown"]),
        })
    return tracks

# ----------------------------------
# Mock Detection Events
# ----------------------------------

def generate_detection_events(global_tracks):
    detections = []
    for t in global_tracks:
        num_det = random.randint(2, 6)
        for _ in range(num_det):
            detections.append({
                "global_track_id": t["global_track_id"],
                "camera_id": t["current_camera_id"],
                "timestamp": rand_dt().isoformat(),
                "bounding_box": random_bbox(),
                "helmet_detected": random.choice([True, True, False]),
                "confidence_score": round(random.uniform(0.85, 0.99), 3),
                "local_track_id": f"{t['current_camera_id']}_T{random.randint(10,999)}",
            })
    return detections

# ----------------------------------
# Mock Worker Embeddings
# ----------------------------------

def generate_embeddings(workers):
    embeddings = []
    for w in workers:
        for _ in range(random.randint(1, 4)):  # multiple samples per worker
            embeddings.append({
                "worker_id": w["worker_id"],
                "feature_vector": random_embedding(),
                "quality_score": round(random.uniform(0.7, 0.99), 3),
                "capture_timestamp": rand_dt().isoformat(),
                "camera_id": random.choice(["CAM_001","CAM_002","CAM_003","CAM_004"]),
                "is_primary": random.choice([True, False, False]),
            })
    return embeddings

# ----------------------------------
# Mock Alerts
# ----------------------------------

def generate_alerts(global_tracks):
    alerts = []
    for t in global_tracks:
        if random.random() < 0.2:  # 20% tracks trigger alerts
            alerts.append({
                "alert_type": random.choice(["helmet_violation", "intruder_alert"]),
                "global_track_id": t["global_track_id"],
                "camera_id": t["current_camera_id"],
                "timestamp": rand_dt().isoformat(),
                "severity": random.choice(["low","medium","high"]),
                "status": "new",
                "description": "Auto-generated test alert",
                "assigned_to": None,
                "related_events": [],
            })
    return alerts

# ----------------------------------
# Mock Trajectory
# ----------------------------------

def generate_trajectories(global_tracks):
    traj = []
    for t in global_tracks:
        sections = random.randint(1, 4)
        prev = rand_dt()
        for step in range(sections):
            start = prev
            end = start + timedelta(seconds=random.randint(1, 30))
            traj.append({
                "global_track_id": t["global_track_id"],
                "camera_id": t["current_camera_id"],
                "entry_time": start.isoformat(),
                "exit_time": end.isoformat(),
                "duration": str(end - start),
                "path_sequence": step+1
            })
            prev = end
    return traj

# ----------------------------------
# MAIN
# ----------------------------------

if __name__ == "__main__":
    workers = generate_workers()
    cameras = generate_cameras()
    tracks = generate_global_tracks(workers)
    events = generate_detection_events(tracks)
    embeds = generate_embeddings(workers)
    alerts = generate_alerts(tracks)
    trajectories = generate_trajectories(tracks)

    output = {
        "workers": workers,
        "cameras": cameras,
        "global_tracks": tracks,
        "detection_events": events,
        "embeddings": embeds,
        "alerts": alerts,
        "trajectory": trajectories
    }

    with open("mock_surveillance_data.json", "w") as f:
        json.dump(output, f, indent=2)

    print("✓ mock_surveillance_data.json generated successfully!")
