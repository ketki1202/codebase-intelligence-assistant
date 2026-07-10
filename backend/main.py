import json
import os
import time
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion.github_loader import clone_repo, load_files
from ingestion.chunker import chunk_documents
from rag.vector_store import CodebaseVectorStore
from rag.generator import generate_answer


app = FastAPI(title="Codebase Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATS_FILE = "index_stats.json"

DEFAULT_STATS = {
    "repo_url": None,
    "files_processed": 0,
    "chunks_created": 0,
    "chunks_indexed": 0,
    "index_ready": False,
}


def load_stats() -> dict:
    """
    Load persisted indexing stats from disk.
    """
    if not os.path.exists(STATS_FILE):
        return DEFAULT_STATS.copy()

    try:
        with open(STATS_FILE, "r", encoding="utf-8") as file:
            stats = json.load(file)

        return {
            **DEFAULT_STATS,
            **stats
        }
    except Exception:
        return DEFAULT_STATS.copy()


def save_stats(stats: dict) -> None:
    """
    Save indexing stats to disk.
    """
    with open(STATS_FILE, "w", encoding="utf-8") as file:
        json.dump(stats, file, indent=2)


vector_store = CodebaseVectorStore()
CURRENT_STATS = load_stats()


class IngestRequest(BaseModel):
    repo_url: str
    max_chunks: Optional[int] = None


class QueryRequest(BaseModel):
    question: str
    n_results: int = 5


@app.get("/")
def root():
    return {
        "message": "Codebase Intelligence API is running.",
        "docs": "Visit /docs for interactive API documentation.",
        "endpoints": ["/health", "/ingest", "/query", "/stats"]
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Codebase Intelligence API"
    }


@app.post("/ingest")
def ingest_repository(request: IngestRequest):
    """
    Clone a GitHub repository, load files, chunk them, and index chunks in ChromaDB.
    """
    global CURRENT_STATS

    try:
        start_time = time.time()

        print(f"Cloning repository: {request.repo_url}")
        repo_path = clone_repo(request.repo_url)

        print("Loading files...")
        documents = load_files(repo_path)

        print("Chunking documents...")
        chunks = chunk_documents(documents)

        chunks_to_index = chunks
        if request.max_chunks is not None:
            chunks_to_index = chunks[:request.max_chunks]

        print("Resetting vector store...")
        vector_store.reset()

        print("Indexing chunks...")
        indexed_count = vector_store.add_chunks(chunks_to_index)

        latency_ms = round((time.time() - start_time) * 1000)

        CURRENT_STATS = {
            "repo_url": request.repo_url,
            "files_processed": len(documents),
            "chunks_created": len(chunks),
            "chunks_indexed": indexed_count,
            "index_ready": True,
        }

        save_stats(CURRENT_STATS)

        return {
            "status": "success",
            "repo_url": request.repo_url,
            "files_processed": len(documents),
            "chunks_created": len(chunks),
            "chunks_indexed": indexed_count,
            "latency_ms": latency_ms,
            "message": "Repository indexed successfully."
        }

    except Exception as error:
        CURRENT_STATS["index_ready"] = False
        save_stats(CURRENT_STATS)
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/query")
def query_codebase(request: QueryRequest):
    """
    Search indexed code chunks and generate a source-aware answer.
    """
    try:
        if vector_store.count() == 0:
            raise HTTPException(
                status_code=400,
                detail="No repository has been indexed yet. Please call /ingest first."
            )

        start_time = time.time()

        search_results = vector_store.search(
            query=request.question,
            n_results=request.n_results
        )

        response = generate_answer(
            question=request.question,
            search_results=search_results
        )

        latency_ms = round((time.time() - start_time) * 1000)

        response["latency_ms"] = latency_ms
        response["retrieved_chunks"] = len(search_results["documents"][0])

        return response

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/stats")
def stats():
    """
    Return current indexing stats.
    """
    vector_count = vector_store.count()

    return {
        **CURRENT_STATS,
        "index_ready": CURRENT_STATS["index_ready"] or vector_count > 0,
        "vector_store_count": vector_count
    }
