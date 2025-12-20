# debug_camera_data.py
from database import CameraRepository, db_manager

def debug_camera_data():
    print("Testing database connection and data retrieval...")
    
    # Test connection
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT camera_id, location_name FROM cameras LIMIT 1")
            result = cursor.fetchone()
            if result:
                print(f"✓ Found camera: {result['camera_id']} - {result['location_name']}")
            else:
                print("✗ No cameras found in database")
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return
    
    # Test getting all cameras
    print("\nGetting all cameras...")
    cameras = CameraRepository.get_all_cameras()
    print(f"Found {len(cameras)} cameras")
    
    if cameras:
        for i, camera in enumerate(cameras[:3]):  # Show first 3
            print(f"\nCamera {i+1}:")
            print(f"  ID: {camera.camera_id}")
            print(f"  Name: {camera.location_name}")
            print(f"  Zone: {camera.zone_type}")
            print(f"  Status: {camera.status}")
            print(f"  IP: {camera.ip_address}")
            print(f"  Coordinates type: {type(camera.coordinates)}")
            print(f"  Coordinates: {camera.coordinates}")
            print(f"  FOV type: {type(camera.field_of_view)}")
            print(f"  FOV: {camera.field_of_view}")
            print(f"  Install Date: {camera.installation_date} (type: {type(camera.installation_date)})")
    
    # Test statistics
    print("\nGetting statistics...")
    stats = CameraRepository.get_camera_stats()
    print(f"Stats: {stats}")
    
    # Test zones
    print("\nGetting zones...")
    zones = CameraRepository.get_all_zones()
    print(f"Zones: {zones}")

if __name__ == "__main__":
    debug_camera_data()