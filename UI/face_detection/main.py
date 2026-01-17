"""
attendance_system.py
Main attendance application with optimized storage
"""

import ast
import cv2
import numpy as np
from datetime import datetime
import json
import os
from pathlib import Path
from collections import defaultdict
import time
from insightface.app import FaceAnalysis
import requests


class AttendanceSystem:
    def __init__(self, db_path='employee_data', attendance_log='attendance.json'):
        """Initialize attendance system with single embedding per employee"""
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        self.attendance_log = attendance_log
        self.api_url = "http://localhost:8000"  # Reid service URL
        
        # Initialize InsightFace
        print("Initializing face detection system...")
        try:
            print("Attempting GPU initialization...")
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CUDAExecutionProvider']
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))  # Larger size for better detection
            print("✅ Running on GPU - Maximum speed!")
        except Exception as e:
            print(f"⚠️  GPU failed, falling back to CPU")
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CPUExecutionProvider']
            )
            self.app.prepare(ctx_id=-1, det_size=(640, 640))  # Larger size
            print("✅ Running on CPU")
        
        # Load employee database (ONE embedding per person)
        self.employee_embeddings = {}  # {emp_id: embedding}
        self.employee_info = {}  # {emp_id: {name, date, etc}}
        self.load_employee_database()
        
        # Attendance tracking
        self.today_attendance = self.load_today_attendance()
        
        # Auto-capture settings
        self.recognition_threshold = 0.5  
        self.confidence_threshold = 3  
        self.cooldown_period = 3  # Seconds between captures (was 5)
        
        # Tracking for auto-capture
        self.recognition_history = defaultdict(list)
        self.last_capture_time = {}
        
        # Statistics
        self.frame_count = 0
        self.detection_count = 0
    
    def load_employee_database(self):
        """Load all employee embeddings from JSON files"""
        print("Loading employee database...")
        try:
            start_time = time.perf_counter()
            response = requests.get(
                f"{self.api_url}/api/worker_embeddings"
            )
            response.raise_for_status()
            rows = response.json().get('embeddings', [])
            if not rows:
                raise ValueError("No embeddings returned from API.")
            end_time = time.perf_counter()
            
            best = {}
            for row in rows:
                try:
                    if not hasattr(row, "get"):
                        # expected columns: embedding_id, worker_id, full_name,
                        # feature_vector, quality_score, camera_id, is_primary, created_at
                        row = {
                            "embedding_id": row[0],
                            "worker_id": row[1],
                            "full_name": row[2],
                            "feature_vector": row[3],
                            "quality_score": row[4],
                            "camera_id": row[5],
                            "is_primary": row[6],
                            "created_at": row[7],
                        }
                    worker_id = row.get('worker_id')
                    if not worker_id:
                        continue
                    
                    vec = row.get('feature_vector')
                    
                    if isinstance(vec, str):
                        try:
                            vec_parsed = json.loads(vec)
                        except Exception:
                            try:
                                vec_parsed = ast.literal_eval(vec)
                            except Exception:
                                print(f"  ✗ Could not parse vector for {worker_id}")
                                continue
                    elif isinstance(vec, (list, tuple, np.ndarray)):
                        vec_parsed = list(vec)
                    else:
                        try:
                            vec_parsed = list(vec)
                        except Exception:
                            print(f"  ✗ Could not parse vector for {worker_id}")
                            continue
                    
                    emb = np.array(vec_parsed, dtype=np.float32)
                    if emb.size == 0:
                        continue
                    
                    quality = row.get('quality_score', 0.0)
                    is_primary = row.get('is_primary', False)
                    if isinstance(is_primary, str):
                        is_primary = is_primary.lower() in ("t", "true", "1")
                    else:
                        is_primary = bool(is_primary)
                    
                    name = row.get('full_name', 'Unknown')
                    created_at = row.get('created_at', '')
                    
                    cur = best.get(worker_id)
                    replace = False
                    if cur is None:
                        replace = True
                    else:
                        if is_primary and not cur['is_primary']:
                            replace = True
                        elif is_primary == cur['is_primary']:
                            if quality > cur['quality_score']:
                                replace = True
                    if replace:
                        best[worker_id] = {
                            'embedding': emb,
                            'quality_score': quality,
                            'is_primary': is_primary,
                            'name': name,
                            'created_at': created_at
                        }
                except Exception as e:
                    print(f"  ✗ Error processing row: {e}")
            
            for worker_id, data in best.items():
                self.employee_embeddings[worker_id] = data['embedding']
                self.employee_info[worker_id] = {
                    'name': data['name'],
                    'registered_date': data['created_at'],
                    'num_photos_used': 1  # Since only one embedding per employee
                }
                print(f"  ✓ {worker_id}: {data['name']} (Quality: {data['quality_score']})")
            
            if len(self.employee_embeddings) == 0:
                print("⚠️  No valid employee embeddings found in the database.")
            
            print(f"✅ Loaded {len(self.employee_embeddings)} employees from API\n")
            return
        except Exception as e:
            print(f"⚠️  Failed to load from API: {e}")
            print("Falling back to local JSON files...")
            
        # for emp_file in self.db_path.glob('*.json'):
        #     emp_id = emp_file.stem
            
        #     try:
        #         # Load JSON file
        #         with open(emp_file, 'r') as f:
        #             data = json.load(f)
                
        #         # Convert embedding list back to numpy array
        #         embedding = np.array(data['embedding'])
                
        #         # Load metadata
        #         info = {
        #             'name': data['name'],
        #             'registered_date': data['registered_date'],
        #             'num_photos_used': data['num_photos_used']
        #         }
                
        #         self.employee_embeddings[emp_id] = embedding
        #         self.employee_info[emp_id] = info
                
        #         print(f"  ✓ {emp_id}: {info['name']} ({info['num_photos_used']} photos)")
        #     except Exception as e:
        #         print(f"  ✗ Error loading {emp_id}: {e}")
        
        # print(f"✅ Loaded {len(self.employee_embeddings)} employees\n")
    
    def recognize_face(self, face_embedding):
        """Recognize face using single embedding comparison"""
        best_match_id = None
        best_distance = float('inf')
        
        for emp_id, emp_embedding in self.employee_embeddings.items():
            # Cosine distance
            distance = 1 - np.dot(face_embedding, emp_embedding)
            
            if distance < best_distance:
                best_distance = distance
                best_match_id = emp_id
        
        # Apply threshold
        if best_distance < self.recognition_threshold:
            return best_match_id, best_distance
        
        return None, best_distance
    
    def should_auto_capture(self, emp_id):
        """Check if should auto-capture attendance for this employee"""
        # Already marked today?
        if emp_id in self.today_attendance:
            return False, "Already marked"
        
        current_time = time.time()
        
        # Check cooldown period
        if emp_id in self.last_capture_time:
            time_since = current_time - self.last_capture_time[emp_id]
            if time_since < self.cooldown_period:
                return False, f"Cooldown ({self.cooldown_period - time_since:.1f}s)"
        
        # Check consecutive recognitions (confidence)
        history = self.recognition_history[emp_id]
        
        # Keep only recent recognitions (last 3 seconds - INCREASED)
        recent = [t for t in history if current_time - t < 3.0]
        self.recognition_history[emp_id] = recent
        
        # Need N consecutive recognitions
        if len(recent) >= self.confidence_threshold:
            return True, "Confident ✓"
        
        return False, f"Building ({len(recent)}/{self.confidence_threshold})"
    
    def auto_mark_attendance(self, emp_id):
        """Automatically mark attendance"""
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        # Load all records
        if os.path.exists(self.attendance_log):
            with open(self.attendance_log, 'r') as f:
                all_records = json.load(f)
        else:
            all_records = {}
        
        # Add today's record
        if today not in all_records:
            all_records[today] = {}
        
        all_records[today][emp_id] = time_str
        
        # Save
        with open(self.attendance_log, 'w') as f:
            json.dump(all_records, f, indent=2)
        
        self.today_attendance[emp_id] = time_str
        self.last_capture_time[emp_id] = time.time()
        self.recognition_history[emp_id] = []
        
        emp_name = self.employee_info[emp_id]['name']
        
        print(f"\n{'='*60}")
        print(f"🎉 AUTO-CAPTURE: {emp_name} ({emp_id})")
        print(f"⏰ Time: {time_str}")
        print(f"{'='*60}\n")
        
        return True
    
    def load_today_attendance(self):
        """Load today's attendance records"""
        if not os.path.exists(self.attendance_log):
            return {}
        
        with open(self.attendance_log, 'r') as f:
            all_records = json.load(f)
        
        today = datetime.now().strftime('%Y-%m-%d')
        return all_records.get(today, {})
    
    def process_frame(self, frame):
        """Process frame with face detection and recognition"""
        self.frame_count += 1
        
        # Convert BGR to RGB for InsightFace
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = self.app.get(rgb_frame)
        self.detection_count += len(faces)
        
        # DEBUG: Print detection info occasionally (removed frequent printing)
        if self.frame_count % 90 == 0 and len(faces) > 0:  # Every 90 frames, only if faces detected
            print(f"✓ Detected {len(faces)} face(s)")
        
        results = []
        current_time = time.time()
        
        for face in faces:
            # Get face embedding
            embedding = face.normed_embedding
            
            # Recognize
            emp_id, distance = self.recognize_face(embedding)
            
            # Get bounding box
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            
            if emp_id:
                emp_name = self.employee_info[emp_id]['name']
                num_photos = self.employee_info[emp_id]['num_photos_used']
                already_marked = emp_id in self.today_attendance
                
                # Add to recognition history
                self.recognition_history[emp_id].append(current_time)
                
                # Check if should auto-capture
                should_capture, msg = self.should_auto_capture(emp_id)
                
                # DEBUG: Print recognition info
                if not already_marked:
                    # Only print when status changes or every 60 frames
                    if should_capture or self.frame_count % 60 == 0:
                        print(f"🔍 {emp_name}: {msg} (distance={distance:.3f})")
                
                # Auto-capture if conditions met
                if should_capture:
                    self.auto_mark_attendance(emp_id)
                    already_marked = True
                
                # Color coding
                if already_marked:
                    color = (0, 255, 0)  # Green - Present
                    status = " PRESENT"
                else:
                    color = (0, 165, 255)  # Orange - Detecting
                    status = f"{msg}"
                
                label = emp_name
                info_text = f"{(1-distance)*100:.1f}% ({num_photos}p)"
                
                results.append({
                    'emp_id': emp_id,
                    'name': emp_name,
                    'distance': distance,
                    'marked': already_marked,
                    'bbox': (x1, y1, x2, y2),
                    'color': color
                })
            else:
                color = (0, 0, 255)  # Red - Unknown
                label = "UNKNOWN"
                status = " Not Recognized"
                info_text = f"Dist: {distance:.2f}"
            
            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw name BELOW the box (not above)
            cv2.putText(frame, label, (x1, y2+25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Draw status below name
            cv2.putText(frame, status, (x1, y2+50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Draw confidence info
            cv2.putText(frame, info_text, (x1, y2+70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return frame, results
    
    def run(self):
        """Run the attendance system"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("\n" + "="*60)
        print("🚀 ATTENDANCE SYSTEM STARTED")
        print("="*60)
        print(f"✅ Auto-capture: ON")
        print(f"⏱️  Recognition threshold: {self.recognition_threshold}")
        print(f"🎯 Confidence requirement: {self.confidence_threshold} frames")
        print(f"❄️  Cooldown period: {self.cooldown_period} seconds")
        print("\nControls:")
        print("  'q' - Quit")
        print("  's' - Show statistics")
        print("  'r' - Reset daily attendance")
        print("  'SPACE' - Manual capture (mark detected face)")
        print("="*60 + "\n")
        
        # FPS calculation
        fps_start = time.time()
        fps_count = 0
        current_fps = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read from camera")
                break
            
            fps_count += 1
            
            # Calculate FPS every 30 frames
            if fps_count >= 30:
                current_fps = 30 / (time.time() - fps_start)
                fps_start = time.time()
                fps_count = 0
            
            # Process every frame
            processed, results = self.process_frame(frame)
            
            # Display info panel
            cv2.putText(processed, f"FPS: {current_fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            present = len(self.today_attendance)
            total = len(self.employee_embeddings)
            cv2.putText(processed, f"Present: {present}/{total}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Attendance System', processed)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n👋 Shutting down...")
                break
            elif key == ord('s'):
                self.print_statistics()
            elif key == ord('r'):
                self.reset_daily_attendance()
            elif key == ord(' '):  # SPACE for manual capture
                # Manually mark any detected faces
                for result in results:
                    emp_id = result['emp_id']
                    if emp_id not in self.today_attendance:
                        self.auto_mark_attendance(emp_id)
                        print(f"✅ Manually captured: {result['name']}")
        
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "="*60)
        print("📊 Final Session Statistics:")
        self.print_statistics()
    
    def print_statistics(self):
        """Print system statistics"""
        print("\n" + "="*60)
        print("📊 SYSTEM STATISTICS")
        print("="*60)
        print(f"Total Employees: {len(self.employee_embeddings)}")
        print(f"Present Today: {len(self.today_attendance)}/{len(self.employee_embeddings)}")
        print(f"Frames Processed: {self.frame_count}")
        print(f"Faces Detected: {self.detection_count}")
        
        if self.today_attendance:
            print("\n✅ Present Employees:")
            for emp_id, time_str in sorted(self.today_attendance.items(), key=lambda x: x[1]):
                name = self.employee_info[emp_id]['name']
                print(f"  {time_str} - {name} ({emp_id})")
        
        if len(self.today_attendance) < len(self.employee_embeddings):
            print("\n❌ Absent Employees:")
            for emp_id, info in self.employee_info.items():
                if emp_id not in self.today_attendance:
                    print(f"  {info['name']} ({emp_id})")
        
        print("="*60 + "\n")
    
    def reset_daily_attendance(self):
        """Reset today's attendance (for testing)"""
        confirm = input("\n⚠️  Reset today's attendance? (yes/no): ").strip().lower()
        if confirm == 'yes':
            self.today_attendance = {}
            self.last_capture_time = {}
            self.recognition_history = defaultdict(list)
            print("✅ Daily attendance reset successfully")
        else:
            print("❌ Reset cancelled")


def main():
    """Main entry point"""
    system = AttendanceSystem()
    
    if len(system.employee_embeddings) == 0:
        print("\n⚠️  WARNING: No employees registered!")
        print("Please run 'python register.py' first to register employees.\n")
        return
    
    system.run()


if __name__ == '__main__':
    main()