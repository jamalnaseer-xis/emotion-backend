from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class PersonEmotion(SQLModel, table=True):
    """
    Database model for storing per-person cumulative emotion times.

    Each record represents one person detected by one device.
    Cumulative times are in seconds.
    """
    __tablename__ = "person_emotions"

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(index=True)
    person_id: str = Field(index=True)
    time_happy: float = Field(default=0.0)
    time_sad: float = Field(default=0.0)
    time_angry: float = Field(default=0.0)
    last_seen: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
