import os
import shutil
from pathlib import Path
from typing import Dict, List

import git


SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".java", ".cpp", ".c", ".h",
    ".go", ".rs",
    ".md", ".txt", ".json", ".yaml", ".yml"
}

EXCLUDED_DIRS = {
    ".git", "node_modules", "venv", ".venv",
    "__pycache__", "dist", "build", ".next",
    ".pytest_cache", ".mypy_cache"
}

MAX_FILE_SIZE_BYTES = 200_000


def safe_repo_name(repo_url: str) -> str:
    """
    Extract a clean local folder name from a GitHub repo URL.
    Example:
    https://github.com/pallets/flask.git -> flask
    """
    repo_name = repo_url.rstrip("/").split("/")[-1]

    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    return repo_name.replace(" ", "_")


def clone_repo(repo_url: str, base_dir: str = "repos") -> str:
    """
    Clone a public GitHub repository into the local repos/ directory.
    If the repo already exists locally, delete and re-clone it for a clean index.
    """
    os.makedirs(base_dir, exist_ok=True)

    repo_name = safe_repo_name(repo_url)
    local_path = os.path.join(base_dir, repo_name)

    if os.path.exists(local_path):
        shutil.rmtree(local_path)

    git.Repo.clone_from(
        repo_url,
        local_path,
        multi_options=["--depth=1"]
    )

    return local_path


def should_skip_path(path: Path) -> bool:
    """
    Return True if the file is inside folders we do not want to index.
    """
    return any(part in EXCLUDED_DIRS for part in path.parts)


def load_files(repo_path: str) -> List[Dict]:
    """
    Load supported source/documentation files from a cloned repository.

    Returns a list of dictionaries:
    {
        content,
        file_path,
        file_name,
        extension,
        size_bytes
    }
    """
    documents = []
    root = Path(repo_path)

    for file_path in root.rglob("*"):
        if file_path.is_dir():
            continue

        if should_skip_path(file_path):
            continue

        if file_path.suffix not in SUPPORTED_EXTENSIONS:
            continue

        if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as error:
            print(f"Skipping unreadable file {file_path}: {error}")
            continue

        if not content.strip():
            continue

        documents.append({
            "content": content,
            "file_path": str(file_path.relative_to(root)),
            "file_name": file_path.name,
            "extension": file_path.suffix,
            "size_bytes": file_path.stat().st_size
        })

    return documents