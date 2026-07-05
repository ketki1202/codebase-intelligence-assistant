from ingestion.github_loader import clone_repo, load_files
from ingestion.chunker import chunk_documents


def main():
    repo_url = "https://github.com/pallets/click"

    print("Cloning repository...")
    repo_path = clone_repo(repo_url)

    print("Loading files...")
    documents = load_files(repo_path)

    print("Chunking documents...")
    chunks = chunk_documents(documents)

    print("\n--- Summary ---")
    print(f"Repository path: {repo_path}")
    print(f"Files loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")

    if chunks:
        first_chunk = chunks[0]

        print("\n--- First Chunk Metadata ---")
        print(f"File path: {first_chunk['file_path']}")
        print(f"File name: {first_chunk['file_name']}")
        print(f"Extension: {first_chunk['extension']}")
        print(f"Chunk index: {first_chunk['chunk_index']}")
        print(f"Total chunks in file: {first_chunk['total_chunks_in_file']}")

        print("\n--- First 500 Characters of First Chunk ---")
        print(first_chunk["content"][:500])

    print("\nDay 2 chunking test completed successfully.")


if __name__ == "__main__":
    main()