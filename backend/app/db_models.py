"""
ORM models — the real, persistent replacement for the in-memory dicts
used in Phase 0 (auth_service.py's _USERS/_TOKENS, rag_pipeline.py's _STATE).

Run `python scripts/init_db.py` once (after docker-compose up) to create
these tables and enable the pgvector extension.
"""

import datetime
import uuid

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.db import Base
from app.config import EMBEDDING_DIM


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: _uid("USR"))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    staff_id = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)  # "Admin" | "Chief Nurse" | "Doctor / Staff"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    submissions = relationship("Submission", back_populates="user")
    tokens = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    token = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="tokens")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=lambda: _uid("SUB"))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    patient_id = Column(String, nullable=True)
    department = Column(String, nullable=True)
    submission_type = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="submissions")
    documents = relationship("Document", back_populates="submission", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="submission", cascade="all, delete-orphan")
    pipeline_run = relationship("PipelineRun", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="submission", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(String, ForeignKey("submissions.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    storage_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    submission = relationship("Submission", back_populates="documents")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(String, ForeignKey("submissions.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
    chunk_index = Column(Integer, nullable=True)
    page = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    submission = relationship("Submission", back_populates="chunks")


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(String, ForeignKey("submissions.id"), unique=True, nullable=False)
    stages_done = Column(Integer, default=0)
    active_stage = Column(Integer, nullable=True)
    chunks_count = Column(Integer, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    avg_latency_ms = Column(Integer, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    submission = relationship("Submission", back_populates="pipeline_run")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: _uid("SESS"))
    submission_id = Column(String, ForeignKey("submissions.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    label = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    submission = relationship("Submission", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")