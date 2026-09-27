import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.schemas import QueryRequest, QueryResponse, SessionSummary, ChatMessageOut, SourceRef
from app.services import chat_service
from app.db import get_db
from app.db_models import ChatSession, ChatMessage
from app.deps import get_current_user_optional

router = APIRouter(tags=["chat"])


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
async def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )
    result = []
    for m in messages:
        sources = []
        if m.sources_json:
            try:
                sources = [SourceRef(**s) for s in json.loads(m.sources_json)]
            except Exception:
                sources = []
        result.append(ChatMessageOut(role=m.role, content=m.content, sources=sources))
    return result


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest, db: Session = Depends(get_db), user=Depends(get_current_user_optional)):
    session = db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()
    if not session:
        session = ChatSession(id=payload.session_id, submission_id=payload.session_id, user_id=user.id if user else None)
        db.add(session)
        db.commit()

    db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))
    db.commit()

    result = await chat_service.answer_query(db, payload.session_id, payload.message)

    db.add(ChatMessage(
        session_id=session.id,
        role="ai",
        content=result.answer,
        sources_json=json.dumps([s.model_dump() for s in result.sources]),
    ))
    db.commit()

    return result


@router.get("/sessions", response_model=list[SessionSummary])
async def list_sessions(db: Session = Depends(get_db), user=Depends(get_current_user_optional)):
    q = db.query(ChatSession)
    if user:
        q = q.filter(ChatSession.user_id == user.id)
    sessions = q.order_by(ChatSession.created_at.desc()).all()
    return [
        SessionSummary(
            session_id=s.id,
            label=s.label or s.submission_id,
            last_message_at=s.created_at.strftime("%b %d, %H:%M"),
        )
        for s in sessions
    ]