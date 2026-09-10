# Hybrid Retrieval for `local-rag-mcp`

## 1. Objective

Improve retrieval quality in the existing [`MobilaName/local-rag-mcp`](https://github.com/MobilaName/local-rag-mcp) project by adding:

1. LLM-based query expansion;
2. BM25 full-text retrieval running in parallel with FAISS retrieval;
3. Reciprocal Rank Fusion (RRF);
4. safe fallback when query expansion or one retrieval branch fails.

This specification targets repository commit `a6583d4e25f6f94eef96f1829ac4f72b9981c021` (2026-02-18).

## 2. Existing behavior to preserve

- Python 3.10+ and the current CLI remain supported.
- Documents are loaded from `DOCUMENTS_DIR`, split into the existing chunk dictionaries, and persisted in `chunks.pkl`.
- FAISS remains the vector index and `SentenceTransformer` remains the embedding provider.
- Ollama remains the only LLM provider.
- `retrieve(query)` continues to return a list of existing chunk dictionaries with `text`, `source`, and `chunk_id` fields.
- `CompanyKBAssistant.query()` keeps its current response structure and MCP decision/tool flow.
- The final answer is generated from the original user question and the fused contexts. Expanded queries must never replace the original question in the answer prompt.

## 3. Required configuration

Add the following settings to `src/config.py`:

```python
SEARCH_CANDIDATE_K = 10
RRF_K = 60
QUERY_EXPANSION_COUNT = 3
QUERY_EXPANSION_TEMPERATURE = 0.0
QUERY_EXPANSION_TIMEOUT_SECONDS = 30
```

- Existing `TOP_K` is the number of chunks returned after fusion.
- Each retrieval branch returns at most `max(TOP_K, SEARCH_CANDIDATE_K)` candidates before fusion.
- Add `rank-bm25>=0.2.2` to `src/requirements.txt`.

## 4. Query expansion

Create `src/rag/query_expansion.py` with a public function:

```python
def expand_query(query: str) -> list[str]:
    """Return up to QUERY_EXPANSION_COUNT alternative search queries."""
```

### LLM request

- Make exactly one request to the existing Ollama `/api/generate` endpoint before retrieval.
- Use `OLLAMA_MODEL`, `QUERY_EXPANSION_TEMPERATURE`, and `QUERY_EXPANSION_TIMEOUT_SECONDS` from configuration.
- Set `stream` to `false` and pass the temperature through Ollama's `options` object.
- Use this compact prompt, substituting the original question verbatim:

```text
Create 2-3 short search queries for this question. Keep its language.
Return JSON only: {"queries":["..."]}
Question: <user question>
```

### Response parsing

1. Read the `response` string from Ollama's JSON response.
2. Trim whitespace and optionally remove one surrounding Markdown code fence, including an optional `json` language marker.
3. Parse the remaining text with `json.loads`.
4. Accept only an object whose `queries` value is a list of strings.
5. Strip every item, discard empty values, deduplicate case-insensitively, discard values equal to the original question, preserve order, and keep at most `QUERY_EXPANSION_COUNT` items.

If the HTTP request fails or times out, the response is not valid JSON, its shape is invalid, or no valid alternatives remain, return an empty list. Do not propagate the expansion error.

The search-query list is always:

```python
[original_query, *expand_query(original_query)]
```

Therefore the original query is used even when expansion fails.

## 5. BM25 index and retrieval helpers

Create `src/rag/hybrid_search.py`. It must contain independently testable helpers for tokenization, BM25 construction/search, vector search, and RRF.

### Tokenization

- Normalize text with `casefold()`.
- Extract Unicode word/number tokens.
- Preserve common internal filename and command separators (`.`, `/`, `:`, `-`) so values such as `config.py`, `docker-compose`, and paths remain searchable as single tokens.
- Compound values may additionally emit their word components (for example, `config.py`, `config`, and `py`) so both exact and partial lexical queries can match.
- Return no empty tokens.
- Use the same tokenizer for chunks and queries.

### BM25 lifecycle

- Use `rank_bm25.BM25Okapi` over the text of every loaded chunk, in the same order as `chunks`.
- Build the BM25 object once after `chunks.pkl` is loaded, including after an automatic FAISS rebuild. Do not rebuild it for every query.
- The BM25 index is in memory and does not need a separate persisted artifact. Rebuilding the existing index/chunk cache must be sufficient to refresh both retrieval methods.

### Branch result format

Both retrieval branches return an ordered list of integer positions in the shared `chunks` list. That position is the canonical identity used for deduplication and fusion.

### Vector branch

- Accept the full search-query list.
- Encode all queries in one batch and L2-normalize the embeddings.
- Run FAISS search for every query.
- Ignore invalid FAISS IDs such as `-1` and IDs outside `chunks`.
- If a chunk occurs for multiple queries, retain its maximum cosine/IP score.
- Sort by retained score descending, using chunk position ascending as the deterministic tie-breaker, then return the configured candidate count.

### BM25 branch

- Score every search query against the BM25 index.
- For each chunk, retain the maximum BM25 score across all search queries.
- Only consider chunks that share at least one normalized token with at least one search query. Do not filter solely on `score > 0`, because BM25 scores can be zero or negative on very small corpora.
- Sort by retained score descending, using chunk position ascending as the deterministic tie-breaker, then return the configured candidate count.

## 6. Parallel hybrid retrieval

Update `src/rag/query.py` so `retrieve(query)` performs this pipeline:

1. Ensure FAISS, chunks, and BM25 are initialized.
2. Generate alternative queries and prepend the original query.
3. Submit the vector and BM25 branches concurrently using one `ThreadPoolExecutor(max_workers=2)`.
4. Wait for both futures.
5. Fuse the two ranked lists with RRF.
6. Map the fused chunk positions back to chunk dictionaries and return at most `TOP_K` chunks.

Only the two retrieval branches need to run in parallel. Query expansion intentionally completes first because both branches consume its output.

If one branch raises an exception, emit a concise warning and fuse the result from the other branch. If both branches fail or return no candidates, return an empty list. A branch failure must not terminate the CLI.

Keep branch execution/fallback in a helper that accepts callable retrieval branches, or otherwise make the orchestration dependency-injectable. This allows its concurrency and failure behavior to be unit-tested without loading a real embedding model or index.

The implementation may add `verbose: bool = False` to `retrieve` if useful, provided existing calls remain valid. In verbose mode it may show the accepted expanded queries and the candidate count from each branch, but it must not print full chunk contents or raw prompts.

## 7. Reciprocal Rank Fusion

Implement rank-based fusion; do not combine raw FAISS and BM25 scores because their scales are not comparable.

For every chunk position `d`:

```text
RRF(d) = sum(1 / (RRF_K + rank(d, result_list)))
```

- Ranks are one-based.
- A missing chunk contributes zero for that result list.
- A chunk present in both lists appears only once in the output.
- Sort by RRF score descending.
- Resolve equal RRF scores by best rank in either input list, then by chunk position ascending.
- Return no more than `TOP_K` positions.

## 8. Tests

Add unit tests under `src/tests/`. Tests must not require a running Ollama server, model downloads, a built FAISS index, or real documents. Use mocks or small in-memory inputs.

At minimum cover:

1. valid query-expansion JSON, optional code fences, deduplication, and result limit;
2. malformed JSON, invalid response shape, empty output, HTTP error, and timeout fallback;
3. BM25 ranking of an exact rare term, filename, or command;
4. aggregation of results from multiple search queries;
5. RRF calculation, deduplication, deterministic ordering, and `TOP_K` limit;
6. graceful degradation when either retrieval branch fails;
7. preservation of the original query when expansion returns no alternatives.

Prefer the standard `unittest` and `unittest.mock` modules so no additional test dependency is required.

## 9. Documentation

Update `src/README.md` and the root `README.md` where relevant:

- describe the new pipeline: query expansion → parallel FAISS/BM25 → RRF → final answer;
- list the new dependency and configuration settings;
- state that BM25 is rebuilt in memory from `chunks.pkl`;
- retain current setup, index-building, CLI, and MCP instructions;
- include the exact command the user can run to execute the unit tests.

Do not claim benchmark improvements without measured results.

## 10. Optional benchmark (not part of this implementation)

The repository contains no document corpus or labeled relevance queries, so a meaningful before/after benchmark cannot be produced from the current source alone. A later benchmark should compare vector-only and hybrid retrieval on the same labeled queries using at least Hit Rate@K or Recall@K, MRR@K, and retrieval latency. Do not add synthetic benchmark results in this iteration.

## 11. Out of scope

- Replacing FAISS, SentenceTransformers, Ollama, or MCP.
- Adding a reranker, database, web UI, API, containerization, or external service.
- Changing chunking or document ingestion behavior.
- Changing MCP tools or the LLM's MCP decision logic.
- Persisting BM25 to disk.
- Unrelated cleanup or refactoring.

## 12. Acceptance criteria

The implementation is complete when all of the following are true:

- One safe LLM expansion step occurs before retrieval.
- The original query plus up to three valid alternatives are used by both branches.
- FAISS and BM25 retrieval are submitted concurrently.
- RRF with one-based ranks and `RRF_K = 60` produces at most `TOP_K` unique chunks.
- Expansion failure falls back to the original query without failing the request.
- Failure of one retrieval branch still allows the other branch to produce contexts.
- Existing CLI, answer generation, source reporting, and MCP behavior remain compatible.
- Focused unit tests and documentation are added.
- No unrelated features or infrastructure are introduced.
