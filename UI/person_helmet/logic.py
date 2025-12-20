import cv2
import numpy as np
import time
from pathlib import Path
from collections import deque, defaultdict
from ultralytics import YOLO

# ---------- 1. Configuration ----------
HELMET_DETECTION_THRESHOLD = 3  # Number of frames required to confirm helmet
TRACKING_HISTORY_SIZE = 5       # Total frames in rolling window
MIN_PERSON_CONFIDENCE = 0.3
MIN_HELMET_CONFIDENCE = 0.5     # 50% threshold

# ---------- 2. Helper Classes ----------
class HelmetTracker:
    """
    System to track helmet detection across multiple frames
    """
    def __init__(self, history_size=5, detection_threshold=3):
        self.history_size = history_size
        self.detection_threshold = detection_threshold
        self.person_history = defaultdict(lambda: deque(maxlen=history_size))
    
    def update(self, person_id, has_helmet):
        self.person_history[person_id].append(has_helmet)
    
    def is_helmet_confirmed(self, person_id):
        if person_id not in self.person_history:
            return False
        history = self.person_history[person_id]
        if len(history) < 3:
            return False
        return sum(history) >= self.detection_threshold
    
    def get_detection_count(self, person_id):
        if person_id not in self.person_history:
            return 0
        return sum(self.person_history[person_id])
    
    def cleanup_old_persons(self, current_person_ids):
        all_ids = list(self.person_history.keys())
        for person_id in all_ids:
            if person_id not in current_person_ids:
                del self.person_history[person_id]

class HelmetVestEngine:
    def __init__(self):
        # --- PATH RESOLUTION ---
        # inside __init__:
        base_dir = Path(__file__).resolve().parent
        model_person_path = base_dir / "01.pt"
        model_helmet_path = base_dir / "helmet.pt"

        missing = [p for p in (model_person_path, model_helmet_path) if not p.exists()]
        if missing:
            raise FileNotFoundError(
                "Missing model files: "
                + ", ".join(str(p) for p in missing)
                + ". Put the model files in the folder "
                + f"`{base_dir}` or update the paths."
            )

        self.model_person = YOLO(str(model_person_path))
        self.model_helmet = YOLO(str(model_helmet_path))
        print("✅ Models loaded successfully!")

        # Initialize tracking system
        self.tracker = HelmetTracker(TRACKING_HISTORY_SIZE, HELMET_DETECTION_THRESHOLD)

    def get_person_id(self, x1, y1, x2, y2):
        """Simple spatial ID generator"""
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return f"{center_x // 100}_{center_y // 100}"

    def process_frame(self, frame):
        output_frame = frame.copy()
        
        # Run Person Detection
        results_person = self.model_person(frame, imgsz=640, verbose=False)[0]
        person_counter = 0
        current_person_ids = []
        
        for box in results_person.boxes:
            conf = float(box.conf[0])
            if conf < MIN_PERSON_CONFIDENCE:
                continue

            cls_id = int(box.cls[0])
            if self.model_person.names[cls_id].lower() != "person":
                continue

            person_counter += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Generate ID and track presence
            person_id = self.get_person_id(x1, y1, x2, y2)
            current_person_ids.append(person_id)

            # Draw Person Box (Green)
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(output_frame, f"Person {conf:.2f}", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Crop Person Region
            x1_c, y1_c = max(0, x1), max(0, y1)
            x2_c, y2_c = min(frame.shape[1], x2), min(frame.shape[0], y2)
            person_crop = frame[y1_c:y2_c, x1_c:x2_c]
            
            helmet_detected_in_frame = False
            highest_helmet_conf = 0.0

            if person_crop.shape[0] >= 20 and person_crop.shape[1] >= 20:
                # Run Helmet Detection on Crop
                results_helmet = self.model_helmet(person_crop, imgsz=640, verbose=False)[0]
                
                for h_box in results_helmet.boxes:
                    h_conf = float(h_box.conf[0])
                    if h_conf < MIN_HELMET_CONFIDENCE:
                        continue

                    h_cls_id = int(h_box.cls[0])
                    h_class_name = self.model_helmet.names[h_cls_id]
                    
                    if any(k in h_class_name.lower() for k in ["helmet", "headgear"]):
                        helmet_detected_in_frame = True
                        highest_helmet_conf = max(highest_helmet_conf, h_conf)
                        
                        hx1, hy1, hx2, hy2 = map(int, h_box.xyxy[0])
                        # Draw Helmet (Blue/Orange)
                        cv2.rectangle(output_frame, 
                                      (x1_c + hx1, y1_c + hy1), 
                                      (x1_c + hx2, y1_c + hy2), 
                                      (255, 150, 0), 2)

            # Update Tracker
            self.tracker.update(person_id, helmet_detected_in_frame)
            
            # Check Confirmation
            helmet_confirmed = self.tracker.is_helmet_confirmed(person_id)
            detect_count = self.tracker.get_detection_count(person_id)

            # UI Text for Tracking Status
            status_text = f"H: {detect_count}/{TRACKING_HISTORY_SIZE}"
            cv2.putText(output_frame, status_text, (x1, y2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            if helmet_confirmed:
                cv2.putText(output_frame, "HELMET OK", (x1, y1 - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(output_frame, "NO HELMET!", (x1, y1 - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Cleanup disappeared persons
        self.tracker.cleanup_old_persons(current_person_ids)

        return output_frame, person_counter