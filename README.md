# Emotion Analytics Backend

FastAPI backend for Jetson-based emotion detection system. Receives emotion data from Jetson devices and serves aggregated analytics to the dashboard frontend.

## Features

- **Batch Ingestion**: Receive cumulative emotion times from Jetson devices
- **Upsert Logic**: Automatically update or insert person emotion records
- **Dashboard API**: Serve aggregated emotion statistics and per-person states
- **SQLite Storage**: Lightweight, file-based database for emotion data
- **CORS Enabled**: Ready for Next.js frontend integration

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **ORM**: SQLModel 0.0.14
- **Database**: SQLite
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic 2.5.3

## Project Structure

```
emotion_backend/
├── app/
│   ├── __init__.py        # Package marker
│   ├── main.py            # FastAPI application and endpoints
│   ├── db.py              # Database engine and session management
│   ├── models.py          # SQLModel database models
│   └── schemas.py         # Pydantic request/response schemas
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── emotion.db             # SQLite database (created on first run)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements.txt
```

## Running the Server

### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Local**: http://localhost:8000
- **Network**: http://YOUR_IP:8000

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

**GET /**

Check if the API is running.

**Response:**
```json
{
  "status": "ok"
}
```

### 2. Ingest Emotion Batch

**POST /api/emotions/batch**

Receive batch emotion updates from Jetson device.

**Request Body:**
```json
{
  "device_id": "jetson_1",
  "timestamp": "2025-11-14T12:34:56Z",
  "people": [
    {
      "person_id": "1",
      "cumulative": {
        "happy": 123.5,
        "sad": 20.0,
        "angry": 10.0
      }
    },
    {
      "person_id": "2",
      "cumulative": {
        "happy": 10.0,
        "sad": 0.0,
        "angry": 5.5
      }
    }
  ]
}
```

**Response:**
```json
{
  "status": "ok",
  "updated_count": 2
}
```

**Behavior:**
- Upserts records: updates if (device_id, person_id) exists, inserts otherwise
- Updates `last_seen` timestamp for each person
- Commits all changes atomically

### 3. Dashboard Summary

**GET /api/dashboard/summary?device_id=jetson_1**

Get aggregated emotion statistics for dashboard.

**Query Parameters:**
- `device_id` (optional): Device ID to filter by. Default: "jetson_1"

**Response:**
```json
{
  "device_id": "jetson_1",
  "device_name": "Entrance Camera",
  "updated_at": "2025-11-14T15:30:00Z",
  "emotion_totals": {
    "happy": 14523.0,
    "sad": 3421.0,
    "angry": 1205.0,
    "neutral": 0.0
  },
  "current_people": [
    {
      "person_id": "1",
      "current_emotion": "happy",
      "time_happy": 145.2,
      "time_sad": 23.1,
      "time_angry": 5.3,
      "last_seen": "2025-11-14T15:29:55Z"
    }
  ]
}
```

**Logic:**
- Aggregates total emotion times across all people
- Determines `current_emotion` as the emotion with max time for each person
- Returns empty array if no people detected

## Database Schema

### PersonEmotion Table

| Column      | Type     | Description                              |
|-------------|----------|------------------------------------------|
| id          | INTEGER  | Primary key (auto-increment)             |
| device_id   | TEXT     | Jetson device identifier (indexed)       |
| person_id   | TEXT     | Person identifier (indexed)              |
| time_happy  | FLOAT    | Cumulative happy time (seconds)          |
| time_sad    | FLOAT    | Cumulative sad time (seconds)            |
| time_angry  | FLOAT    | Cumulative angry time (seconds)          |
| last_seen   | DATETIME | Last detection timestamp                 |

**Unique Constraint**: (device_id, person_id) pairs are logically unique via upsert logic.

## CORS Configuration

The API allows requests from:
- http://localhost:3000
- http://127.0.0.1:3000

To add more origins, edit `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://your-domain.com",  # Add your origins here
    ],
    ...
)
```

## Integration Guide

### Jetson Device Integration

From your Jetson device, send POST requests to:

```python
import requests
import json
from datetime import datetime

payload = {
    "device_id": "jetson_1",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "people": [
        {
            "person_id": "1",
            "cumulative": {
                "happy": 123.5,
                "sad": 20.0,
                "angry": 10.0
            }
        }
    ]
}

response = requests.post(
    "http://BACKEND_IP:8000/api/emotions/batch",
    json=payload
)
print(response.json())
```

### Next.js Dashboard Integration

Update your dashboard to fetch from this backend:

```typescript
const fetchDashboardData = async () => {
  const response = await fetch(
    'http://localhost:8000/api/dashboard/summary?device_id=jetson_1'
  );
  const data = await response.json();
  setData(data);
};
```

## Development

### Database Reset

To reset the database, simply delete the SQLite file:

```bash
rm emotion.db
```

The database will be recreated on next server start.

### Enable SQL Logging

Edit `app/db.py` and set `echo=True` in the engine:

```python
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Enable SQL query logging
)
```

## Testing

### Manual Testing with curl

**Health Check:**
```bash
curl http://localhost:8000/
```

**Submit Batch:**
```bash
curl -X POST http://localhost:8000/api/emotions/batch \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "jetson_1",
    "timestamp": "2025-11-14T12:34:56Z",
    "people": [
      {
        "person_id": "1",
        "cumulative": {"happy": 100, "sad": 20, "angry": 5}
      }
    ]
  }'
```

**Get Summary:**
```bash
curl http://localhost:8000/api/dashboard/summary?device_id=jetson_1
```

## Deployment

### Running as a Service (Linux)

Create a systemd service file:

```ini
[Unit]
Description=Emotion Analytics Backend
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/emotion_backend
ExecStart=/usr/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t emotion-backend .
docker run -p 8000:8000 -v $(pwd)/emotion.db:/app/emotion.db emotion-backend
```

## Troubleshooting

### Database Locked Error

If you see "database is locked" errors:
- Ensure only one instance of the server is running
- Check file permissions on `emotion.db`
- Consider using PostgreSQL for concurrent write scenarios

### CORS Errors

If the dashboard can't connect:
- Verify the dashboard origin is in `allow_origins`
- Check that both services are running
- Inspect browser console for specific CORS error messages

## License

Private project

## Version

**v0.1.0** - Initial release with core functionality
