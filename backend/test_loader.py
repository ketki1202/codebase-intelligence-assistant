from ingestion.github_loader import clone_repo, load_files


def main():
    repo_url = "https://github.com/pallets/click"

    repo_path = clone_repo(repo_url)
    documents = load_files(repo_path)

    print(f"Repository cloned to: {repo_path}")
    print(f"Files loaded: {len(documents)}")

    if documents:
        first_doc = documents[0]
        print("\nFirst file metadata:")
        print(f"File path: {first_doc['file_path']}")
        print(f"File name: {first_doc['file_name']}")
        print(f"Extension: {first_doc['extension']}")
        print(f"Size: {first_doc['size_bytes']} bytes")

        print("\nFirst 400 characters:")
        print(first_doc["content"][:400])


if __name__ == "__main__":
    main()