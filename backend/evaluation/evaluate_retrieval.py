import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_DIR))

from rag.vector_store import CodebaseVectorStore


EVAL_QUESTIONS = [
    "Where is the command line interface defined?",
    "How are commands and groups created?",
    "How are options passed to a command?",
    "How does Click handle command line arguments?",
]


def main():
    vector_store = CodebaseVectorStore()

    if vector_store.count() == 0:
        print("No indexed chunks found. Run /ingest or test_api.py first.")
        return

    print(f"Indexed chunks available: {vector_store.count()}")

    for question in EVAL_QUESTIONS:
        print("\n" + "=" * 80)
        print(f"Question: {question}")

        results = vector_store.search(question, n_results=5)

        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        print("Top retrieved sources:")

        for index, metadata in enumerate(metadatas):
            print(
                f"{index + 1}. {metadata['file_path']} "
                f"(chunk {metadata['chunk_index']}, distance {round(distances[index], 4)})"
            )

    print("\nRetrieval evaluation completed.")


if __name__ == "__main__":
    main()
