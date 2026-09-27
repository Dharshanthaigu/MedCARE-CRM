"""
Pipeline runner - REAL Phase 2 work instead of asyncio.sleep.
"""

import asyncio
import os
import shutil

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.db_models import Submission, Document, PipelineRun, Chunk
from app.config import UPLOAD_DIR
from app.rag.ingest import run_parse_and_ocr, run_chunk_and_embed, run_llm_ready_check
from app.rag.parsers import detect_file_type


def create_submission(db: Session, files: list, notes: str, patient_id: str, department: str, user_id: str = None) -> str:
    submission = Submission(
        user_id=user_id,
        patient_id=patient_id,
        department=department,
        notes=notes,
    )
    db.add(submission)
    db.flush()

    submission_dir = os.path.join(UPLOAD_DIR, submission.id)
    os.makedirs(submission_dir, exist_ok=True)

    for f in files:
        dest_path = os.path.join(submission_dir, f.filename)
        with open(dest_path, "wb") as out:
            shutil.copyfileobj(f.file, out)
        size_bytes = os.path.getsize(dest_path)

        db.add(Document(
            submission_id=submission.id,
            filename=f.filename,
            file_type=detect_file_type(f.filename),
            size_bytes=size_bytes,
            storage_path=dest_path,
        ))

    db.add(PipelineRun(submission_id=submission.id, status="pending"))
    db.commit()

    asyncio.create_task(_run_pipeline(submission.id))
    return submission.id


def get_status(db: Session, submission_id: str) -> dict | None:
    run = db.query(PipelineRun).filter(PipelineRun.submission_id == submission_id).first()
    if not run:
        return None
    return {
        "submission_id": submission_id,
        "stages_done": run.stages_done,
        "active_stage": run.active_stage,
        "chunks": run.chunks_count,
        "ocr_confidence": run.ocr_confidence,
        "avg_latency_ms": run.avg_latency_ms,
    }


def rerun(db: Session, submission_id: str) -> dict | None:
    run = db.query(PipelineRun).filter(PipelineRun.submission_id == submission_id).first()
    if not run:
        return None
    db.query(Chunk).filter(Chunk.submission_id == submission_id).delete()
    run.stages_done = 0
    run.active_stage = None
    run.status = "pending"
    db.commit()
    asyncio.create_task(_run_pipeline(submission_id))
    return get_status(db, submission_id)


async def _run_pipeline(submission_id: str):
    db = SessionLocal()
    try:
        run = db.query(PipelineRun).filter(PipelineRun.submission_id == submission_id).first()
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not run or not submission:
            return
        run.status = "running"
        db.commit()

        run.active_stage = 1
        db.commit()
        await asyncio.sleep(0.3)
        run.stages_done = 1
        db.commit()

        run.active_stage = 2
        db.commit()
        ocr_confidence = await asyncio.to_thread(run_parse_and_ocr, db, submission)
        run.ocr_confidence = ocr_confidence
        run.stages_done = 2
        db.commit()

        run.active_stage = 3
        db.commit()
        chunk_count = await asyncio.to_thread(run_chunk_and_embed, db, submission)
        run.chunks_count = chunk_count
        run.stages_done = 3
        db.commit()

        run.active_stage = 4
        db.commit()
        await asyncio.sleep(0.3)
        run.stages_done = 4
        db.commit()

        run.active_stage = 5
        db.commit()
        try:
            latency_ms = await run_llm_ready_check(db, submission)
            run.avg_latency_ms = latency_ms
        except Exception as e:
            run.status = "error"
            db.commit()
            print(f"[pipeline] Stage 5 failed for {submission_id}: {e}")
            return
        run.stages_done = 5

        run.active_stage = None
        run.status = "done"
        db.commit()
    finally:
        db.close()
