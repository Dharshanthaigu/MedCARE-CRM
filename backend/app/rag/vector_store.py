"""
STAGE ii - RETRIEVAL (search half)
"""

import re
from typing import List

from sqlalchemy import case, or_
from sqlalchemy.orm import Session

from app.db_models import Chunk

_STOPWORDS = {
    "what", "is", "are", "the", "a", "an", "of", "to", "in", "for", "with",
    "from", "this", "that", "how", "much", "many", "does", "value", "number",
    "mail", "on", "at", "it", "its", "and", "or",
}


def _extract_keywords(query: str) -> List[str]:
    words = re.findall(r"[A-Za-z0-9]+", query)
    return [w for w in words if len(w) > 2 and w.lower() not in _STOPWORDS]


def search(db: Session, submission_id: str, query_embedding: List[float], top_k: int = 5, query_text: str = "") -> List[Chunk]:
    base = db.query(Chunk).filter(Chunk.submission_id == submission_id).filter(Chunk.embedding.isnot(None))

    keywords = _extract_keywords(query_text) if query_text else []
    if not keywords:
        return base.order_by(Chunk.embedding.cosine_distance(query_embedding)).limit(top_k).all()

    match_count = sum(
        case((Chunk.content.ilike(f"%{kw}%"), 1), else_=0) for kw in keywords
    )

    results = (
        base.add_columns(match_count.label("match_count"))
        .order_by(match_count.desc(), Chunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )
    return [row[0] for row in results]
