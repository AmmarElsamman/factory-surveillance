import json
from typing import List

import numpy as np

from Utils.logger import get_logger

from .base import BaseRepository, IRepository
from Entites.WorkerEmbedding import EmbeddingSearchResult, WorkerEmbedding

logger = get_logger(__name__)

class WorkerEmbeddingRepository(BaseRepository[WorkerEmbedding], IRepository[WorkerEmbedding]):
    """
    Repository for WorkerEmbedding Entity
    """
    def add(self, workerEmbedding: WorkerEmbedding) -> str:
        """
        Add new worker embedding to database
        """
        query = """
            INSERT INTO worker_embeddings 
            (worker_id, feature_vector, quality_score, capture_timestamp, camera_id, is_primary, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING embedding_id
        """
        
        self._execute(query, (
            workerEmbedding.worker_id,
            json.dumps(workerEmbedding.feature_vector) if workerEmbedding.feature_vector else None,
            workerEmbedding.quality_score,
            workerEmbedding.capture_timestamp,
            workerEmbedding.camera_id,
            workerEmbedding.is_primary,
            workerEmbedding.created_at
        ))
        
        result = self._fetch_one()
        logger.info(f"Worker embedding for worker {workerEmbedding.worker_id} added to database")
        return result['embedding_id']
    
    def delete(self, embedding_id: int) -> bool:
        """
        Delete worker embedding by ID
        """
        query = """
            DELETE FROM worker_embeddings
            WHERE embedding_id = %s
        """
        
        self._execute(query, (embedding_id,))
        logger.info(f"Worker embedding {embedding_id} deleted from database")
        return True
        
    
    def get_by_worker_id(self, worker_id: str) -> List[WorkerEmbedding]:
        """
        Get all embeddings for a worker
        """
        query = """
            SELECT * FROM worker_embeddings
            WHERE worker_id = %s
        """
        
        self._execute(query, (worker_id,))
        rows = self._fetch_all()
        
        return [self._map_to_entity(row) for row in rows]
    
    def search_by_similarity(self, feature_vector: List[float], top_k: int = 5) -> List[EmbeddingSearchResult]:
        """
        Search for similar embeddings using cosine similarity
        """
        query = """
            SELECT *, 
            (feature_vector <=> %s::vector) AS similarity
            FROM worker_embeddings
            JOIN workers ON worker_embeddings.worker_id = workers.worker_id
            ORDER BY similarity
            LIMIT %s
        """
        
        self._execute(query, (self.to_pgvector(feature_vector), top_k))
        rows = self._fetch_all()
        
        
        return [self._map_to_search_result(row) for row in rows]
    
    def set_primary_embedding(self, embedding_id: int) -> bool:
        """
        Set a specific embedding as primary for the worker
        """
        # First, get the worker_id for the given embedding_id
        query_get_worker = """
            SELECT worker_id FROM worker_embeddings
            WHERE embedding_id = %s
        """
        
        self._execute(query_get_worker, (embedding_id,))
        result = self._fetch_one()
        
        if not result:
            logger.warning(f"Embedding {embedding_id} not found")
            return False
        
        worker_id = result['worker_id']
        
        # Set all embeddings for this worker to is_primary = False
        query_reset_primary = """
            UPDATE worker_embeddings
            SET is_primary = FALSE
            WHERE worker_id = %s
        """
        
        self._execute(query_reset_primary, (worker_id,))
        
        # Set the specified embedding to is_primary = True
        query_set_primary = """
            UPDATE worker_embeddings
            SET is_primary = TRUE
            WHERE embedding_id = %s
        """
        
        self._execute(query_set_primary, (embedding_id,))
        
        logger.info(f"Embedding {embedding_id} set as primary for worker {worker_id}")
        return True
    
    def list_all(self, limit = 100, offset = 0) -> List[WorkerEmbedding]:
        """
        List all worker embeddings
        """
        query = """
            SELECT we.*, w.full_name 
            FROM worker_embeddings we
            JOIN workers w ON we.worker_id = w.worker_id
        """
        
        self._execute(query, (limit, offset))
        rows = self._fetch_all()
        
        return [self._map_to_entity(row) for row in rows]
    
    def get_by_id(self, entity_id):
        raise NotImplementedError("Not implemented")
    def update(self, entity):
        raise NotImplementedError("Not implemented")
    
    def _map_to_entity(self, row) -> WorkerEmbedding:
        """
        Map database row to WorkerEmbedding entity
        """
        return WorkerEmbedding(
            embedding_id=row['embedding_id'],
            worker_id=row['worker_id'],
            camera_id=row['camera_id'],
            name = row['full_name'] if 'full_name' in row else None,
            feature_vector=json.loads(row['feature_vector']) if row['feature_vector'] else None,
            quality_score=row['quality_score'],
            is_primary=row['is_primary'],
            capture_timestamp=row['capture_timestamp'],
            created_at=row['created_at']
        )
    
    def _map_to_search_result(self, row) -> EmbeddingSearchResult:
        """
        Map database row to EmbeddingSearchResult model
        """
        return EmbeddingSearchResult(
            embedding_id=row['embedding_id'],
            worker_id=row['worker_id'],
            full_name=row['full_name'],
            similarity=row['similarity'],
            is_primary=row['is_primary']
        )
        
    
    def to_pgvector(self, vec: List[float]) -> str:
            return "[" + ",".join(map(str, vec)) + "]"
    