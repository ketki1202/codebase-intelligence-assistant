from dotenv import load_dotenv

from ingestion.github_loader import clone_repo, load_files
from ingestion.chunker import chunk_documents
from rag.vector_store import CodebaseVectorStore


def print_search_results(results):
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("\n--- Search Results ---")

    for index, metadata in enumerate(metadatas):
        print(f"\nResult {index + 1}")
        print(f"File: {metadata['file_path']}")
        print(f"Chunk: {metadata['chunk_index']}")
        print(f"Distance: {round(distances[index], 4)}")
        print("Preview:")
        print(documents[index][:500])


def main():
    load_dotenv(override=True)

    repo_url = "https://github.com/pallets/click"

    print("Cloning repository...")
    repo_path = clone_repo(repo_url)

    print("Loading files...")
    documents = load_files(repo_path)

    print("Chunking documents...")
    chunks = chunk_documents(documents)

    # Limit chunks for Day 3 testing to avoid unnecessary API cost/time.
    test_chunks = chunks[:120]

    print(f"Files loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Chunks used for this test: {len(test_chunks)}")

    print("\nInitializing vector store...")
    vector_store = CodebaseVectorStore()

    print("Resetting existing ChromaDB collection...")
    vector_store.reset()

    print("Adding chunks to ChromaDB...")
    total_added = vector_store.add_chunks(test_chunks)

    print(f"\nTotal chunks stored: {total_added}")
    print(f"Collection count: {vector_store.count()}")

    query = "Where is the command line interface defined?"
    print(f"\nSearching query: {query}")

    results = vector_store.search(query, n_results=5)
    print_search_results(results)

    print("\nDay 3 vector search test completed successfully.")


if __name__ == "__main__":
    main()
