import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*50)
    print("Testing Health Endpoint")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_get_cameras():
    """Test getting cameras"""
    print("\n" + "="*50)
    print("Testing Get Cameras")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/cameras")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data['cameras'])} cameras")
    for cam in data['cameras']:
        print(f"  - {cam['camera_id']}: {cam['location_name']}")

def test_get_workers():
    """Test getting workers"""
    print("\n" + "="*50)
    print("Testing Get Workers")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/workers")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data['workers'])} workers")
    for worker in data['workers'][:3]:  # Show first 3
        print(f"  - {worker['employee_code']}: {worker['full_name']} ({worker['department']})")

def test_create_detection():
    """Test creating detection event"""
    print("\n" + "="*50)
    print("Testing Create Detection")
    print("="*50)
    
    detection_data = {
        "camera_id": "CAM_002",
        "timestamp": datetime.now().isoformat(),
        "detections": [
            {
                "local_track_id": "CAM_002_TEST_001",
                "bounding_box": {
                    "x": 500,
                    "y": 300,
                    "width": 80,
                    "height": 200
                },
                "person_confidence": 0.95,
                "helmet_detected": False,  # Violation!
                "helmet_confidence": 0.89
            }
        ]
    }
    
    print("Sending detection with helmet violation...")
    response = requests.post(
        f"{BASE_URL}/api/detections",
        json=detection_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201

def test_get_alerts():
    """Test getting alerts"""
    print("\n" + "="*50)
    print("Testing Get Alerts")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/alerts")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} alerts")
    
    for alert in data[:3]:  # Show first 3
        print(f"\n  Alert #{alert['alert_id']}:")
        print(f"    Type: {alert['alert_type']}")
        print(f"    Location: {alert['location_name']}")
        print(f"    Severity: {alert['severity']}")
        print(f"    Status: {alert['status']}")

def test_get_stats():
    """Test statistics endpoint"""
    print("\n" + "="*50)
    print("Testing Statistics")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/stats/summary")
    print(f"Status: {response.status_code}")
    stats = response.json()
    
    print(f"\nActive Workers: {stats['active_workers']}")
    print(f"Recent Alerts: {stats['recent_alerts']}")
    print(f"\nHelmet Compliance Today:")
    compliance = stats['helmet_compliance_today']
    print(f"  Compliant: {compliance['compliant']}")
    print(f"  Violations: {compliance['violations']}")
    print(f"  Total: {compliance['total']}")
    print(f"  Compliance Rate: {compliance['compliance_rate_percent']}%")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print(" RUNNING API TESTS ")
    print("="*60)
    
    try:
        test_health()
        test_get_cameras()
        test_get_workers()
        test_create_detection()
        time.sleep(1)  # Wait a moment
        test_get_alerts()
        test_get_stats()
        
        print("\n" + "="*60)
        print(" ✓ ALL TESTS PASSED ")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise

if __name__ == "__main__":
    # Make sure API is running first!
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print("✗ Error: API is not running!")
        print("Please start the API first:")
        print("  python src/main.py")
        exit(1)
    
    run_all_tests()