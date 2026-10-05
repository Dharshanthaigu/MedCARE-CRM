"""
Runs Stage i (parsing) and the embedding half of Stage ii for one
submission: every uploaded document + the free-text notes get parsed,
chunked, embedded, and written to the `chunks` table.
"""

import time
from typing import Tuple

from sqlalchemy.orm import Session

from app.db_models import Submission, Document, Chunk
from app.rag.parsers import parse_document
from app.rag.chunker import chunk_text, chunk_document
from app.rag.embeddings import get_embedder


def run_parse_and_ocr(db: Session, submission: Submission) -> float:
    confidences = []
    for doc in submission.documents:
        text = parse_document(doc.storage_path, doc.file_type)
        doc._extracted_text = text
        if doc.file_type == "image":
            confidences.append(60.0 if text.startswith("[") else 95.0)
    return round(sum(confidences) / len(confidences), 1) if confidences else 100.0


def run_chunk_and_embed(db: Session, submission: Submission) -> int:
    embedder = get_embedder()
    all_texts = []
    all_meta = []

    for doc in submission.documents:
        text = getattr(doc, "_extracted_text", None) or parse_document(doc.storage_path, doc.file_type)
        pieces = chunk_document(text)
        for i, piece in enumerate(pieces):
            all_texts.append(piece)
            all_meta.append((doc.id, i))

    if submission.notes and submission.notes.strip():
        pieces = chunk_text(submission.notes)
        for i, piece in enumerate(pieces):
            all_texts.append(piece)
            all_meta.append((None, i))

    if not all_texts:
        return 0

    vectors = embedder.embed(all_texts)

    for text, (doc_id, idx), vector in zip(all_texts, all_meta, vectors):
        db.add(Chunk(
            submission_id=submission.id,
            document_id=doc_id,
            content=text,
            embedding=vector,
            chunk_index=idx,
        ))
    db.commit()
    return len(all_texts)


async def run_llm_ready_check(db: Session, submission: Submission) -> int:
    from app.rag.vector_store import search
    from app.rag.embeddings import get_embedder
    from app.rag.prompt_builder import build_sources, build_prompt
    from app.rag.llm_client import get_llm_client

    start = time.perf_counter()

    embedder = get_embedder()
    query = "What is this submission about?"
    query_vec = embedder.embed([query])[0]

    chunks = search(db, submission.id, query_vec, top_k=3)
    documents_by_id = {d.id: d for d in submission.documents}
    sources = build_sources(chunks, documents_by_id)
    prompt = build_prompt(query, sources)

    llm = get_llm_client(sources=sources)
    await llm.generate(prompt)

    elapsed_ms = round((time.perf_counter() - start) * 1000)
    return elapsed_ms