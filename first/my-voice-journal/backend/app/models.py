# backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from .database import engine, SessionLocal
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VoiceEntry(Base):
    __tablename__ = "voice_entries"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    audio_file_path = Column(String, nullable=True)
    transcription = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    events_tagged = Column(Text, nullable=True)  # could store JSON data or event references

# Create tables if not exist
Base.metadata.create_all(bind=engine)
