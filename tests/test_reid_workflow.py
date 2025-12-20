"""
Test the complete Re-ID workflow
"""

from os import name
import requests
import time
from typing import List
import random

BASE_URL = "http://localhost:8000"

def generate_fake_embedding(base_value: float = 0.5, variation: float = 0.1) -> List[float]:
    """Generate fake embedding that's similar to base_value"""
    return [base_value + random.uniform(-variation, variation) for _ in range(512)]

def test_complete_reid_workflow():
    """
    Simulate complete Re-ID
    workflow from detection to tracking
"""
print("\n" + "="*60)
print(" TESTING COMPLETE RE-ID WORKFLOW ")
print("="*60)

# Step 1: Register a worker with their embedding
print("\n[Step 1] Registering Worker 'John Doe' with embedding...")

# Get a worker from database
workers_response = requests.get(f"{BASE_URL}/api/workers")
john = workers_response.json()['workers'][0]  # First worker
john_id = john['worker_id']
print(f"  Worker ID: {john_id}")
print(f"  Name: {john['full_name']}")

# Store primary embedding for John
john_embedding = generate_fake_embedding(base_value=0.5, variation=0.05)

store_response = requests.post(
    f"{BASE_URL}/api/reid/embeddings/store",
    params={
        "worker_id": john_id,
        "camera_id": "CAM_001",
        "quality_score": 0.95,
        "is_primary": True
    },
    json=john_embedding
)
print(f"  ✓ Embedding stored: {store_response.json()}")

# Step 2: John enters at Camera 1
print("\n[Step 2] John enters at Camera 1...")

# Simulate detection with similar embedding
john_detection_embedding = generate_fake_embedding(base_value=0.5, variation=0.03)

search_response = requests.post(
    f"{BASE_URL}/api/reid/search-embedding",
    json={
        "feature_vector": john_detection_embedding,
        "threshold": 0.85,
        "max_results": 5,
        "search_active_only": False
    }
)

search_result = search_response.json()
print(f"  Search results: {search_result['count']} matches")

if search_result['matches']:
    best_match = search_result['matches'][0]
    print(f"  Best match: {best_match['worker_name']}")
    print(f"  Similarity: {best_match['similarity_score']:.4f}")
    
    if best_match['similarity_score'] >= 0.85:
        print("  ✓ Strong match - Creating/updating global track")
        
        # Create global track for John
        track_response = requests.post(
            f"{BASE_URL}/api/reid/tracks/create",
            json={
                "worker_id": john_id,
                "camera_id": "CAM_001",
                "local_track_id": "CAM_001_T001",
                "confidence_level": int(best_match['similarity_score'] * 100),
                "helmet_status": "compliant"
            }
        )
        
        john_track_id = track_response.json()['global_track_id']
        print(f"  Global Track ID: {john_track_id}")

time.sleep(2)

# Step 3: John moves to Camera 2
print("\n[Step 3] John moves to Camera 2...")

# Search again with slightly different embedding (different angle)
john_cam2_embedding = generate_fake_embedding(base_value=0.5, variation=0.04)

search_response2 = requests.post(
    f"{BASE_URL}/api/reid/search-embedding",
    json={
        "feature_vector": john_cam2_embedding,
        "threshold": 0.85,
        "max_results": 5,
        "search_active_only": True  # Search only active tracks
    }
)

search_result2 = search_response2.json()
print(f"  Active track search: {search_result2['count']} matches")

if search_result2['matches']:
    match = search_result2['matches'][0]
    print(f"  Matched to: {match['worker_name']}")
    print(f"  Previous location: {match['current_camera_id']}")
    print(f"  Similarity: {match['similarity_score']:.4f}")
    
    # Update track location
    print("  ✓ Updating track location to CAM_002")
    update_response = requests.put(
        f"{BASE_URL}/api/reid/tracks/{john_track_id}",
        json={
            "current_camera_id": "CAM_002",
            "helmet_status": "compliant"
        }
    )
    print(f"  Update result: {update_response.json()}")

time.sleep(2)

# Step 4: Unknown person appears at Camera 3
print("\n[Step 4] Unknown person appears at Camera 3...")

# Generate completely different embedding (intruder)
intruder_embedding = generate_fake_embedding(base_value=0.9, variation=0.05)

search_response3 = requests.post(
    f"{BASE_URL}/api/reid/search-embedding",
    json={
        "feature_vector": intruder_embedding,
        "threshold": 0.85,
        "max_results": 5,
        "search_active_only": False
    }
)

search_result3 = search_response3.json()
print(f"  Search results: {search_result3['count']} matches")

if not search_result3['matches'] or search_result3['matches'][0]['similarity_score'] < 0.85:
    print("  ⚠️ No match found - Potential intruder!")
    
    # Create track for unknown person
    intruder_response = requests.post(
        f"{BASE_URL}/api/reid/tracks/create",
        json={
            "worker_id": None,  # Unknown!
            "camera_id": "CAM_003",
            "local_track_id": "CAM_003_T015",
            "confidence_level": 0,
            "helmet_status": "unknown"
        }
    )
    
    intruder_track_id = intruder_response.json()['global_track_id']
    print(f"  Created new track: {intruder_track_id}")
    print(f"  Intruder suspect: {intruder_response.json()['is_intruder_suspect']}")
    print("  ✓ Alert should be generated")

time.sleep(2)

# Step 5: Check current system state
print("\n[Step 5] Checking system state...")

# Get active tracks
active_response = requests.get(f"{BASE_URL}/api/reid/active-tracks")
active_tracks = active_response.json()
print(f"  Active tracks: {active_tracks['count']}")

for track in active_tracks['active_tracks']:
    print(f"    - {track['full_name'] or 'UNKNOWN'} at {track['location_name']}")

# Get recent alerts
alerts_response = requests.get(f"{BASE_URL}/api/alerts?hours=1")
alerts = alerts_response.json()
print(f"\n  Recent alerts: {len(alerts)}")

for alert in alerts:
    print(f"    - {alert['alert_type']} at {alert['location_name']} ({alert['severity']})")

# Step 6: Query John's location
print(f"\n[Step 6] Finding John's current location...")

location_response = requests.get(f"{BASE_URL}/api/workers/{john_id}/location")
if location_response.status_code == 200:
    location = location_response.json()
    print(f"  {location['full_name']} is at: {location['location_name']}")
    print(f"  Camera: {location['camera_id']}")
    print(f"  Last seen: {location['last_seen']}")
    print(f"  Helmet status: {location['helmet_status']}")
else:
    print("  Worker not currently tracked")

print("\n" + "="*60)
print(" ✓ WORKFLOW TEST COMPLETE ")
print("="*60)

def test_embedding_similarity():
    """Test that similar embeddings match"""
    print("\n" + "="*60)
    print(" TESTING EMBEDDING SIMILARITY ")
    print("="*60)
    # Create base embedding
    base_embedding = generate_fake_embedding(base_value=0.5, variation=0.01)

    # Create similar embeddings with increasing variation
    variations = [0.01, 0.05, 0.10, 0.20, 0.30]

    print("\nTesting similarity with different variations:")
    print("Base embedding value: ~0.5")
    print("-" * 60)

    for var in variations:
        similar_embedding = generate_fake_embedding(base_value=0.5, variation=var)
        
        # This would need to be done by your ReID system
        # For now, we'll just show the concept
        print(f"\nVariation: ±{var}")
        print(f"  Expected similarity: {1.0 - var:.2f}")
        print(f"  Would match? {var <= 0.15}")
        
def test_intruder_detection():
    """Test intruder detection logic"""
    print("\n" + "="*60)
    print(" TESTING INTRUDER DETECTION ")
    print("="*60)
    # Generate completely different embedding
    intruder_embedding = generate_fake_embedding(base_value=0.95, variation=0.02)

    print("\nSearching for completely different embedding...")

    search_response = requests.post(
        f"{BASE_URL}/api/reid/search-embedding",
        json={
            "feature_vector": intruder_embedding,
            "threshold": 0.85,
            "max_results": 5,
            "search_active_only": False
        }
    )

    result = search_response.json()

    if not result['matches'] or result['matches'][0]['similarity_score'] < 0.85:
        print("✓ No match found - This would trigger intruder detection")
        print("\nIntruder detection logic:")
        print("  1. No match with similarity >= 0.85")
        print("  2. Wait 120 seconds (maybe bad angle)")
        print("  3. Still no match → Create alert")
        print("  4. Notify security personnel")
    else:
        print("✗ Unexpected match found")
        print(f"  Best match: {result['matches'][0]}")
        
def test_track_lifecycle():
    """Test complete track lifecycle"""
    print("\n" + "="*60)
    print(" TESTING TRACK LIFECYCLE ")
    print("="*60)
    # Get a worker
    workers_response = requests.get(f"{BASE_URL}/api/workers")
    worker = workers_response.json()['workers'][0]
    worker_id = worker['worker_id']

    print(f"\n1. Creating track for {worker['full_name']}...")

    # Create track
    create_response = requests.post(
        f"{BASE_URL}/api/reid/tracks/create",
        json={
            "worker_id": worker_id,
            "camera_id": "CAM_001",
            "local_track_id": "CAM_001_TEST",
            "confidence_level": 95,
            "helmet_status": "compliant"
        }
    )

    track_id = create_response.json()['global_track_id']
    print(f"   ✓ Track created: {track_id}")

    time.sleep(1)

    print("\n2. Worker moves to Camera 2...")

    # Update location
    update_response = requests.put(
        f"{BASE_URL}/api/reid/tracks/{track_id}",
        json={
            "current_camera_id": "CAM_002",
            "helmet_status": "compliant"
        }
    )

    print(f"   ✓ Track updated: {update_response.json()}")

    time.sleep(1)

    print("\n3. Worker moves to Camera 3...")

    # Update again
    update_response2 = requests.put(
        f"{BASE_URL}/api/reid/tracks/{track_id}",
        json={
            "current_camera_id": "CAM_003",
            "helmet_status": "violation"
        }
    )

    print(f"   ✓ Track updated: {update_response2.json()}")

    time.sleep(1)

    print("\n4. Worker leaves premises...")

    # Close track
    close_response = requests.post(
        f"{BASE_URL}/api/reid/tracks/{track_id}/close"
    )

    print(f"   ✓ Track closed: {close_response.json()}")

    print("\n5. Checking trajectory...")

    # This would need a trajectory endpoint
    print("   Track trajectory:")
    print("     CAM_001 (entry) → CAM_002 → CAM_003 → (exit)")
    
if name == "main":
    # Make sure API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            raise Exception("API not healthy")
    except:
        print("✗ Error: API is not running!")
        print("Please start the API first:")
        print("  python src/main.py")
        exit(1)
    
    print("\n" + "="*60)
    print(" RE-IDENTIFICATION SYSTEM TESTS ")
    print("="*60)

    # Run tests
    test_complete_reid_workflow()
    time.sleep(2)

    test_embedding_similarity()
    time.sleep(2)

    test_intruder_detection()
    time.sleep(2)

    test_track_lifecycle()

    print("\n" + "="*60)
    print(" ALL RE-ID TESTS COMPLETE ")
    print("="*60)