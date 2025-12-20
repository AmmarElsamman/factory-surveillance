# Re-ID Integration Architecture

## Data Flow

```
┌─────────────────┐
│   Camera 1      │
│   (Edge Device) │
└────────┬────────┘
         │ 1. Detection Event
         │    {camera_id, timestamp,
         │     detections: [{bbox, helmet, ...}]}
         ▼
┌─────────────────┐
│  CV Processing  │
│  - Extract      │
│    embedding    │
│  - Quality      │
│    assessment   │
└────────┬────────┘
         │ 2. Embedding Query
         │    POST /api/reid/search-embedding
         │    {feature_vector: [512D]}
         ▼
┌─────────────────────────────────────┐
│  Database API (Your Part)           │
│                                     │
│  1. Vector similarity search        │
│  2. Return top matches              │
│     [{similarity, worker_id, ...}]  │
└────────┬────────────────────────────┘
         │ 3. Match Results
         ▼
┌─────────────────┐
│  Re-ID Service  │
│  (Your Logic)   │
│                 │
│  Decision:      │
│  • Match >=0.85?│
│    → Use ID     │
│  • No match?    │
│    → New ID     │
└────────┬────────┘
         │ 4a. Create/Update Track
         │     POST /api/reid/tracks/create
         │     PUT /api/reid/tracks/{id}
         │
         │ 4b. Store Detection
         │     POST /api/detections
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   - Tracks      │
│   - Embeddings  │
│   - Detections  │
│   - Alerts      │
└────────┬────────┘
         │ 5. Query Results
         ▼
┌─────────────────┐
│   Dashboard     │
│   - Live map    │
│   - Alerts      │
│   - Reports     │
└─────────────────┘
```
