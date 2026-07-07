from ingestion.github_loader import clone_repo, load_files
from ingestion.chunker import chunk_documents
from rag.vector_store import CodebaseVectorStore
from rag.generator import generate_answer


def main():
    repo_url = "https://github.com/pallets/click"
    question = "Where is the command line interface defined?"

    print("Cloning repository...")
    repo_path = clone_repo(repo_url)

    print("Loading files...")
    documents = load_files(repo_path)

    print("Chunking documents...")
    chunks = chunk_documents(documents)

    # Limit chunks for testing so the test stays fast.
    test_chunks = chunks[:120]

    print(f"Files loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Chunks used for test: {len(test_chunks)}")

    print("\nInitializing vector store...")
    vector_store = CodebaseVectorStore()

    print("Resetting collection...")
    vector_store.reset()

    print("Adding chunks...")
    vector_store.add_chunks(test_chunks)

    print(f"\nSearching question: {question}")
    search_results = vector_store.search(question, n_results=5)

    print("\nGenerating source-aware answer...")
    response = generate_answer(question, search_results)

    print("\n--- Generated Answer ---")
    print(response["answer"])

    print("\n--- Sources ---")
    for source in response["sources"]:
        print(source)

    print("\nDay 4 RAG answer generation test completed successfully.")


if __name__ == "__main__":
    main()
