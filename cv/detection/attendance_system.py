"""
attendance_system.py
Main attendance application using API for face recognition
"""
 
import cv2
import numpy as np
from datetime import datetime
import json
import os
from collections import defaultdict
import time
from insightface.app import FaceAnalysis
import requests
 
 
API_URL = "http://localhost:8000"
 
 
class AttendanceSystem:
    def __init__(self, attendance_log='attendance.json'):
        """Initialize attendance system"""
        self.attendance_log = attendance_log
        self.api_url = API_URL
 
        # Initialize InsightFace
        print("Initializing face detection system...")
        try:
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CUDAExecutionProvider']
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            print("✅ Running on GPU")
        except Exception:
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CPUExecutionProvider']
            )
            self.app.prepare(ctx_id=-1, det_size=(640, 640))
            print("✅ Running on CPU")
 
        # Track total employees count for display
        self.total_employees = self._get_total_employees()
 
        # Attendance tracking
        self.today_attendance = self.load_today_attendance()
 
        # Recognition settings
        self.recognition_threshold = 0.5
        self.confidence_threshold = 3
        self.cooldown_period = 3
 
        # Tracking state
        self.recognition_history = defaultdict(list)
        self.last_capture_time = {}
 
        # Statistics
        self.frame_count = 0
        self.detection_count = 0
 
    def _get_total_employees(self):
        """Get total number of active workers from API"""
        try:
            response = requests.get(f"{self.api_url}/api/workers?status=active")
            return len(response.json().get('workers', []))
        except Exception:
            return 0
 
    def recognize_face(self, face_embedding):
        """Recognize face using API similarity search"""
        try:
            response = requests.post(
                f"{self.api_url}/api/reid/search-embedding",
                json={
                    "feature_vector": face_embedding.tolist(),
                    "threshold": self.recognition_threshold,
                    "max_results": 1,
                    "search_active_only": False
                }
            )
            data = response.json()
 
            if data['match_found']:
                best = data['matches'][0]
                return best['worker_id'], best['full_name'], best['similarity']
            else:
                closest = data['matches'][0]['similarity'] if data['matches'] else float('inf')
                return None, None, closest
 
        except Exception as e:
            print(f"❌ Recognition API error: {e}")
            return None, None, float('inf')
 
    def should_auto_capture(self, worker_id):
        """Check if should auto-capture attendance for this worker"""
        if worker_id in self.today_attendance:
            return False, "Already marked"
 
        current_time = time.time()
 
        if worker_id in self.last_capture_time:
            time_since = current_time - self.last_capture_time[worker_id]
            if time_since < self.cooldown_period:
                return False, f"Cooldown ({self.cooldown_period - time_since:.1f}s)"
 
        history = self.recognition_history[worker_id]
        recent = [t for t in history if current_time - t < 3.0]
        self.recognition_history[worker_id] = recent
 
        if len(recent) >= self.confidence_threshold:
            return True, "Confident ✓"
 
        return False, f"Building ({len(recent)}/{self.confidence_threshold})"
 
    def auto_mark_attendance(self, worker_id, worker_name):
        """Automatically mark attendance"""
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
 
        if os.path.exists(self.attendance_log):
            with open(self.attendance_log, 'r') as f:
                all_records = json.load(f)
        else:
            all_records = {}
 
        if today not in all_records:
            all_records[today] = {}
 
        all_records[today][worker_id] = {
            'name': worker_name,
            'time': time_str
        }
 
        with open(self.attendance_log, 'w') as f:
            json.dump(all_records, f, indent=2)
 
        self.today_attendance[worker_id] = time_str
        self.last_capture_time[worker_id] = time.time()
        self.recognition_history[worker_id] = []
 
        print(f"\n{'='*60}")
        print(f"🎉 AUTO-CAPTURE: {worker_name}")
        print(f"⏰ Time: {time_str}")
        print(f"{'='*60}\n")
 
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
 
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.app.get(rgb_frame)
        self.detection_count += len(faces)
 
        if self.frame_count % 90 == 0 and len(faces) > 0:
            print(f"✓ Detected {len(faces)} face(s)")
 
        results = []
        current_time = time.time()
 
        for face in faces:
            embedding = face.normed_embedding
            worker_id, worker_name, distance = self.recognize_face(embedding)
 
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
 
            if worker_id:
                already_marked = worker_id in self.today_attendance
                self.recognition_history[worker_id].append(current_time)
                should_capture, msg = self.should_auto_capture(worker_id)
 
                if not already_marked:
                    if should_capture or self.frame_count % 60 == 0:
                        print(f"🔍 {worker_name}: {msg} (distance={distance:.3f})")
 
                if should_capture:
                    self.auto_mark_attendance(worker_id, worker_name)
                    already_marked = True
 
                color = (0, 255, 0) if already_marked else (0, 165, 255)
                status = "PRESENT" if already_marked else msg
                label = worker_name
                info_text = f"{(1 - distance) * 100:.1f}%"
 
                results.append({
                    'worker_id': worker_id,
                    'name': worker_name,
                    'distance': distance,
                    'marked': already_marked,
                    'bbox': (x1, y1, x2, y2),
                    'color': color
                })
            else:
                color = (0, 0, 255)
                label = "UNKNOWN"
                status = "Not Recognized"
                info_text = f"Dist: {distance:.2f}"
 
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y2 + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, status, (x1, y2 + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.putText(frame, info_text, (x1, y2 + 70),
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
        print(f"⏱️  Recognition threshold: {self.recognition_threshold}")
        print(f"🎯 Confidence requirement: {self.confidence_threshold} frames")
        print(f"❄️  Cooldown period: {self.cooldown_period} seconds")
        print("\nControls:")
        print("  'q' - Quit")
        print("  's' - Show statistics")
        print("  'r' - Reset daily attendance")
        print("  'SPACE' - Manual capture")
        print("="*60 + "\n")
 
        fps_start = time.time()
        fps_count = 0
        current_fps = 0
 
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read from camera")
                break
 
            fps_count += 1
            if fps_count >= 30:
                current_fps = 30 / (time.time() - fps_start)
                fps_start = time.time()
                fps_count = 0
 
            processed, results = self.process_frame(frame)
 
            cv2.putText(processed, f"FPS: {current_fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(processed, f"Present: {len(self.today_attendance)}/{self.total_employees}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
 
            cv2.imshow('Attendance System', processed)
 
            key = cv2.waitKey(1) & 0xFF
 
            if key == ord('q'):
                print("\n👋 Shutting down...")
                break
            elif key == ord('s'):
                self.print_statistics()
            elif key == ord('r'):
                self.reset_daily_attendance()
            elif key == ord(' '):
                for result in results:
                    if result['worker_id'] not in self.today_attendance:
                        self.auto_mark_attendance(result['worker_id'], result['name'])
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
        print(f"Total Employees: {self.total_employees}")
        print(f"Present Today: {len(self.today_attendance)}/{self.total_employees}")
        print(f"Frames Processed: {self.frame_count}")
        print(f"Faces Detected: {self.detection_count}")
 
        if self.today_attendance:
            print("\n✅ Present Employees:")
            for worker_id, time_str in sorted(self.today_attendance.items(), key=lambda x: x[1]):
                print(f"  {time_str} - {worker_id}")
 
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
    system.run()
 
 
if __name__ == '__main__':
    main()
 