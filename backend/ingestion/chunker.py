from typing import Dict, List


DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 200


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[str]:
    """
    Split a long text/code file into overlapping chunks.

    Why overlap?
    If a function/class is split between two chunks, overlap helps preserve context.
    """
    if not text or not text.strip():
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks


def chunk_documents(
    documents: List[Dict],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[Dict]:
    """
    Convert loaded repository documents into searchable chunks.

    Each chunk keeps metadata so we know:
    - which file it came from
    - chunk number inside that file
    - file extension/type
    """
    all_chunks = []

    for doc in documents:
        file_chunks = chunk_text(
            doc["content"],
            chunk_size=chunk_size,
            overlap=overlap
        )

        for index, chunk in enumerate(file_chunks):
            all_chunks.append({
                "content": chunk,
                "file_path": doc["file_path"],
                "file_name": doc["file_name"],
                "extension": doc["extension"],
                "chunk_index": index,
                "total_chunks_in_file": len(file_chunks),
                "source_file_size_bytes": doc.get("size_bytes", 0)
            })

    return all_chunks