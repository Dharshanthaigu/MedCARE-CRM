from sqlalchemy.orm import Session

from app.db_models import Submission
from app.models.schemas import QueryResponse, SourceRef
from app.rag.embeddings import get_embedder
from app.rag.vector_store import search
from app.rag.prompt_builder import build_sources, build_prompt
from app.rag.llm_client import get_llm_client


async def answer_query(db: Session, session_id: str, message: str) -> QueryResponse:
    submission = db.query(Submission).filter(Submission.id == session_id).first()
    if not submission:
        return QueryResponse(
            answer="I don't have an indexed submission for this session yet — "
                   "submit documents on the New Submission page first.",
            sources=[],
            tool_calls=[],
        )

    embedder = get_embedder()
    query_vec = embedder.embed([message])[0]

    chunks = search(db, submission.id, query_vec, top_k=5)
    documents_by_id = {d.id: d for d in submission.documents}
    sources = build_sources(chunks, documents_by_id)
    prompt = build_prompt(message, sources)

    llm = get_llm_client(sources=sources)
    answer_text = await llm.generate(prompt)

    return QueryResponse(
        answer=answer_text,
        sources=[
            SourceRef(doc=s.doc_name, location=s.location, snippet=s.snippet)
            for s in sources
        ],
        tool_calls=[f"queried clinical-rag-v3 · {len(chunks)} chunks"] if chunks else [],
    )