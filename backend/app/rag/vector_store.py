"""
STAGE ii — RETRIEVAL (search half)
"""

from typing import List

from sqlalchemy.orm import Session

from app.db_models import Chunk


def search(db: Session, submission_id: str, query_embedding: List[float], top_k: int = 5) -> List[Chunk]:
    return (
        db.query(Chunk)
        .filter(Chunk.submission_id == submission_id)
        .filter(Chunk.embedding.isnot(None))
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )