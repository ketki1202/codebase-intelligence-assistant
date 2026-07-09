const API_BASE_URL = "http://127.0.0.1:8000";

export type IngestResponse = {
  status: string;
  repo_url: string;
  files_processed: number;
  chunks_created: number;
  chunks_indexed: number;
  latency_ms: number;
  message: string;
};

export type QueryResponse = {
  answer: string;
  sources: string[];
  evidence: {
    rank: number;
    file_path: string;
    file_name: string;
    chunk_index: number;
    distance: number;
    snippet: string;
  }[];
  num_sources: number;
  latency_ms: number;
  retrieved_chunks: number;
};

export type StatsResponse = {
  repo_url: string | null;
  files_processed: number;
  chunks_created: number;
  chunks_indexed: number;
  index_ready: boolean;
  vector_store_count: number;
};

export async function ingestRepository(
  repoUrl: string,
  maxChunks: number
): Promise<IngestResponse> {
  const response = await fetch(`${API_BASE_URL}/ingest`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      repo_url: repoUrl,
      max_chunks: maxChunks,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to ingest repository");
  }

  return response.json();
}

export async function queryCodebase(
  question: string,
  nResults: number
): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      n_results: nResults,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to query codebase");
  }

  return response.json();
}

export async function getStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/stats`);

  if (!response.ok) {
    throw new Error("Failed to fetch stats");
  }

  return response.json();
}