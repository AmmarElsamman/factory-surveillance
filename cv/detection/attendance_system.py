"""
attendance_system.py
Main attendance application with optimized storage
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
        """Initialize attendance system with single embedding per employee"""
        self.attendance_log = attendance_log
        self.api_url = API_URL

        # Initialize InsightFace
        print("Initializing face detection system...")
        try:
            print("Attempting GPU initialization...")
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CUDAExecutionProvider']
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            print("✅ Running on GPU - Maximum speed!")
        except Exception:
            print("⚠️  GPU failed, falling back to CPU")
            self.app = FaceAnalysis(
                name='buffalo_l',
                providers=['CPUExecutionProvider']
            )
            self.app.prepare(ctx_id=-1, det_size=(640, 640))
            print("✅ Running on CPU")

        # Load employee database (ONE embedding per person)
        self.employee_embeddings = {}  # {worker_id: np.array}
        self.employee_info = {}        # {worker_id: {name}}
        self.load_employee_database()

        # Pre-build embedding matrix for vectorized search
        self.embedding_matrix = None   # (N, 512) normalized matrix
        self.embedding_ids = []        # ordered list of worker_ids matching rows
        self._build_embedding_matrix()

        # Attendance tracking
        self.today_attendance = self.load_today_attendance()

        # Auto-capture settings
        self.recognition_threshold = 0.5
        self.confidence_threshold = 3
        self.cooldown_period = 3  # seconds between captures

        # Tracking for auto-capture
        self.recognition_history = defaultdict(list)
        self.last_capture_time = {}

        # Statistics
        self.frame_count = 0
        self.detection_count = 0

        # Frame-skip state
        self.skip_frames = 3
        self._last_results = []

        # Warm up the model with a dummy frame
        print("Warming up face detection model...")
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        self.app.get(dummy)
        print("✅ Model warmed up\n")

    def _build_embedding_matrix(self):
        """Pre-build a normalized matrix for fast vectorized similarity search"""
        if not self.employee_embeddings:
            self.embedding_matrix = None
            self.embedding_ids = []
            return

        ids = list(self.employee_embeddings.keys())
        matrix = np.stack([self.employee_embeddings[i] for i in ids]).astype(np.float32)

        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        matrix = matrix / norms

        self.embedding_matrix = matrix
        self.embedding_ids = ids
        print(f"✅ Embedding matrix built: {matrix.shape}")

    def load_employee_database(self):
        """Load all employee embeddings from API into memory"""
        print("Loading employee database...")
        try:
            response = requests.get(f"{self.api_url}/api/worker_embeddings")
            response.raise_for_status()
            rows = response.json().get('embeddings', [])

            if not rows:
                print("⚠️  No embeddings found in database.")
                return

            # Keep only the best embedding per worker (primary first, then highest quality)
            best = {}
            for row in rows:
                worker_id = row.get('worker_id')
                if not worker_id:
                    continue
                
                name =row.get('name', 'Unknown')

                vec = row.get('feature_vector')
                if not vec:
                    continue

                if isinstance(vec, str):
                    try:
                        vec = json.loads(vec)
                    except Exception:
                        print(f"  ✗ Could not parse vector for {worker_id}")
                        continue

                emb = np.array(vec, dtype=np.float32)
                if emb.size == 0:
                    continue

                quality = float(row.get('quality_score') or 0.0)
                is_primary = bool(row.get('is_primary', False))
                name = row.get('name', 'Unknown')

                cur = best.get(worker_id)
                replace = False
                if cur is None:
                    replace = True
                elif is_primary and not cur['is_primary']:
                    replace = True
                elif is_primary == cur['is_primary'] and quality > cur['quality_score']:
                    replace = True

                if replace:
                    best[worker_id] = {
                        'embedding': emb,
                        'quality_score': quality,
                        'is_primary': is_primary,
                        'name': name
                    }

            for worker_id, data in best.items():
                self.employee_embeddings[worker_id] = data['embedding']
                self.employee_info[worker_id] = {'name': data['name']}
                print(f"  ✓ {worker_id}: {data['name']} (Quality: {data['quality_score']})")

            print(f"✅ Loaded {len(self.employee_embeddings)} employees\n")

        except Exception as e:
            print(f"❌ Failed to load employee database: {e}")

    def recognize_face(self, face_embedding):
        """Fast vectorized similarity search against in-memory embedding matrix"""
        if self.embedding_matrix is None or len(self.embedding_ids) == 0:
            return None, float('inf')

        norm = np.linalg.norm(face_embedding)
        if norm > 0:
            face_embedding = face_embedding / norm

        similarities = self.embedding_matrix @ face_embedding
        best_idx = int(np.argmax(similarities))
        best_sim = float(similarities[best_idx])
        distance = 1.0 - best_sim

        if distance < self.recognition_threshold:
            return self.embedding_ids[best_idx], distance
        return None, distance

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

    def auto_mark_attendance(self, worker_id):
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

        all_records[today][worker_id] = time_str

        with open(self.attendance_log, 'w') as f:
            json.dump(all_records, f, indent=2)

        self.today_attendance[worker_id] = time_str
        self.last_capture_time[worker_id] = time.time()
        self.recognition_history[worker_id] = []

        emp_name = self.employee_info[worker_id]['name']

        print(f"\n{'='*60}")
        print(f"🎉 AUTO-CAPTURE: {emp_name} ({worker_id})")
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

    def _draw_results(self, frame, results):
        """Draw bounding boxes and labels on frame"""
        for r in results:
            x1, y1, x2, y2 = r['bbox']
            color = r['color']
            label = r['name'] if r['worker_id'] else "UNKNOWN"
            status = "✓ PRESENT" if r['marked'] else ""
            info_text = f"{(1 - r['distance']) * 100:.1f}%"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y2 + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, status, (x1, y2 + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.putText(frame, info_text, (x1, y2 + 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        return frame

    def process_frame(self, frame):
        """Process frame with face detection and recognition"""
        self.frame_count += 1

        # Always process frame 1, then apply skip logic
        if self.frame_count > 1 and self.frame_count % (self.skip_frames + 1) != 0:
            return self._draw_results(frame, self._last_results), self._last_results

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.app.get(rgb_frame)
        self.detection_count += len(faces)

        if self.frame_count % 90 == 0 and len(faces) > 0:
            print(f"✓ Detected {len(faces)} face(s)")

        results = []
        current_time = time.time()

        for face in faces:
            embedding = face.normed_embedding
            worker_id, distance = self.recognize_face(embedding)

            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox

            if worker_id:
                emp_name = self.employee_info[worker_id]['name']
                already_marked = worker_id in self.today_attendance

                self.recognition_history[worker_id].append(current_time)
                should_capture, msg = self.should_auto_capture(worker_id)

                if not already_marked:
                    if should_capture or self.frame_count % 60 == 0:
                        print(f"🔍 {emp_name}: {msg} (distance={distance:.3f})")

                if should_capture:
                    self.auto_mark_attendance(worker_id)
                    already_marked = True

                color = (0, 255, 0) if already_marked else (0, 165, 255)
                status = "✓ PRESENT" if already_marked else msg

                results.append({
                    'worker_id': worker_id,
                    'name': emp_name,
                    'distance': distance,
                    'marked': already_marked,
                    'bbox': (x1, y1, x2, y2),
                    'color': color
                })
            else:
                results.append({
                    'worker_id': None,
                    'name': None,
                    'distance': distance,
                    'marked': False,
                    'bbox': (x1, y1, x2, y2),
                    'color': (0, 0, 255)
                })

        self._last_results = results
        return self._draw_results(frame, results), results

    def run(self):
        """Run the attendance system"""
        print("\nOpening camera...")
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
        print(f"⚡ Frame skip: process 1 every {self.skip_frames + 1} frames")
        print("\nControls:")
        print("  'q' - Quit")
        print("  's' - Show statistics")
        print("  'r' - Reset daily attendance")
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

            present = len(self.today_attendance)
            total = len(self.employee_embeddings)
            cv2.putText(processed, f"Present: {present}/{total}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow('Attendance System', processed)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                print("\n👋 Shutting down...")
                break
            elif key == ord('r'):
                self.reset_daily_attendance()

        cap.release()
        cv2.destroyAllWindows()


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
        print("Please register employees first.\n")
        return

    system.run()


if __name__ == '__main__':
    main()