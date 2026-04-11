from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from datetime import datetime, timedelta
import json
import psycopg2
import numpy as np

from models import (
    DetectionEvent, WorkerLocation, AlertResponse, 
    EmbeddingQuery, CreateGlobalTrack, UpdateGlobalTrack
)

from database import get_db_connection

app = FastAPI(
    title="Factory Surveillance API",
    description="Database API for smart security camera system",
    version="1.0.0"
)



# ============================================
# Health Check
# ============================================

@app.get("/")
async def root():
    return {
        "service": "Factory Surveillance Database API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database unhealthy: {str(e)}")
    
    
# ============================================
# Re-Identification Endpoints
# ============================================

# @app.post("/api/reid/search-embedding")
# async def search_similar_embeddings(query: EmbeddingQuery):
#     """
#     Search for similar embeddings to identify a person.
    
#     This is the MAIN Re-ID function.
    
#     Usage:
#     1. CV team detects person and extracts 512D embedding
#     2. Send embedding to this endpoint
#     3. Get back list of potential matches with similarity scores
#     4. If top match > threshold, it's the same person
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     model = SentenceTransformer('distiluse-base-multilingual-cased')
#     def to_pgvector(vec: np.ndarray) -> str:
#         return "[" + ",".join(map(str, vec.tolist())) + "]"
    
#     text = "John Doe works as Software Developer in Engineering department"
#     embedding = model.encode(text)
    
#     query2 = EmbeddingQuery(
#     feature_vector=embedding.tolist(),  # 512-dim vector with all 0.5
#     threshold=0.90,
#     max_results=2,
#     search_active_only=False
# )
    
#     try:
#         # Convert list to PostgreSQL vector format
#         vector_str = json.dumps([float(x) for x in query2.feature_vector])
        
        
#         # Search all registered workers (slower, fallback)
#         sql = """
#             SELECT 
#                 we.embedding_id,
#                 we.worker_id,
#                 w.full_name as worker_name,
#                 NULL as global_track_id,
#                 NULL as current_camera_id,
#                 NULL as last_seen,
#                 1 - (we.feature_vector <=> %s::vector) as similarity
#             FROM worker_embeddings we
#             JOIN workers w ON we.worker_id = w.worker_id
#             WHERE we.is_primary = true
#                 AND w.status = 'active'
#             ORDER BY similarity DESC
#             LIMIT %s
#         """
#         cursor.execute(sql, (vector_str, query2.max_results))
#         matches = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return {"matches": matches, "count": len(matches)}
        
    
#     except Exception as e:
#         cursor.close()
#         conn.close()
#         raise HTTPException(status_code=500, detail=f"Embedding search failed: {str(e)}")

# @app.get("/api/reid/active-tracks")
# async def get_active_track_embeddings():
#     """
#     Get embeddings of all currently active tracks.
#     Used for cross-camera re-identification.
    
#     When person appears at Camera 2, compare against all active tracks
#     from other cameras to see if they just moved.
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     cursor.execute("""
#         SELECT 
#             gt.global_track_id,
#             gt.worker_id,
#             w.full_name,
#             gt.current_camera_id,
#             c.location_name,
#             gt.last_seen,
#             we.feature_vector,
#             we.embedding_id
#         FROM global_tracks gt
#         LEFT JOIN workers w ON gt.worker_id = w.worker_id
#         LEFT JOIN cameras c ON gt.current_camera_id = c.camera_id
#         LEFT JOIN worker_embeddings we ON w.worker_id = we.worker_id AND we.is_primary = true
#         WHERE gt.track_status = 'active'
#             AND gt.last_seen > NOW() - INTERVAL '5 minutes'
#         ORDER BY gt.last_seen DESC
#     """)
    
#     tracks = cursor.fetchall()
#     cursor.close()
#     conn.close()
    
#     return {
#         "active_tracks": tracks,
#         "count": len(tracks)
#     }
    
    
#     # TODO:
#     # When registering new worker or updating their appearance
#     # GET /api/reid/worker/{worker_id}/embeddings

# ============================================
# Track Management Endpoints
# ============================================
@app.post("/api/reid/tracks/create")
async def create_global_track(track: CreateGlobalTrack):
    """
    Create a new global track when person is detected for first time.
    
    Called when:
    - New person detected with no matching embedding
    - Potential intruder
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO global_tracks 
            (worker_id, current_camera_id, track_status, first_seen, 
             last_seen, confidence_level, is_intruder_suspect, helmet_status)
            VALUES (%s, %s, 'active', NOW(), NOW(), %s, %s, %s)
            RETURNING global_track_id
        """, (
            track.worker_id,
            track.camera_id,
            track.confidence_level,
            track.worker_id is None,  # is_intruder_suspect if no worker_id
            track.helmet_status
        ))
        
        result = cursor.fetchone()
        global_track_id = result['global_track_id']
        
        # Also create initial trajectory entry
        cursor.execute("""
            INSERT INTO track_trajectory
            (global_track_id, camera_id, entry_time, path_sequence)
            VALUES (%s, %s, NOW(), 1)
        """, (global_track_id, track.camera_id))
        
        conn.commit()
        
        # If this is a potential intruder, create alert
        if track.worker_id is None:
            cursor.execute("""
                INSERT INTO alerts
                (alert_type, global_track_id, camera_id, timestamp, 
                 severity, status, description)
                VALUES ('intruder', %s, %s, NOW(), 'critical', 'new', 
                        'Unidentified person detected')
            """, (global_track_id, track.camera_id))
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "global_track_id": str(global_track_id),
            "worker_id": track.worker_id,
            "status": "created",
            "is_intruder_suspect": track.worker_id is None
        }
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/api/reid/tracks/{global_track_id}")
async def update_global_track(global_track_id: str, update: UpdateGlobalTrack):
    """
    Update an existing global track.
    
    Called when:
    - Person moves to different camera
    - Helmet status changes
    - Re-identification confidence updated
    
    - ses row-level locking (FOR UPDATE) to prevent concurrent modification conflicts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Lock the row for the duration of this transaction
        # This prevents other concurrent updates from reading stale data
        # Check if camera changed (person moved)
        cursor.execute("""
            SELECT current_camera_id, worker_id
            FROM global_tracks
            WHERE global_track_id = %s
            FOR UPDATE
        """, (global_track_id,))
        
        current = cursor.fetchone()
        if not current:
            raise HTTPException(status_code=404, detail="Track not found")
        
        if update.current_camera_id is None:
            raise HTTPException(status_code=400, detail="current_camera_id is required")
        
        camera_changed = current['current_camera_id'] != update.current_camera_id
        
        # Update the track
        update_fields = ["last_seen = NOW()"]
        params = []
        
        if update.current_camera_id:
            update_fields.append("current_camera_id = %s")
            params.append(update.current_camera_id)
        
        if update.helmet_status:
            update_fields.append("helmet_status = %s")
            params.append(update.helmet_status)
        
        if update.confidence_level is not None:
            update_fields.append("confidence_level = %s")
            params.append(update.confidence_level)
        
        params.append(global_track_id)
        
        cursor.execute(f"""
            UPDATE global_tracks
            SET {', '.join(update_fields)}
            WHERE global_track_id = %s
        """, params)
        
        # If camera changed, update trajectory
        if camera_changed:
            # Close previous trajectory entry
            cursor.execute("""
                UPDATE track_trajectory
                SET exit_time = NOW(),
                    duration = NOW() - entry_time
                WHERE global_track_id = %s 
                    AND exit_time IS NULL
            """, (global_track_id,))
            
            # Create new trajectory entry
            cursor.execute("""
                INSERT INTO track_trajectory
                (global_track_id, camera_id, entry_time, path_sequence)
                SELECT %s, %s, NOW(), COALESCE(MAX(path_sequence), 0) + 1
                FROM track_trajectory
                WHERE global_track_id = %s
            """, (global_track_id, update.current_camera_id, global_track_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "global_track_id": global_track_id,
            "status": "updated",
            "camera_changed": camera_changed
        }
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reid/tracks/{global_track_id}/close")
async def close_global_track(global_track_id: str):
    """
    Close a global track when person leaves premises or not seen for long time.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE global_tracks
            SET track_status = 'closed'
            WHERE global_track_id = %s
        """, (global_track_id,))
        
        # Close any open trajectory entries
        cursor.execute("""
            UPDATE track_trajectory
            SET exit_time = NOW(),
                duration = NOW() - entry_time
            WHERE global_track_id = %s 
                AND exit_time IS NULL
        """, (global_track_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"global_track_id": global_track_id, "status": "closed"}
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

# Msh 3arf hnst5dmo ezay lsa
@app.post("/api/reid/tracks/{global_track_id}/link-worker")
async def link_track_to_worker(global_track_id: str, worker_id: str, confidence: int):
    """
    Link an unidentified track to a worker (late identification).
    
    Called when:
    - Initially detected as unknown
    - Later identified through better view/embedding
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE global_tracks
            SET worker_id = %s,
                confidence_level = %s,
                is_intruder_suspect = false
            WHERE global_track_id = %s
        """, (worker_id, confidence, global_track_id))
        
        # Resolve any intruder alerts for this track
        cursor.execute("""
            UPDATE alerts
            SET status = 'resolved',
                resolution_notes = 'Identified as registered worker',
                resolved_at = NOW()
            WHERE global_track_id = %s 
                AND alert_type = 'intruder'
                AND status = 'new'
        """, (global_track_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "global_track_id": global_track_id,
            "worker_id": worker_id,
            "status": "linked"
        }
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Detection Events Endpoint
# ============================================

@app.post("/api/detections", status_code=201)
async def create_detection_events(event: DetectionEvent):
    """
    Receive detection events from CV team
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        inserted_events = []
        
        for detection in event.detections:
            # For now, we'll create a temporary global_track_id
            # Later, your ReID system will assign proper IDs
            cursor.execute("""
                INSERT INTO detection_events 
                (camera_id, timestamp, bounding_box, helmet_detected, 
                 confidence_score, local_track_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING event_id
            """, (
                event.camera_id,
                event.timestamp,
                detection.bounding_box.json(),
                detection.helmet_detected,
                detection.person_confidence,
                detection.local_track_id
            ))
            
            event_id = cursor.fetchone()['event_id']
            inserted_events.append(event_id)
            
            # Check for helmet violation
            if not detection.helmet_detected and detection.helmet_confidence > 0.80:
                cursor.execute("""
                    INSERT INTO alerts 
                    (alert_type, camera_id, timestamp, severity, status, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    'helmet_violation',
                    event.camera_id,
                    event.timestamp,
                    'high',
                    'new',
                    f'Helmet violation detected at {event.camera_id}'
                ))
        
        conn.commit()
        
        return {
            "status": "success",
            "message": f"Inserted {len(inserted_events)} detection events",
            "event_ids": inserted_events
        }
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cursor.close()
        conn.close()

# ============================================
# Query Endpoints
# ============================================

@app.get("/api/cameras")
async def get_cameras():
    """Get all cameras"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT camera_id, location_name, zone_type, status
            FROM cameras
            ORDER BY camera_id
        """)    
        cameras = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
        
    return {"cameras": cameras}

@app.get("/api/workers")
async def get_workers(status: Optional[str] = Query(None)):
    """Get all workers, optionally filtered by status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:    
        if status:
            cursor.execute("""
                SELECT worker_id, employee_code, full_name, department, role, status
                FROM workers
                WHERE status = %s
                ORDER BY full_name
            """, (status,))
        else:
            cursor.execute("""
                SELECT worker_id, employee_code, full_name, department, role, status
                FROM workers
                ORDER BY full_name
            """)
        workers = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
        
    return {"workers": workers}

@app.get("/api/worker_embeddings")
async def get_worker_embeddings():
    """Get all workers embeddings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:    
        cursor.execute("""
            SELECT 
                we.embedding_id,
                we.worker_id,
                w.full_name,
                we.feature_vector,
                we.quality_score,
                we.camera_id,
                we.is_primary,
                we.created_at
            FROM worker_embeddings we
            JOIN workers w ON we.worker_id = w.worker_id
            ORDER BY w.full_name
        """)
        embeddings = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
        
    return {"embeddings": embeddings}

@app.post("/api/worker_embeddings/{employee_code}")
async def insert_worker_embedding(employee_code: str):
    """Insert a single embedding for a worker (for testing)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Locate file relative to project root
    file_path = Path(__file__).resolve().parent.parent / "grad-project" / "employee_data" / f"{employee_code}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Employee file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        embedding = data.get("embedding")
        if not embedding or not isinstance(embedding, list):
            raise HTTPException(status_code=400, detail="Invalid embedding data in file")
        
        if len(embedding) != 512:
            raise HTTPException(status_code=400, detail="Embedding must be 512 dimensions")
        
        def to_pgvector(vec: np.ndarray) -> str:
            return "[" + ",".join(map(str, vec.tolist())) + "]"
        
        cursor.execute("""
                       SELECT worker_id, full_name, department, role
                       FROM workers 
                       WHERE employee_code=%s
                       """, (employee_code,))
        worker = cursor.fetchone()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        
            
        INSERT_SQL = """
                    INSERT INTO worker_embeddings (
                        worker_id,
                        feature_vector,
                        quality_score,
                        capture_timestamp,
                        camera_id,
                        is_primary
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
        cursor.execute(
                    INSERT_SQL, 
                    (
                        worker["worker_id"],
                        embedding,
                        round(np.random.uniform(0.8, 1.0), 3),
                        datetime.utcnow(),
                        f"CAM_0{np.random.randint(1,4)}",
                        True 
                    )
                )
        conn.commit()
        return {"status": "embedding inserted", "employee_code": employee_code}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/worker_embeddings/upload")
async def upload_embedding():
    
    
    model = SentenceTransformer('distiluse-base-multilingual-cased')
    def to_pgvector(vec: np.ndarray) -> str:
        return "[" + ",".join(map(str, vec.tolist())) + "]"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
                       SELECT worker_id, full_name, department, role
                       FROM workers 
                       WHERE status='active'
                       """)
        
        workers = cursor.fetchall()
        print(f"Found {len(workers)} active workers")
        
        INSERT_SQL = """
                        INSERT INTO worker_embeddings (
                            worker_id,
                            feature_vector,
                            quality_score,
                            capture_timestamp,
                            camera_id,
                            is_primary
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
        for worker in workers:
            base_text = f"{worker['full_name']} work as {worker['role']} in {worker['department']} department"
            for i in range(10):
                variation_text = f"{base_text}. capture variation {i}"
                embedding = model.encode(variation_text)
                
                cursor.execute(
                    INSERT_SQL, 
                    (
                        worker["worker_id"],
                        to_pgvector(embedding),
                        round(np.random.uniform(0.8, 1.0), 3),
                        datetime.utcnow(),
                        f"CAM_0{np.random.randint(1,4)}",
                        True if i == 0 else False
                    )
                )
    finally:
        conn.commit()
        cursor.close()
        conn.close()    
    
    return {"status": "embeddings uploaded"}

@app.get("/api/workers/{worker_id}/location", response_model=WorkerLocation)
async def get_worker_location(worker_id: str):
    """Get current location of a specific worker"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                w.worker_id,
                w.full_name,
                gt.current_camera_id as camera_id,
                c.location_name,
                gt.last_seen,
                gt.helmet_status
            FROM global_tracks gt
            JOIN workers w ON gt.worker_id = w.worker_id
            JOIN cameras c ON gt.current_camera_id = c.camera_id
            WHERE w.worker_id = %s 
            AND gt.track_status = 'active'
            ORDER BY gt.last_seen DESC
            LIMIT 1
        """, (worker_id,))
        result = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Worker not found or not currently tracked")
    
    return result

@app.get("/api/alerts", response_model=List[AlertResponse])
async def get_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    hours: int = Query(24, description="Get alerts from last N hours")
):
    """Get recent alerts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            a.alert_id,
            a.alert_type,
            a.camera_id,
            c.location_name,
            a.timestamp,
            a.severity,
            a.status,
            a.description
        FROM alerts a
        JOIN cameras c ON a.camera_id = c.camera_id
        WHERE a.timestamp > %s
    """
    params = [datetime.now() - timedelta(hours=hours)]
    
    if status:
        query += " AND a.status = %s"
        params.append(status)
    
    if severity:
        query += " AND a.severity = %s"
        params.append(severity)
    
    query += " ORDER BY a.timestamp DESC LIMIT 100"
    
    cursor.execute(query, params)
    alerts = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return alerts

@app.get("/api/detections/recent")
async def get_recent_detections(
    camera_id: Optional[str] = Query(None),
    minutes: int = Query(10, description="Get detections from last N minutes")
):
    """Get recent detection events"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            de.event_id,
            de.camera_id,
            c.location_name,
            de.timestamp,
            de.local_track_id,
            de.helmet_detected,
            de.confidence_score
        FROM detection_events de
        JOIN cameras c ON de.camera_id = c.camera_id
        WHERE de.timestamp > %s
    """
    params = [datetime.now() - timedelta(minutes=minutes)]
    
    if camera_id:
        query += " AND de.camera_id = %s"
        params.append(camera_id)
    
    query += " ORDER BY de.timestamp DESC LIMIT 200"
    
    cursor.execute(query, params)
    detections = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {"detections": detections}

# ============================================
# Statistics Endpoint
# ============================================

@app.get("/api/stats/summary")
async def get_summary_stats():
    """Get overall system statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Active workers
    cursor.execute("""
        SELECT COUNT(DISTINCT worker_id) as active_workers
        FROM global_tracks
        WHERE track_status = 'active'
          AND last_seen > NOW() - INTERVAL '5 minutes'
    """)
    active_workers = cursor.fetchone()['active_workers']
    
    # Recent alerts
    cursor.execute("""
        SELECT COUNT(*) as recent_alerts
        FROM alerts
        WHERE timestamp > NOW() - INTERVAL '1 hour'
          AND status = 'new'
    """)
    recent_alerts = cursor.fetchone()['recent_alerts']
    
    # Helmet compliance today
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE helmet_detected = true) as compliant,
            COUNT(*) FILTER (WHERE helmet_detected = false) as violations,
            COUNT(*) as total
        FROM detection_events
        WHERE timestamp > CURRENT_DATE
    """)
    compliance = cursor.fetchone()
    
    compliance_rate = 0
    if compliance['total'] > 0:
        compliance_rate = round((compliance['compliant'] / compliance['total']) * 100, 2)
    
    cursor.close()
    conn.close()
    
    return {
        "active_workers": active_workers,
        "recent_alerts": recent_alerts,
        "helmet_compliance_today": {
            "compliant": compliance['compliant'],
            "violations": compliance['violations'],
            "total": compliance['total'],
            "compliance_rate_percent": compliance_rate
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)