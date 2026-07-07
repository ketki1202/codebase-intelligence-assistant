from typing import Dict, List


def _clean_snippet(text: str, max_chars: int = 700) -> str:
    """
    Clean a retrieved chunk and shorten it for display.
    """
    text = text.strip()
    text = " ".join(text.split())

    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "..."

    return text


def _extract_sources(search_results: Dict) -> List[str]:
    """
    Extract unique source file paths from ChromaDB search results.
    """
    sources = []

    for metadata in search_results["metadatas"][0]:
        file_path = metadata["file_path"]
        if file_path not in sources:
            sources.append(file_path)

    return sources


def generate_answer(question: str, search_results: Dict) -> Dict:
    """
    Generate a source-aware answer from retrieved chunks.

    This is a free local fallback generator:
    - does not require OpenAI API quota
    - summarizes retrieved evidence in a structured way
    - cites source files
    """
    documents = search_results["documents"][0]
    metadatas = search_results["metadatas"][0]
    distances = search_results["distances"][0]

    sources = _extract_sources(search_results)
    evidence_blocks = []

    for index, document in enumerate(documents):
        metadata = metadatas[index]
        distance = distances[index]

        evidence_blocks.append({
            "rank": index + 1,
            "file_path": metadata["file_path"],
            "file_name": metadata["file_name"],
            "chunk_index": metadata["chunk_index"],
            "distance": round(distance, 4),
            "snippet": _clean_snippet(document)
        })

    answer_lines = [
        f"Question: {question}",
        "",
        "Based on the retrieved codebase context, the most relevant information appears in these source files:",
        ""
    ]

    for block in evidence_blocks[:3]:
        answer_lines.append(
            f"- {block['file_path']} "
            f"(chunk {block['chunk_index']}, relevance distance {block['distance']})"
        )

    answer_lines.extend([
        "",
        "Relevant context summary:",
        ""
    ])

    for block in evidence_blocks[:3]:
        answer_lines.append(f"Source: {block['file_path']}")
        answer_lines.append(f"Snippet: {block['snippet']}")
        answer_lines.append("")

    answer_lines.append(
        "Note: This answer is generated from retrieved source chunks. "
        "For production use, this can be upgraded with an LLM generation layer."
    )

    return {
        "answer": "\n".join(answer_lines),
        "sources": sources,
        "evidence": evidence_blocks,
        "num_sources": len(sources)
    }
