"""
register.py
Employee registration system with multiple photos -> single embedding
"""

import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import shutil
import json
from insightface.app import FaceAnalysis


class RegistrationSystem:
    def __init__(self, db_path='grad-project/employee_data'):
        """Initialize registration system"""
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # Initialize InsightFace
        print("Initializing face detection system...")
        try:
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CUDAExecutionProvider']
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))  # Larger size
            print("✅ Running on GPU")
        except:
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CPUExecutionProvider']
            )
            self.app.prepare(ctx_id=-1, det_size=(640, 640))  # Larger size
            print("✅ Running on CPU")
    
    def register_employee(self, emp_id, emp_name, image_paths):
        """
        Register employee with multiple photos
        Computes and saves ONLY ONE averaged embedding
        """
        print(f"\n{'='*60}")
        print(f"Registering: {emp_name} ({emp_id})")
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
        
        # Calculate AVERAGE embedding
        avg_embedding = np.mean(embeddings, axis=0)
        # Normalize
        avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)
        
        # Quality metrics
        if len(embeddings) > 1:
            similarities = [np.dot(avg_embedding, emb) for emb in embeddings]
            avg_sim = np.mean(similarities)
            min_sim = np.min(similarities)
            
            print(f"\n📊 Quality Metrics:")
            print(f"   Average similarity: {avg_sim:.4f}")
            print(f"   Minimum similarity: {min_sim:.4f}")
            
            if avg_sim < 0.7:
                print("   ⚠️  Warning: Photos have low consistency")
                print("   💡 Tip: Use similar lighting and angles")
        
        # Save ONLY the average embedding as JSON
        emp_file = self.db_path / f"{emp_id}.json"
        
        # Prepare data for JSON (convert numpy to list)
        save_data = {
            'embedding': avg_embedding.tolist(),  # Convert to list for JSON
            'name': emp_name,
            'registered_date': datetime.now().isoformat(),
            'num_photos_used': successful
        }
        
        with open(emp_file, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        print(f"\n✅ Successfully registered {emp_name}")
        print(f"📁 Saved as: {emp_file.name}")
        print(f"📊 Used {successful} photos to create profile")
        print(f"💾 File size: {emp_file.stat().st_size / 1024:.1f} KB")
        
        return True, f"Registered with {successful} photos"
    
    def list_employees(self):
        """List all registered employees"""
        employees = list(self.db_path.glob('*.json'))
        
        if not employees:
            print("\n❌ No employees registered yet")
            return
        
        print(f"\n{'='*60}")
        print(f"👥 REGISTERED EMPLOYEES ({len(employees)})")
        print(f"{'='*60}")
        
        total_size = 0
        for emp_file in sorted(employees):
            with open(emp_file, 'r') as f:
                data = json.load(f)
            
            emp_id = emp_file.stem
            name = data['name']
            date = data['registered_date'][:10]
            num_photos = data['num_photos_used']
            size_kb = emp_file.stat().st_size / 1024
            total_size += size_kb
            
            print(f"\n{emp_id}: {name}")
            print(f"  Registered: {date}")
            print(f"  Photos used: {num_photos}")
            print(f"  Size: {size_kb:.1f} KB")
        
        print(f"\n{'='*60}")
        print(f"Total storage: {total_size:.1f} KB")
        print(f"{'='*60}\n")
    
    def delete_employee(self, emp_id):
        """Delete an employee"""
        emp_file = self.db_path / f"{emp_id}.json"
        
        if not emp_file.exists():
            print(f"❌ Employee {emp_id} not found")
            return False
        
        with open(emp_file, 'r') as f:
            data = json.load(f)
        name = data['name']
        
        confirm = input(f"⚠️  Delete {name} ({emp_id})? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            emp_file.unlink()
            print(f"✅ Deleted {name}")
            return True
        
        print("❌ Cancelled")
        return False


def capture_photos_webcam(emp_id, emp_name, num_photos=5):
    """Capture multiple photos from webcam"""
    print(f"\n{'='*60}")
    print(f"📸 MULTI-PHOTO CAPTURE")
    print(f"{'='*60}")
    print(f"Employee: {emp_name} ({emp_id})")
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
    
    # Temp folder
    temp_folder = Path('temp_registration')
    temp_folder.mkdir(exist_ok=True)
    
    captured = []
    count = 0
    
    while count < num_photos:
        ret, frame = cap.read()
        if not ret:
            break
        
        instruction = poses[count] if count < len(poses) else f"Photo {count+1}"
        
        # Create overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Instructions
        cv2.putText(frame, f"Photo {count+1}/{num_photos}: {instruction}", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, "SPACE = capture | ESC = cancel", 
                   (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Guide box
        h, w = frame.shape[:2]
        gw, gh = w//3, h//2
        gx, gy = (w-gw)//2, (h-gh)//2
        cv2.rectangle(frame, (gx, gy), (gx+gw, gy+gh), (0, 255, 0), 3)
        cv2.putText(frame, "Position face here", (gx+20, gy-15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.imshow('Registration - Photo Capture', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # SPACE
            photo_path = temp_folder / f"{emp_id}_{count:02d}.jpg"
            cv2.imwrite(str(photo_path), frame)
            captured.append(str(photo_path))
            count += 1
            
            # Flash effect
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
    
    emp_id = input("\nEmployee ID (e.g., EMP001): ").strip().upper()
    if not emp_id:
        print("❌ Employee ID is required!")
        return
    
    emp_name = input("Employee Name: ").strip()
    if not emp_name:
        print("❌ Employee Name is required!")
        return
    
    # Check if exists
    emp_file = system.db_path / f"{emp_id}.json"
    if emp_file.exists():
        print(f"\n⚠️  {emp_id} already exists!")
        choice = input("Options: (o)verwrite | (d)ifferent ID | (c)ancel: ").strip().lower()
        
        if choice == 'o':
            emp_file.unlink()
            print("✅ Previous record deleted")
        elif choice == 'd':
            emp_id = input("New Employee ID: ").strip().upper()
            if not emp_id:
                print("❌ Cancelled")
                return
        else:
            print("❌ Cancelled")
            return
    
    # Number of photos
    num_input = input("\nNumber of photos (3-10, default 5): ").strip()
    num_photos = int(num_input) if num_input.isdigit() else 5
    num_photos = max(3, min(10, num_photos))
    
    # Capture photos
    photo_paths = capture_photos_webcam(emp_id, emp_name, num_photos)
    
    if not photo_paths:
        return
    
    # Process and register
    print("="*60)
    print("🔄 Processing photos...")
    print("="*60)
    
    success, message = system.register_employee(emp_id, emp_name, photo_paths)
    
    # Cleanup temp files
    for photo in photo_paths:
        Path(photo).unlink(missing_ok=True)
    temp_folder = Path('temp_registration')
    if temp_folder.exists():
        temp_folder.rmdir()
    
    if success:
        print(f"\n🎉 {emp_name} registered successfully!")
    else:
        print(f"\n❌ Registration failed: {message}")


def register_from_folder():
    """Register from existing folder of photos"""
    system = RegistrationSystem()
    
    print("\n" + "="*60)
    print("📁 REGISTER FROM FOLDER")
    print("="*60)
    
    emp_id = input("\nEmployee ID: ").strip().upper()
    emp_name = input("Employee Name: ").strip()
    folder = input("Folder path: ").strip()
    
    if not all([emp_id, emp_name, folder]):
        print("❌ All fields are required!")
        return
    
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder}")
        return
    
    # Find images
    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        images.extend(folder_path.glob(ext))
    
    if not images:
        print("❌ No images found in folder!")
        return
    
    print(f"Found {len(images)} images")
    
    success, message = system.register_employee(
        emp_id, emp_name, [str(img) for img in images]
    )
    
    if success:
        print(f"\n🎉 {emp_name} registered successfully!")


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
        
        # Parse folder name: EMP001_John_Doe
        name = emp_folder.name
        parts = name.split('_', 1)
        
        if len(parts) < 2:
            print(f"\n⚠️  Skip '{name}' - Use format: ID_Name (e.g., EMP001_John_Doe)")
            failed += 1
            continue
        
        emp_id = parts[0].upper()
        emp_name = parts[1].replace('_', ' ')
        
        print(f"\n{'='*60}")
        print(f"Processing: {emp_name} ({emp_id})")
        
        # Find images
        images = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            images.extend(emp_folder.glob(ext))
        
        if not images:
            print(f"  ❌ No images found")
            failed += 1
            continue
        
        success, _ = system.register_employee(
            emp_id, emp_name, [str(img) for img in images]
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


def manage_employees():
    """Manage existing employees"""
    system = RegistrationSystem()
    
    while True:
        print("\n" + "="*60)
        print("👥 EMPLOYEE MANAGEMENT")
        print("="*60)
        print("\n1. List all employees")
        print("2. Delete employee")
        print("3. Back to main menu")
        
        choice = input("\nChoice (1-3): ").strip()
        
        if choice == '1':
            system.list_employees()
            
        elif choice == '2':
            emp_id = input("\nEmployee ID to delete: ").strip().upper()
            system.delete_employee(emp_id)
            
        elif choice == '3':
            break
        else:
            print("❌ Invalid choice!")


def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("🎯 EMPLOYEE REGISTRATION SYSTEM")
        print("="*60)
        print("\n1. Live capture (webcam)")
        print("2. Register from folder")
        print("3. Bulk register")
        print("4. Manage employees")
        print("5. Exit")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == '1':
            register_live()
        elif choice == '2':
            register_from_folder()
        elif choice == '3':
            bulk_register()
        elif choice == '4':
            manage_employees()
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice!")


if __name__ == '__main__':
    main()