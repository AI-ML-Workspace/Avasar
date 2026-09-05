from typing import List
from app.models.document import ProcessedChunk, SchemeDocument


def split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> List[str]:
    """Split text deterministically into chunks of approximate size with overlap.

    Prefers splitting along whitespace (spaces or newlines) to avoid cutting words
    in half.

    Args:
        text: Raw text string to split.
        chunk_size: Maximum character length per chunk (must be > 0).
        chunk_overlap: Character overlap between consecutive chunks (must be >= 0 and < chunk_size).

    Returns:
        List of non-empty string chunks.

    Raises:
        ValueError: If chunk_size <= 0, chunk_overlap < 0, or chunk_overlap >= chunk_size.
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
    if chunk_overlap < 0:
        raise ValueError(f"chunk_overlap cannot be negative, got {chunk_overlap}")
    if chunk_overlap >= chunk_size:
        raise ValueError(
            f"chunk_overlap ({chunk_overlap}) must be strictly less than chunk_size ({chunk_size})"
        )

    clean_text = text.replace("\r\n", "\n").strip()
    if not clean_text:
        return []

    # If the text fits inside a single chunk, return immediately
    if len(clean_text) <= chunk_size:
        return [clean_text]

    chunks: List[str] = []
    start = 0
    total_len = len(clean_text)

    while start < total_len:
        end = start + chunk_size

        if end >= total_len:
            final_chunk = clean_text[start:].strip()
            if final_chunk:
                chunks.append(final_chunk)
            break

        # Look for a natural split point (newline or space) within the latter half of the window
        split_at = -1
        # Search backward from end down to the halfway point of the chunk
        min_split_point = start + (chunk_size // 2)

        # 1. Prefer paragraph/line breaks
        newline_idx = clean_text.rfind("\n", min_split_point, end)
        if newline_idx != -1:
            split_at = newline_idx
        else:
            # 2. Prefer space boundaries
            space_idx = clean_text.rfind(" ", min_split_point, end)
            if space_idx != -1:
                split_at = space_idx
            else:
                # 3. No natural delimiter found; force cut at chunk_size
                split_at = end

        chunk_content = clean_text[start:split_at].strip()
        if chunk_content:
            chunks.append(chunk_content)

        # Advance start position taking overlap into account
        next_start = split_at - chunk_overlap
        # Guarantee forward progress
        if next_start <= start:
            next_start = split_at

        # If next_start points to whitespace, skip it
        while next_start < total_len and clean_text[next_start].isspace():
            next_start += 1

        start = next_start

    return chunks


def chunk_document(
    doc: SchemeDocument,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> List[ProcessedChunk]:
    """Chunk a SchemeDocument into ProcessedChunk objects with preserved metadata.

    Args:
        doc: The SchemeDocument to chunk.
        chunk_size: Maximum character length per chunk.
        chunk_overlap: Overlap in characters between consecutive chunks.

    Returns:
        List of ProcessedChunk objects with deterministic IDs and complete metadata.
    """
    raw_chunks = split_text(doc.content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    total_chunks = len(raw_chunks)

    processed: List[ProcessedChunk] = []
    for idx, chunk_text in enumerate(raw_chunks):
        processed.append(
            ProcessedChunk(
                chunk_id=f"{doc.id}#{idx}",
                scheme_id=doc.id,
                title=doc.title,
                url=doc.url,
                source_id=doc.source_id,
                source_name=doc.source_name,
                official_source_url=doc.official_source_url,
                source_type=doc.source_type,
                trust_level=doc.trust_level,
                retrieved_at=doc.retrieved_at,
                published_at=doc.published_at,
                content_hash=doc.content_hash,
                document_type=doc.document_type,
                version=doc.version,
                language=doc.language,
                chunk_index=idx,
                total_chunks=total_chunks,
                text=chunk_text,
                char_length=len(chunk_text),
                metadata=dict(doc.metadata),
            )
        )

    return processed
