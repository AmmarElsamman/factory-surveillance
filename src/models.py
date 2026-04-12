from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BoundingBox(BaseModel):
    """Bounding box coordinates"""
    x: int = Field(..., description="X coordinate of top-left corner")
    y: int = Field(..., description="Y coordinate of top-left corner")
    width: int = Field(..., description="Width of bounding box")
    height: int = Field(..., description="Height of bounding box")

class CreateGlobalTrack(BaseModel):
    """Create new global track"""
    worker_id: Optional[str] = None
    camera_id: str
    local_track_id: str
    confidence_level: int
    helmet_status: str = "unknown"

class UpdateGlobalTrack(BaseModel):
    """Update existing global track"""
    current_camera_id: str
    helmet_status: Optional[str] = None
    confidence_level: Optional[int] = None

class Detection(BaseModel):
    """Detection model"""
    local_track_id: str
    bounding_box: BoundingBox
    person_confidence: float = Field(..., ge=0.0, le=1.0)
    helmet_detected: bool
    helmet_confidence: float = Field(..., ge=0.0, le=1.0)
    snapshot_base64: Optional[str] = None

class DetectionEvent(BaseModel):
    """Detection event sent from cameras"""
    camera_id: str
    timestamp: datetime
    detections: List[Detection]

class EmbeddingQuery(BaseModel):
    """Model for embedding similarity search"""
    feature_vector: List[float] = Field(..., description="512D embedding vector")
    threshold: float = Field(0.85, description="Minimum similarity score")
    max_results: int = Field(5, description="Maximum number of results")
    search_active_only: bool = Field(True, description="Only search active tracks")

class EmbeddingMatch(BaseModel):
    """Model for embedding match result"""
    global_track_id: Optional[str]
    worker_id: Optional[str]
    worker_name: Optional[str]
    similarity_score: float
    last_seen: Optional[datetime]
    current_camera_id: Optional[str]
    embedding_id: int

class WorkerLocation(BaseModel):
    """Worker location and status"""
    worker_id: str
    full_name: str
    camera_id: str
    location_name: str
    last_seen: datetime
    helmet_status: str

class AlertResponse(BaseModel):
    """Alert response model"""
    alert_id: int
    alert_type: str
    camera_id: str
    location_name: str
    timestamp: datetime
    severity: str
    status: str
    description: str

class StoreEmbeddingRequest(BaseModel):
    """worker embedding storage request model"""
    worker_id: str
    camera_id: str
    feature_vector: List[float]
    quality_score: Optional[float] = None
    is_primary: bool = False

