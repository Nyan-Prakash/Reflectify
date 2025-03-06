# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VoiceEntryCreate(BaseModel):
    # For uploading audio; might have a file or a file path
    pass

class VoiceEntryOut(BaseModel):
    id: int
    created_at: datetime
    transcription: Optional[str] = None
    sentiment_score: Optional[float] = None
    events_tagged: Optional[str] = None

    class Config:
        orm_mode = True
