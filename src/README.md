# Company Knowledge Base Assistant

An intelligent Q&A system that answers questions about company documentation using RAG (Retrieval-Augmented Generation) and MCP (Model Context Protocol) tools.

## Features

- **Hybrid RAG search**: Query expansion, parallel FAISS semantic search and BM25 full-text search, fused with RRF
- **MCP tools**: Dynamic document reading and management
- **Local LLM**: Privacy-preserving answers using Ollama

## Setup

The dependency list includes `rank-bm25>=0.2.2` for the in-memory full-text retrieval branch.

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Documents

Create a `docs/` directory and add your company documentation files (`.txt`, `.md`, `.pdf`, `.docx`):

```bash
mkdir docs
# Add your company documentation files here
```

### 3. Configure

Edit `config.py` to set:
- `DOCUMENTS_DIR`: Path to your documentation directory
- `OLLAMA_MODEL`: Local LLM model to use (default: "llama3")
- `TOP_K`: Number of final chunks returned after fusion (default: `5`)
- `SEARCH_CANDIDATE_K`: Candidates from each retrieval branch before fusion (default: `10`)
- `RRF_K`: Reciprocal Rank Fusion constant (default: `60`)
- `QUERY_EXPANSION_COUNT`, `QUERY_EXPANSION_TEMPERATURE`, and `QUERY_EXPANSION_TIMEOUT_SECONDS`
- Other settings as needed

### 4. Build Index (Optional)

The index will be built automatically on first use. To manually build it:

```bash
python main.py build-index
```

Or directly:

```bash
python -m rag.build_index
```

Building or rebuilding the existing FAISS index also refreshes the in-memory BM25 index from `chunks.pkl`; BM25 has no separate on-disk artifact.

### Run Unit Tests

```bash
python -m unittest discover -s tests
```

## Usage

### Interactive CLI

Run the interactive assistant:

```bash
python main.py
```

Then ask questions about your company documentation!

## Project Structure

```
src/
├── config.py              # Configuration
├── main.py                # CLI entry point
├── assistant.py           # Main assistant class
├── rag/                   # RAG components
│   ├── ingest.py         # Document ingestion
│   ├── chunk.py          # Text chunking
│   ├── embed.py          # Embedding generation
│   ├── build_index.py    # FAISS index building
│   └── query.py          # Query and retrieval
├── mcp/                   # MCP components
│   ├── server.py         # MCP server with tools
│   └── client.py         # MCP client
├── requirements.txt      # Dependencies
└── README.md             # This file
```

## How It Works

1. **Document Ingestion**: Loads documents from the `docs/` directory
2. **Chunking**: Splits documents into smaller chunks with overlap
3. **Embedding**: Generates embeddings using SentenceTransformers
4. **Indexing**: Builds FAISS vector index for fast similarity search
5. **Query**:
   - Expands the original question with Ollama (with a safe original-query fallback)
   - Searches FAISS and BM25 in parallel, then fuses their ranked chunks with Reciprocal Rank Fusion
   - Optionally uses MCP tools for document access
   - Generates answer using local LLM (Ollama)

## MCP Tools

The MCP server provides:
- `read_document`: Read a specific document
- `list_documents`: List all available documents
- `search_documents`: Search documents by name

## Troubleshooting

**Index not found**: Run `python main.py build-index` first

**Ollama not responding**: Make sure Ollama is running and the model is installed:
```bash
ollama pull llama3
```

**No documents found**: Check that `DOCUMENTS_DIR` in `config.py` points to your documents

## License

MIT
