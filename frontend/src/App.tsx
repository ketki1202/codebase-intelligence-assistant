import { useEffect, useState } from "react";
import "./App.css";

import { getStats, ingestRepository, queryCodebase } from "./api";

import type {
  IngestResponse,
  QueryResponse,
  StatsResponse,
} from "./api";

const exampleQuestions = [
  "Where is the command line interface defined?",
  "How are commands and groups created?",
  "How are options passed to a command?",
  "How does Click handle command line arguments?",
];

function App() {
  const [repoUrl, setRepoUrl] = useState<string>(
    "https://github.com/pallets/click"
  );
  const [maxChunks, setMaxChunks] = useState<number>(120);
  const [question, setQuestion] = useState<string>(
    "Where is the command line interface defined?"
  );

  const [loading, setLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [ingestResult, setIngestResult] = useState<IngestResponse | null>(null);
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);

  async function refreshStats() {
    try {
      const statsData = await getStats();
      setStats(statsData);
    } catch (error) {
      console.error("Failed to refresh stats:", error);
    }
  }

  useEffect(() => {
    refreshStats();
  }, []);

  async function handleIngest() {
    try {
      setLoading(true);
      setStatusMessage("Indexing repository. This may take a few moments...");
      setQueryResult(null);

      const result = await ingestRepository(repoUrl, maxChunks);
      setIngestResult(result);
      setStatusMessage("Repository indexed successfully.");

      await refreshStats();
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Ingest failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleQuery() {
    try {
      setLoading(true);
      setStatusMessage("Searching indexed codebase...");

      const result = await queryCodebase(question, 5);
      setQueryResult(result);
      setStatusMessage("Query completed.");

      await refreshStats();
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <div className="hero-badge">Full-stack RAG project</div>
        <h1>Codebase Intelligence Assistant</h1>
        <p className="subtitle">
          Ask questions about a public GitHub repository. The app ingests source
          files, chunks them, stores local embeddings in ChromaDB, and returns
          source-aware answers with evidence snippets.
        </p>

        <div className="tech-row">
          <span>FastAPI</span>
          <span>React</span>
          <span>ChromaDB</span>
          <span>Sentence Transformers</span>
          <span>RAG</span>
        </div>
      </section>

      <section className="grid">
        <div className="card">
          <div className="card-header">
            <p className="step">Step 1</p>
            <h2>Ingest Repository</h2>
          </div>

          <label>GitHub repository URL</label>
          <input
            value={repoUrl}
            onChange={(event) => setRepoUrl(event.target.value)}
            placeholder="https://github.com/owner/repo"
          />

          <label>Max chunks for demo</label>
          <input
            type="number"
            value={maxChunks}
            onChange={(event) => setMaxChunks(Number(event.target.value))}
          />

          <button onClick={handleIngest} disabled={loading || !repoUrl}>
            {loading ? "Working..." : "Ingest Repository"}
          </button>

          {ingestResult && (
            <div className="result-box">
              <p>
                <strong>Status:</strong> {ingestResult.status}
              </p>
              <p>
                <strong>Files processed:</strong>{" "}
                {ingestResult.files_processed}
              </p>
              <p>
                <strong>Chunks created:</strong> {ingestResult.chunks_created}
              </p>
              <p>
                <strong>Chunks indexed:</strong> {ingestResult.chunks_indexed}
              </p>
              <p>
                <strong>Latency:</strong> {ingestResult.latency_ms} ms
              </p>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <p className="step">Step 2</p>
            <h2>Query Codebase</h2>
          </div>

          <label>Question</label>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a question about the indexed repository"
          />

          <div className="examples">
            <p>Try an example:</p>
            {exampleQuestions.map((example) => (
              <button
                className="example-button"
                key={example}
                type="button"
                onClick={() => setQuestion(example)}
              >
                {example}
              </button>
            ))}
          </div>

          <button onClick={handleQuery} disabled={loading || !question}>
            {loading ? "Working..." : "Ask Question"}
          </button>

          {statusMessage && <p className="status">{statusMessage}</p>}
        </div>
      </section>

      {stats && (
        <section className="card">
          <div className="card-header">
            <p className="step">Index</p>
            <h2>Repository Stats</h2>
          </div>

          <div className="stats-grid">
            <p>
              <strong>Repo:</strong> {stats.repo_url || "None"}
            </p>
            <p>
              <strong>Files:</strong> {stats.files_processed}
            </p>
            <p>
              <strong>Chunks created:</strong> {stats.chunks_created}
            </p>
            <p>
              <strong>Chunks indexed:</strong> {stats.chunks_indexed}
            </p>
            <p>
              <strong>Vector count:</strong> {stats.vector_store_count}
            </p>
            <p>
              <strong>Ready:</strong> {stats.index_ready ? "Yes" : "No"}
            </p>
          </div>
        </section>
      )}

      {queryResult && (
        <section className="card answer-card">
          <div className="card-header">
            <p className="step">Result</p>
            <h2>Source-aware Answer</h2>
          </div>

          <div className="metrics-row">
            <span>{queryResult.retrieved_chunks} chunks retrieved</span>
            <span>{queryResult.num_sources} source files</span>
            <span>{queryResult.latency_ms} ms latency</span>
          </div>

          <pre>{queryResult.answer}</pre>

          <h3>Sources</h3>
          <ul className="source-list">
            {queryResult.sources.map((source: string) => (
              <li key={source}>{source}</li>
            ))}
          </ul>

          <h3>Evidence</h3>
          {queryResult.evidence.map((item) => (
            <div
              className="evidence"
              key={`${item.file_path}-${item.chunk_index}`}
            >
              <p>
                <strong>
                  {item.rank}. {item.file_path}
                </strong>{" "}
                <span>
                  chunk {item.chunk_index}, distance {item.distance}
                </span>
              </p>
              <p>{item.snippet}</p>
            </div>
          ))}
        </section>
      )}

      <footer>
        Built with FastAPI, React, ChromaDB, and local embeddings.
      </footer>
    </main>
  );
}

export default App;
