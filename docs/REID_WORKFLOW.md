# Re-Identification Workflow

## Trigger Points for Re-ID

### 1. **New Detection at Camera** (Most Common)
**When**: Every time a person is detected
**Trigger**: Camera sends detection event
**Process**:
```
1. CV extracts appearance embedding from detection
2. POST /api/reid/search-embedding with the embedding
3. Check similarity scores:
   - Score >= 0.90: Strong match → Use existing global_track_id
   - Score 0.85-0.89: Moderate match → Use with caution, flag for review
   - Score < 0.85: No match → Create new global_track_id
```

### 2. **Person Disappears from One Camera**
**When**: Local track lost at Camera A
**Trigger**: Person not seen for 30-60 seconds
**Process**:
```
1. Mark track as 'lost' (don't close yet)
2. If reappears at Camera B within 2 minutes:
   - Run re-ID to confirm same person
   - Update global_track with new camera location
3. If not seen after 5 minutes:
   - Close the global track
```

### 3. **Better Quality Frame Available**
**When**: Person's face/body clearly visible
**Trigger**: Quality score > 0.90
**Process**:
```
1. Extract new embedding from high-quality frame
2. If confidence in current ID is low (< 85%):
   - Re-run re-ID with better embedding
   - Update global_track if different match found
3. Store as primary embedding for this worker
```

### 4. **Identity Conflict Detection**
**When**: Same person matched to 2 different global_track_ids
**Trigger**: System detects duplicate
**Process**:
```
1. Compare timestamps and locations
2. Merge tracks if actually same person
3. Keep most confident identification
4. Update all related records
```

### 5. **Scheduled Re-verification**
**When**: Every 5-10 minutes for active tracks
**Trigger**: Background job
**Process**:
```
1. Get all active tracks
2. Re-run identification for low-confidence tracks (< 85%)
3. Update if better match found
4. Close stale tracks (not seen in 5+ minutes)
```

### 6. **Manual Re-identification Request**
**When**: Security staff disputes identification
**Trigger**: User action in dashboard
**Process**:
```
1. Fetch all embeddings for the track
2. Allow manual selection of correct worker
3. Update global_track with manual override
4. Mark as "manually verified" (don't auto-update)
```

## Decision Thresholds

| Similarity Score | Action | Confidence |
|-----------------|--------|------------|
| >= 0.95 | Auto-accept, use existing ID | Very High |
| 0.90 - 0.94 | Accept, monitor | High |
| 0.85 - 0.89 | Accept with caution, flag | Medium |
| 0.75 - 0.84 | Possible match, needs review | Low |
| < 0.75 | Reject, create new ID | No Match |

## Intruder Detection Logic
```
Person detected → Run Re-ID → No match?
  ↓
Wait 2 minutes (maybe bad angle/lighting)
  ↓
Still no match → Check if visitor registered
  ↓
Not registered → INTRUDER ALERT
```