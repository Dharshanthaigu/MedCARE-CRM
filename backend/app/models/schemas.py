from pydantic import BaseModel
from typing import List, Optional


class SubmissionCreatedResponse(BaseModel):
    submission_id: str


class PipelineStatusResponse(BaseModel):
    submission_id: str
    stages_done: int          # 0-5
    active_stage: Optional[int] = None   # 1-5 while processing, None when idle/done
    chunks: Optional[int] = None
    ocr_confidence: Optional[float] = None
    avg_latency_ms: Optional[int] = None


class SourceRef(BaseModel):
    doc: str
    location: str
    snippet: Optional[str] = None


class QueryRequest(BaseModel):
    session_id: str
    message: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceRef] = []
    tool_calls: List[str] = []


class SessionSummary(BaseModel):
    session_id: str
    label: str
    last_message_at: str


class ChatMessageOut(BaseModel):
    role: str
    content: str
    sources: List[SourceRef] = []


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    staff_id: str
    role: str   # "Admin" | "Chief Nurse" | "Doctor / Staff"


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    staff_id: str
    role: str


class AuthResponse(BaseModel):
    token: str
    user: UserOut