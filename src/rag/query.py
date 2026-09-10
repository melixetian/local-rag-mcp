import pickle
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import faiss
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CHUNKS_PATH, EMBEDDING_MODEL, FAISS_INDEX_PATH, SEARCH_CANDIDATE_K, TOP_K
from rag.hybrid_search import bm25_search, build_bm25, reciprocal_rank_fusion, vector_search
from rag.query_expansion import expand_query

# Initialized on first retrieval, so importing this module has no model download or index build.
model = None
index = None
chunks = []
bm25_index = None
chunk_tokens = []


def _initialize_bm25():
    global bm25_index, chunk_tokens
    bm25_index, chunk_tokens = build_bm25(chunks)


def _get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(EMBEDDING_MODEL)
    return model


def _load_index_and_chunks(index_path, chunks_path):
    global index, chunks
    index = faiss.read_index(str(index_path))
    with open(chunks_path, "rb") as file:
        chunks = pickle.load(file)
    _initialize_bm25()


def _ensure_index_exists():
    """Ensure FAISS, chunks, and their in-memory BM25 index are available."""
    src_dir = Path(__file__).parent.parent
    index_path = src_dir / FAISS_INDEX_PATH
    chunks_path = src_dir / CHUNKS_PATH

    if index_path.exists() and chunks_path.exists():
        try:
            _load_index_and_chunks(index_path, chunks_path)
            return True
        except Exception as error:
            print(f"⚠️  Warning: Error loading existing index: {error}")
            print("Rebuilding index...")

    print("📦 Index not found. Building index from documents...")
    try:
        from rag.build_index import build_index

        build_index()
        if index_path.exists() and chunks_path.exists():
            _load_index_and_chunks(index_path, chunks_path)
            print("✅ Index built and loaded successfully")
            return True

        print("❌ Failed to build index. No documents found or error occurred.")
        from config import DOCUMENTS_DIR

        print(f"   Check that documents exist in: {src_dir / DOCUMENTS_DIR}")
        return False
    except Exception as error:
        print(f"❌ Error building index: {error}")
        return False


def _run_retrieval_branches(vector_branch, bm25_branch):
    """Run both branches concurrently and retain either successful result."""
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = (("FAISS", executor.submit(vector_branch)), ("BM25", executor.submit(bm25_branch)))
        for name, future in futures:
            try:
                results.append(future.result())
            except Exception as error:
                print(f"⚠️  Warning: {name} retrieval failed: {error}")
                results.append([])
    return results


def retrieve(query: str, verbose: bool = False):
    """Retrieve up to TOP_K chunks through expanded hybrid search and RRF."""
    if index is None or not chunks or bm25_index is None:
        if not _ensure_index_exists():
            return []
    if index is None or not chunks or bm25_index is None:
        return []

    alternatives = expand_query(query)
    search_queries = [query, *alternatives]
    candidate_count = max(TOP_K, SEARCH_CANDIDATE_K)
    if verbose:
        print(f"🔎 Search queries: {len(search_queries)}")

    branch_results = _run_retrieval_branches(
        lambda: vector_search(index, _get_model(), search_queries, candidate_count, len(chunks)),
        lambda: bm25_search(bm25_index, chunk_tokens, search_queries, candidate_count),
    )
    if verbose:
        print(f"   FAISS candidates: {len(branch_results[0])}; BM25 candidates: {len(branch_results[1])}")

    positions = reciprocal_rank_fusion(branch_results, top_k=TOP_K)
    return [chunks[position] for position in positions]


def build_prompt(query, contexts):
    """Build prompt with retrieved context."""
    if not contexts:
        return f"""
<role>You are a helpful assistant that answers questions about company information.</role>
<instructions>Answer the question based on your general knowledge. If you don't know, say so.</instructions>

<query>
{query}
</query>

<assistant>
"""

    context_text = "\n\n".join(f"[Source: {context['source']}]\n{context['text']}" for context in contexts)
    context_instructions = (
        "Answer the question ONLY based on the context provided below. "
        "If the answer is not in the context, say "
        '"I don\'t have that information in the knowledge base."'
    )
    return f"""
<role>You are a helpful assistant that answers questions about company information.</role>
<instructions>{context_instructions}</instructions>

<context>
{context_text}
</context>

<query>
{query}
</query>

<assistant>
"""


def ask_llm(prompt):
    """Query Ollama LLM."""
    from config import OLLAMA_MODEL, OLLAMA_URL

    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
    )
    return response.json()["response"]


def ask(query: str):
    """Answer a question using RAG."""
    contexts = retrieve(query)
    prompt = build_prompt(query, contexts)
    return ask_llm(prompt), contexts


if __name__ == "__main__":
    while True:
        question = input("\n❓ Question: ")
        if question.lower() in {"exit", "quit"}:
            break
        print("\n🤖 Answer:\n")
        answer, sources = ask(question)
        print(answer)
        if sources:
            print("\n📚 Sources:")
            for source in sources:
                print(f"  - {source['source']}")
