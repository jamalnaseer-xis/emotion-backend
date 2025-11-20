from datetime import datetime
from typing import List, Dict, Optional

from pydantic import BaseModel, Field


# ============================================================
# INGEST SCHEMAS (Jetson → Backend)
# ============================================================

class PersonCumulativeIn(BaseModel):
    """
    Per-person cumulative emotion times from Jetson.
    Example:
      {
        "person_id": "1",
        "cumulative": { "happy": 120.5, "sad": 10.0, "angry": 0.0 }
      }
    """
    person_id: str
    cumulative: Dict[str, float] = Field(
        description="Cumulative seconds for each emotion (happy, sad, angry)"
    )


class EmotionsBatchIn(BaseModel):
    """
    Batch update from Jetson device.

    Example:
      {
        "device_id": "jetson_1",
        "timestamp": "2025-11-14T12:34:56Z",
        "people": [
          {
            "person_id": "1",
            "cumulative": { "happy": 120.5, "sad": 10.0, "angry": 0.0 }
          }
        ]
      }
    """
    device_id: str
    timestamp: str = Field(description="ISO 8601 timestamp")
    people: List[PersonCumulativeIn]


class EmotionsBatchResponse(BaseModel):
    """Response after processing batch update."""
    status: str
    updated_count: int


# ============================================================
# DASHBOARD SCHEMAS (Backend → Dashboard)
# ============================================================

class EmotionTotalsOut(BaseModel):
    """Aggregated emotion totals across all people."""
    happy: float = 0.0
    sad: float = 0.0
    angry: float = 0.0
    neutral: float = 0.0


class PersonStateOut(BaseModel):
    """Individual person's emotion state."""
    person_id: str
    current_emotion: str = Field(
        description="Dominant emotion: happy|sad|angry|neutral"
    )
    time_happy: float
    time_sad: float
    time_angry: float
    last_seen: str = Field(description="ISO 8601 timestamp")


class DashboardSummaryOut(BaseModel):
    """Complete dashboard summary response used by the dashboard."""
    device_id: str
    device_name: str
    updated_at: str = Field(
        description="ISO 8601 timestamp when summary was generated"
    )
    emotion_totals: EmotionTotalsOut
    current_people: List[PersonStateOut]


# ============================================================
# HEALTH CHECK
# ============================================================

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str


# ============================================================
# VIDEO STREAM (MJPEG) UPLOAD
# ============================================================

class FrameUpload(BaseModel):
    """
    Single annotated frame from Jetson, base64-encoded JPEG.

    Example:
      {
        "device_id": "jetson_1",
        "frame_b64": "<base64-string>",
        "timestamp": "2025-11-14T12:34:56Z"
      }
    """
    device_id: str
    frame_b64: str  # base64-encoded JPEG frame
    timestamp: Optional[datetime] = None
