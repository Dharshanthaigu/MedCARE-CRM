from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List
from sqlalchemy.orm import Session

from app.models.schemas import SubmissionCreatedResponse
from app.services import rag_pipeline
from app.db import get_db
from app.deps import get_current_user_optional

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionCreatedResponse)
async def create_submission(
    files: List[UploadFile] = File(default=[]),
    notes: str = Form(default=""),
    patient_id: str = Form(default=""),
    department: str = Form(default=""),
    db: Session = Depends(get_db),
    user=Depends(get_current_user_optional),
):
    submission_id = rag_pipeline.create_submission(
        db=db,
        files=files,
        notes=notes,
        patient_id=patient_id,
        department=department,
        user_id=user.id if user else None,
    )
    return SubmissionCreatedResponse(submission_id=submission_id)