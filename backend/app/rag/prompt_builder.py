"""
STAGE iii — AUGMENTATION
"""

from typing import List
from dataclasses import dataclass

from app.db_models import Chunk, Document


@dataclass
class SourceEntry:
    index: int
    doc_name: str
    location: str
    snippet: str      # short preview, used only for the source chips shown in the UI
    full_text: str    # the complete chunk, this is what the LLM actually reads


SYSTEM_PROMPT = (
    "You are MedRAG, a clinical documentation assistant. Answer the user's "
    "question using ONLY the numbered context passages below — do not use "
    "outside medical knowledge to fill gaps. If the passages don't contain "
    "the answer, say so plainly rather than guessing. When you state a "
    "fact from a passage, reference it with its number in brackets, e.g. [1]. "
    "Write in plain text without markdown formatting (no asterisks or bold). "
    "Be concise and clinically precise."
)


def build_sources(chunks: List[Chunk], documents_by_id: dict) -> List[SourceEntry]:
    sources = []
    for i, chunk in enumerate(chunks, start=1):
        doc = documents_by_id.get(chunk.document_id)
        doc_name = doc.filename if doc else "submitted note"
        location = f"page {chunk.page}" if chunk.page else f"chunk {chunk.chunk_index}"
        sources.append(SourceEntry(
            index=i,
            doc_name=doc_name,
            location=location,
            snippet=chunk.content[:220],
            full_text=chunk.content,
        ))
    return sources


def build_prompt(question: str, sources: List[SourceEntry]) -> str:
    if not sources:
        context_block = "(No relevant passages were found in this submission's index.)"
    else:
        context_block = "\n\n".join(
            f"[{s.index}] ({s.doc_name}, {s.location}):\n{s.full_text}" for s in sources
        )

    return (
        f"CONTEXT PASSAGES:\n{context_block}\n\n"
        f"QUESTION: {question}\n\n"
        f"Answer using only the passages above, citing sources like [1] where relevant."
    )
