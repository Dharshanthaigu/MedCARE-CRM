import re
from typing import List


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def chunk_document(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    """Table-aware chunking: each '--- Table on page N ---' block becomes its own chunk."""
    text = (text or "").strip()
    if not text:
        return []

    parts = re.split(r'(?=--- Table on page \d+ ---)', text)
    chunks: List[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("--- Table on page"):
            if len(part) <= chunk_size * 3:
                chunks.append(part)
            else:
                chunks.extend(chunk_text(part, chunk_size, overlap))
        else:
            chunks.extend(chunk_text(part, chunk_size, overlap))
    return chunks
