\# Codebase Intelligence Assistant



A full-stack RAG application that lets users ask natural-language questions about public GitHub repositories.



The system ingests repository files, chunks source code and documentation, creates local embeddings, stores them in ChromaDB, retrieves relevant chunks for a question, and returns a source-aware answer with evidence snippets.

## Motivation

Developers often spend significant time understanding unfamiliar codebases before contributing, debugging, or reviewing a project. This project explores how retrieval-augmented generation can make codebase exploration faster by connecting natural-language questions to source-grounded evidence.

The goal is not only to generate an answer, but to show where the answer came from through file paths, retrieved chunks, and source snippets.

\## Features



\- Public GitHub repository ingestion

\- Source file loading and filtering

\- Code/document chunking with metadata

\- Local embeddings using Sentence Transformers

\- ChromaDB vector search

\- Source-aware answer generation

\- FastAPI backend with `/ingest`, `/query`, `/stats`, and `/health`

\- React + TypeScript frontend

\- API testing script

\- Basic retrieval evaluation script



\## Tech Stack



\*\*Backend\*\*

\- Python

\- FastAPI

\- ChromaDB

\- Sentence Transformers

\- GitPython

\- pandas-style data workflow patterns



\*\*Frontend\*\*

\- React

\- TypeScript

\- Vite

\- CSS



\## Architecture



```text

GitHub Repository URL

&#x20;       ↓

Repository Cloning

&#x20;       ↓

File Loading and Filtering

&#x20;       ↓

Chunking with Metadata

&#x20;       ↓

Local Embeddings

&#x20;       ↓

ChromaDB Vector Store

&#x20;       ↓

Semantic Retrieval

&#x20;       ↓

Source-aware Answer

&#x20;       ↓

React UI

## What I Learned

- Built an end-to-end RAG workflow from repository ingestion to retrieval and answer generation.
- Used local embeddings to avoid dependency on paid API calls.
- Designed FastAPI endpoints for ingestion, querying, health checks, and indexing stats.
- Connected a React + TypeScript frontend to a Python backend.
- Added retrieval evaluation and API testing scripts to make the project easier to validate.
- Learned the importance of source-aware answers, metadata, and evidence when building AI-assisted developer tools.

## Limitations

- Current chunking is file/text based and can be improved with function-level or class-level parsing.
- The answer generator is source-aware but does not yet use a full LLM generation layer.
- The current version supports public repositories only.
- Large repositories may require batching, progress indicators, and more efficient indexing.
- Retrieval quality depends on chunking strategy, embedding model, and repository structure.


