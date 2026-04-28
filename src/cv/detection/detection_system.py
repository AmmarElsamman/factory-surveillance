"""
detection_system.py
Face detection and recognition system for the surveillance UI.
Designed to be instantiated once and used via process_frame().
"""

import cv2
import numpy as np
import json
import time
from collections import defaultdict
from insightface.app import FaceAnalysis
import requests

API_URL = "http://localhost:8000"


class DetectionSystem:
    def __init__(self):
        """Initialize face detection and recognition system"""

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

        # Load employee embeddings into memory
        # {worker_id: {'embedding': np.array, 'name': str}}
        self.employee_data = {}
        self.load_employee_database()

        # Pre-build matrix for fast vectorized search
        self.embedding_matrix = None
        self.embedding_ids = []
        self._build_embedding_matrix()

        # Recognition settings
        self.recognition_threshold = 0.5

        # Frame state
        self.frame_count = 0
        self.skip_frames = 3
        self._last_results = []

        # Warm up model
        print("Warming up model...")
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        self.app.get(dummy)
        print("✅ Model ready\n")

    def load_employee_database(self):
        """Load all employee embeddings from API into memory"""
        print("Loading employee database...")
        try:
            response = requests.get(f"{API_URL}/api/worker_embeddings")
            response.raise_for_status()
            rows = response.json().get('embeddings', [])

            if not rows:
                print("⚠️  No embeddings found in database.")
                return

            best = {}
            for row in rows:
                worker_id = row.get('worker_id')
                if not worker_id:
                    continue

                vec = row.get('feature_vector')
                if not vec:
                    continue

                if isinstance(vec, str):
                    try:
                        vec = json.loads(vec)
                    except Exception:
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
                self.employee_data[worker_id] = {
                    'embedding': data['embedding'],
                    'name': data['name']
                }
                print(f"  ✓ {data['name']} ({worker_id})")

            print(f"✅ Loaded {len(self.employee_data)} employees\n")

        except Exception as e:
            print(f"❌ Failed to load employee database: {e}")

    def _build_embedding_matrix(self):
        """Pre-build normalized matrix for fast vectorized similarity search"""
        if not self.employee_data:
            return

        ids = list(self.employee_data.keys())
        matrix = np.stack([self.employee_data[i]['embedding'] for i in ids]).astype(np.float32)

        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        matrix = matrix / norms

        self.embedding_matrix = matrix
        self.embedding_ids = ids
        print(f"✅ Embedding matrix built: {matrix.shape}")

    def recognize_face(self, face_embedding):
        """
        Fast vectorized similarity search against in-memory embedding matrix.
        Returns (worker_id, worker_name, distance)
        """
        if self.embedding_matrix is None or len(self.embedding_ids) == 0:
            return None, None, float('inf')

        norm = np.linalg.norm(face_embedding)
        if norm > 0:
            face_embedding = face_embedding / norm

        similarities = self.embedding_matrix @ face_embedding
        best_idx = int(np.argmax(similarities))
        best_sim = float(similarities[best_idx])
        distance = 1.0 - best_sim

        if distance < self.recognition_threshold:
            worker_id = self.embedding_ids[best_idx]
            worker_name = self.employee_data[worker_id]['name']
            return worker_id, worker_name, distance
        
        

        return None, None, distance

    def _draw_results(self, frame, results):
        """Draw bounding boxes and labels on frame"""
        for r in results:
            x1, y1, x2, y2 = r['bbox']
            color = r['color']
            label = r['name'] if r['worker_id'] else "UNKNOWN"
            info_text = f"{(1 - r['distance']) * 100:.1f}%" if r['worker_id'] else f"Dist: {r['distance']:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y2 + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, info_text, (x1, y2 + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        return frame

    def process_frame(self, frame):
        """
        Main entry point for the UI.
        Detects and recognizes faces in a single frame.
        Returns (annotated_frame, results)
        """
        self.frame_count += 1

        # Frame skipping for performance
        if self.frame_count > 1 and self.frame_count % (self.skip_frames + 1) != 0:
            return self._draw_results(frame, self._last_results), self._last_results

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.app.get(rgb_frame)

        results = []

        for face in faces:
            embedding = face.normed_embedding
            worker_id, worker_name, distance = self.recognize_face(embedding)

            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox

            color = (0, 255, 0) if worker_id else (0, 0, 255)

            results.append({
                'worker_id': worker_id,
                'name': worker_name,
                'distance': distance,
                'bbox': (x1, y1, x2, y2),
                'color': color
            })

        self._last_results = results
        return self._draw_results(frame, results), results

    def reload_database(self):
        """
        Call this when new workers are registered
        to refresh the in-memory embeddings without restarting.
        """
        self.employee_data = {}
        self.load_employee_database()
        self._build_embedding_matrix()