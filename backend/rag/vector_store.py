import hashlib
from typing import Dict, List

import chromadb
from chromadb.utils import embedding_functions


class CodebaseVectorStore:
    """
    Handles storing and searching code chunks using ChromaDB + local embeddings.
    No OpenAI API key is required for embeddings.
    """

    def __init__(self, collection_name: str = "codebase"):
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(path="chroma_db")

        # Free local embedding model.
        # First run may download the model, then it will be cached locally.
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )

    def reset(self) -> None:
        """
        Delete and recreate the collection.
        Useful when indexing a new repository.
        """
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )

    def _make_chunk_id(self, chunk: Dict) -> str:
        """
        Create stable unique ID for each chunk.
        """
        raw_id = (
            f"{chunk['file_path']}::"
            f"{chunk['chunk_index']}::"
            f"{chunk['content'][:80]}"
        )
        return hashlib.md5(raw_id.encode("utf-8")).hexdigest()

    def add_chunks(self, chunks: List[Dict], batch_size: int = 50) -> int:
        """
        Add chunks to ChromaDB in batches.
        """
        total_added = 0

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]

            ids = [self._make_chunk_id(chunk) for chunk in batch]
            documents = [chunk["content"] for chunk in batch]
            metadatas = [
                {
                    "file_path": chunk["file_path"],
                    "file_name": chunk["file_name"],
                    "extension": chunk["extension"],
                    "chunk_index": chunk["chunk_index"],
                    "total_chunks_in_file": chunk["total_chunks_in_file"]
                }
                for chunk in batch
            ]

            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

            total_added += len(batch)
            print(f"Added {total_added}/{len(chunks)} chunks...")

        return total_added

    def search(self, query: str, n_results: int = 5) -> Dict:
        """
        Search ChromaDB for chunks most relevant to the query.
        """
        return self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

    def count(self) -> int:
        """
        Return number of stored chunks.
        """
        return self.collection.count()
