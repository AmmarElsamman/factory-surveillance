"""
register.py
Employee registration system with multiple photos -> single embedding
"""
 
import cv2
import requests
import numpy as np
from pathlib import Path
import shutil
from insightface.app import FaceAnalysis
 
API_URL = "http://localhost:8000"
 
class RegistrationSystem:
    def __init__(self):
        """Initialize registration system"""
        
        # Initialize InsightFace
        print("Initializing face detection system...")
        try:
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CUDAExecutionProvider']
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            print("✅ Running on GPU")
        except:
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CPUExecutionProvider']
            )
            self.app.prepare(ctx_id=-1, det_size=(640, 640))
            print("✅ Running on CPU")
    
    def register_employee(self, emp_code, emp_name, image_paths):
        """
        Register employee with multiple photos
        Computes ONE averaged embedding and saves it to the database
        """
        print(f"\n{'='*60}")
        print(f"Registering: {emp_name} ({emp_code})")
        print(f"{'='*60}")
        
        embeddings = []
        successful = 0
        
        # Process all photos
        for idx, img_path in enumerate(image_paths):
            print(f"\n📸 Photo {idx+1}/{len(image_paths)}: {Path(img_path).name}")
            
            img = cv2.imread(img_path)
            if img is None:
                print(f"  ❌ Could not read image")
                continue
            
            # Convert to RGB for InsightFace
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            faces = self.app.get(rgb_img)
            
            if len(faces) == 0:
                print(f"  ❌ No face detected")
                continue
            
            if len(faces) > 1:
                print(f"  ⚠️  Multiple faces, using largest")
                faces = sorted(faces, 
                             key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]), 
                             reverse=True)
            
            # Get embedding
            face = faces[0]
            embedding = face.normed_embedding
            
            # Quality check
            bbox_area = (face.bbox[2]-face.bbox[0]) * (face.bbox[3]-face.bbox[1])
            img_area = img.shape[0] * img.shape[1]
            face_ratio = bbox_area / img_area
            
            if face_ratio < 0.05:
                print(f"  ⚠️  Face small ({face_ratio*100:.1f}% of image)")
            else:
                print(f"  ✅ Good quality ({face_ratio*100:.1f}% of image)")
            
            embeddings.append(embedding)
            successful += 1
        
        if successful == 0:
            return False, "No valid photos processed"
        
        # Calculate AVERAGE embedding and normalize
        avg_embedding = np.mean(embeddings, axis=0)
        avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)
        
        # Calculate quality score from consistency between photos
        avg_sim = 1.0
        if len(embeddings) > 1:
            similarities = [np.dot(avg_embedding, emb) for emb in embeddings]
            avg_sim = float(np.mean(similarities))
            min_sim = float(np.min(similarities))
            
            print(f"\n📊 Quality Metrics:")
            print(f"   Average similarity: {avg_sim:.4f}")
            print(f"   Minimum similarity: {min_sim:.4f}")
            
            if avg_sim < 0.7:
                print("   ⚠️  Warning: Photos have low consistency")
                print("   💡 Tip: Use similar lighting and angles")
        
        # Look up worker_id from API using employee_code
        try:
            response = requests.get(f"{API_URL}/api/worker/{emp_code}")
            if response.status_code == 200:
                worker_id = response.json()['worker']['worker_id']
                
                # Save embedding to database
                embed_response = requests.post(
                    f"{API_URL}/api/worker_embeddings",
                    json={
                        "worker_id": worker_id,
                        "camera_id": "CAM-001",
                        "feature_vector": avg_embedding.tolist(),
                        "name": emp_name,
                        "quality_score": avg_sim,
                        "is_primary": True
                    }
                )
                if embed_response.status_code == 200:
                    print(f"\n✅ Successfully registered {emp_name}")
                    print(f"📊 Used {successful} photos to create profile")
                    return True, f"Registered with {successful} photos"
                else:
                    print(f"❌ Failed to save embedding: {embed_response.text}")
                    return False, "Failed to save embedding to database"
            else:
                print(f"❌ Worker {emp_code} not found in database")
                return False, f"Worker {emp_code} not found in database"
        except Exception as e:
            print(f"❌ Could not connect to API: {e}")
            return False, f"API connection error: {e}"
 
 
def capture_photos_webcam(emp_code, emp_name, num_photos=5):
    """Capture multiple photos from webcam"""
    print(f"\n{'='*60}")
    print(f"📸 MULTI-PHOTO CAPTURE")
    print(f"{'='*60}")
    print(f"Employee: {emp_name} ({emp_code})")
    print(f"Photos to capture: {num_photos}")
    
    poses = [
        "Look STRAIGHT at camera",
        "Turn slightly LEFT",
        "Turn slightly RIGHT",
        "SMILE 😊",
        "Neutral expression"
    ]
    
    print("\n📋 Instructions:")
    for i, pose in enumerate(poses[:num_photos], 1):
        print(f"  {i}. {pose}")
    print("\n⌨️  Controls:")
    print("  SPACE - Capture photo")
    print("  ESC - Cancel registration")
    print("\n")
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print("❌ Could not open camera")
        return None
    
    temp_folder = Path('temp_registration')
    temp_folder.mkdir(exist_ok=True)
    
    captured = []
    count = 0
    
    while count < num_photos:
        ret, frame = cap.read()
        if not ret:
            break
        
        instruction = poses[count] if count < len(poses) else f"Photo {count+1}"
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        cv2.putText(frame, f"Photo {count+1}/{num_photos}: {instruction}", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, "SPACE = capture | ESC = cancel", 
                   (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        h, w = frame.shape[:2]
        gw, gh = w//3, h//2
        gx, gy = (w-gw)//2, (h-gh)//2
        cv2.rectangle(frame, (gx, gy), (gx+gw, gy+gh), (0, 255, 0), 3)
        cv2.putText(frame, "Position face here", (gx+20, gy-15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.imshow('Registration - Photo Capture', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):
            photo_path = temp_folder / f"{emp_code}_{count:02d}.jpg"
            cv2.imwrite(str(photo_path), frame)
            captured.append(str(photo_path))
            count += 1
            
            white = frame.copy()
            cv2.rectangle(white, (0, 0), (w, h), (255, 255, 255), -1)
            cv2.imshow('Registration - Photo Capture', white)
            cv2.waitKey(150)
            
            print(f"✅ Captured {count}/{num_photos}")
            
        elif key == 27:  # ESC
            print("\n❌ Registration cancelled by user")
            cap.release()
            cv2.destroyAllWindows()
            shutil.rmtree(temp_folder, ignore_errors=True)
            return None
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n✅ All {num_photos} photos captured successfully!\n")
    return captured
 
 
def register_live():
    """Live webcam registration"""
    system = RegistrationSystem()
    
    print("\n" + "="*60)
    print("📸 LIVE WEBCAM REGISTRATION")
    print("="*60)
    
    emp_code = input("\nEmployee Code (e.g., EMP001): ").strip().upper()
    if not emp_code:
        print("❌ Employee Code is required!")
        return
    
    emp_name = input("Employee Name: ").strip()
    if not emp_name:
        print("❌ Employee Name is required!")
        return
    
    num_input = input("\nNumber of photos (3-10, default 5): ").strip()
    num_photos = int(num_input) if num_input.isdigit() else 5
    num_photos = max(3, min(10, num_photos))
    
    photo_paths = capture_photos_webcam(emp_code, emp_name, num_photos)
    
    if not photo_paths:
        return
    
    print("="*60)
    print("🔄 Processing photos...")
    print("="*60)
    
    success, message = system.register_employee(emp_code, emp_name, photo_paths)
    
    # Cleanup temp files
    for photo in photo_paths:
        Path(photo).unlink(missing_ok=True)
    temp_folder = Path('temp_registration')
    if temp_folder.exists():
        temp_folder.rmdir()
    
    if not success:
        print(f"\n❌ Registration failed: {message}")
 
 
def register_from_folder():
    """Register from existing folder of photos"""
    system = RegistrationSystem()
    
    print("\n" + "="*60)
    print("📁 REGISTER FROM FOLDER")
    print("="*60)
    
    emp_code = input("\nEmployee Code: ").strip().upper()
    emp_name = input("Employee Name: ").strip()
    folder = input("Folder path: ").strip()
    
    if not all([emp_code, emp_name, folder]):
        print("❌ All fields are required!")
        return
    
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder}")
        return
    
    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        images.extend(folder_path.glob(ext))
    
    if not images:
        print("❌ No images found in folder!")
        return
    
    print(f"Found {len(images)} images")
    
    success, message = system.register_employee(
        emp_code, emp_name, [str(img) for img in images]
    )
    
    if not success:
        print(f"\n❌ Registration failed: {message}")
 
 
def bulk_register():
    """Bulk register from structured folders"""
    system = RegistrationSystem()
    
    print("\n" + "="*60)
    print("📁 BULK REGISTRATION")
    print("="*60)
    print("\nExpected structure:")
    print("  employee_photos/")
    print("    ├── EMP001_John_Doe/")
    print("    │   ├── photo1.jpg")
    print("    │   └── photo2.jpg")
    print("    └── EMP002_Jane_Smith/")
    print("        └── photo1.jpg")
    
    base = input("\nBase folder path: ").strip()
    base_path = Path(base)
    
    if not base_path.exists():
        print("❌ Folder not found!")
        return
    
    registered = 0
    failed = 0
    
    for emp_folder in sorted(base_path.iterdir()):
        if not emp_folder.is_dir():
            continue
        
        name = emp_folder.name
        parts = name.split('_', 1)
        
        if len(parts) < 2:
            print(f"\n⚠️  Skip '{name}' - Use format: ID_Name (e.g., EMP001_John_Doe)")
            failed += 1
            continue
        
        emp_code = parts[0].upper()
        emp_name = parts[1].replace('_', ' ')
        
        print(f"\n{'='*60}")
        print(f"Processing: {emp_name} ({emp_code})")
        
        images = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            images.extend(emp_folder.glob(ext))
        
        if not images:
            print(f"  ❌ No images found")
            failed += 1
            continue
        
        success, _ = system.register_employee(
            emp_code, emp_name, [str(img) for img in images]
        )
        
        if success:
            registered += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print("BULK REGISTRATION COMPLETE")
    print("="*60)
    print(f"✅ Registered: {registered}")
    print(f"❌ Failed: {failed}")
 
 
def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("🎯 EMPLOYEE REGISTRATION SYSTEM")
        print("="*60)
        print("\n1. Live capture (webcam)")
        print("2. Register from folder")
        print("3. Bulk register")
        print("4. Exit")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == '1':
            register_live()
        elif choice == '2':
            register_from_folder()
        elif choice == '3':
            bulk_register()
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice!")
 
 
if __name__ == '__main__':
    main()
 