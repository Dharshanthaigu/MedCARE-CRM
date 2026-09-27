from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.schemas import PipelineStatusResponse
from app.services import rag_pipeline
from app.db import get_db

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.get("/status/{submission_id}", response_model=PipelineStatusResponse)
async def get_status(submission_id: str, db: Session = Depends(get_db)):
    state = rag_pipeline.get_status(db, submission_id)
    if state is None:
        return PipelineStatusResponse(submission_id=submission_id, stages_done=0)
    return PipelineStatusResponse(**state)


@router.post("/rerun/{submission_id}", response_model=PipelineStatusResponse)
async def rerun(submission_id: str, db: Session = Depends(get_db)):
    state = rag_pipeline.rerun(db, submission_id)
    if state is None:
        raise HTTPException(status_code=404, detail="submission not found")
    return PipelineStatusResponse(**state)