"""
Re-Identification Service
Handles the logic for when and how to run re-identification
"""

import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta

from sentence_transformers import SentenceTransformer

class ReIDService:
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_url = api_base_url
        
    def process_new_detection(
        self,
        camera_id: str,
        local_track_id: str,
        embedding: List[float],
        helmet_detected: bool
    ) -> Dict:
        """
        Main Re-ID logic when new person detected.
        
        Returns:
        {
            "global_track_id": "...",
            "worker_id": "..." or None,
            "action": "matched" | "created" | "updated",
            "confidence": 0-100
        }
        """
        
        # Step 1: Search for similar embeddings
        search_result = self._search_embedding(embedding)
        
        if search_result['matches'] and len(search_result['matches']) > 0:
            best_match = search_result['matches'][0]
            similarity = best_match['similarity']
            
            # Step 2: Decide based on similarity
            if similarity >= 0.85:
                # MATCH FOUND - Use existing track
                global_track_id = best_match['global_track_id']
                worker_id = best_match['worker_id']
                
                # Check if person moved cameras
                if best_match['current_camera_id'] != camera_id:
                    # Person moved! Update track
                    self._update_track_location(
                        global_track_id,
                        camera_id,
                        helmet_detected
                    )
                    action = "updated"
                else:
                    # Still at same camera, just update timestamp
                    action = "matched"
                
                return {
                    "global_track_id": global_track_id,
                    "worker_id": worker_id,
                    "action": action,
                    "confidence": int(similarity * 100)
                }
        
        # Step 3: NO MATCH - Create new track
        new_track = self._create_new_track(
            camera_id,
            local_track_id,
            helmet_detected,
            confidence=0  # Unknown person
        )
        
        return {
            "global_track_id": new_track['global_track_id'],
            "worker_id": None,
            "action": "created",
            "confidence": 0,
            "alert": "Potential intruder - no matching worker found"
        }
    
    def _search_embedding(self, embedding: List[float]) -> Dict:
        """Query database for similar embeddings"""
        response = requests.post(
            f"{self.api_url}/api/reid/search-embedding",
            json={
                "feature_vector": embedding,
                "threshold": 0.75,  # Lower threshold for search
                "max_results": 5,
                "search_active_only": True
            }
        )
        return response.json()
    
    def _create_new_track(
        self,
        camera_id: str,
        local_track_id: str,
        helmet_detected: bool,
        worker_id: Optional[str] = None,
        confidence: int = 0
    ) -> Dict:
        """Create new global track"""
        response = requests.post(
            f"{self.api_url}/api/reid/tracks/create",
            json={
                "worker_id": worker_id,
                "camera_id": camera_id,
                "local_track_id": local_track_id,
                "confidence_level": confidence,
                "helmet_status": "compliant" if helmet_detected else "violation"
            }
        )
        return response.json()
    
    def _update_track_location(
        self,
        global_track_id: str,
        new_camera_id: str,
        helmet_detected: bool
    ):
        """Update track when person moves to different camera"""
        response = requests.put(
            f"{self.api_url}/api/reid/tracks/{global_track_id}",
            json={
                "current_camera_id": new_camera_id,
                "helmet_status": "compliant" if helmet_detected else "violation"
            }
        )
        return response.json()
    
    def register_new_worker(
        self,
        worker_id: str,
        embedding: List[float],
        camera_id: str,
        quality_score: float
    ) -> Dict:
        """Register embedding for new worker"""
        response = requests.post(
            f"{self.api_url}/api/reid/embeddings/store",
            json={
                "worker_id": worker_id,
                "feature_vector": embedding,
                "camera_id": camera_id,
                "quality_score": quality_score,
                "is_primary": True  # First embedding is primary
            }
        )
        return response.json()
    
    def close_inactive_tracks(self, inactive_minutes: int = 5):
        """Background job: Close tracks not seen recently"""
        # Get all active tracks
        response = requests.get(f"{self.api_url}/api/reid/active-tracks")
        tracks = response.json()['active_tracks']
        
        now = datetime.now()
        closed_count = 0
        
        for track in tracks:
            last_seen = datetime.fromisoformat(track['last_seen'].replace('Z', '+00:00'))
            time_diff = (now - last_seen).total_seconds() / 60
            
            if time_diff > inactive_minutes:
                # Close this track
                requests.post(
                    f"{self.api_url}/api/reid/tracks/{track['global_track_id']}/close"
                )
                closed_count += 1
        
        return {"closed_tracks": closed_count}

# Usage example
if __name__ == "__main__":
    reid = ReIDService()
    
    # Simulate new detection
    fake_embedding = [0.1] * 512  # 512D vector of 0.1s
    model = SentenceTransformer('distiluse-base-multilingual-cased')
    text = "John Doe works as Software Developer in Engineering department"
    embedding = model.encode(text)
    
    result = reid.process_new_detection(
        camera_id="CAM_001",
        local_track_id="CAM_001_T042",
        embedding=embedding.tolist(),
        helmet_detected=True
    )
    
    print("Re-ID Result:", result)