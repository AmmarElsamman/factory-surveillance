"""
WorkerEmbedding Entity
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

@dataclass
class WorkerEmbedding:
    """
    WorkerEmbedding Entity
    Represents the embedding vector for a worker
    """
    worker_id: str
    camera_id: str
    feature_vector: List[float]
    embedding_id: Optional[int] = None
    quality_score: Optional[float] = None
    is_primary: bool = False
    capture_timestamp: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    def set_as_primary_embedding(self):
        self.is_primary = True

@dataclass
class EmbeddingSearchResult:
    """Model for embedding search result"""
    embedding_id: int
    worker_id: str
    full_name: str
    similarity: float
    is_primary: bool