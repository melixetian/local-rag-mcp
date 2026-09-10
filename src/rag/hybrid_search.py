"""Testable retrieval helpers for the hybrid FAISS/BM25 search pipeline."""

import re
import sys
from pathlib import Path

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import RRF_K, TOP_K

_TOKEN_PATTERN = re.compile(r"[\w]+(?:[./:-][\w]+)*", re.UNICODE)
_COMPONENT_PATTERN = re.compile(r"[./:-]")


def tokenize(text: str) -> list[str]:
    """Return normalized lexical tokens while retaining useful path-like terms."""
    tokens = []
    for token in _TOKEN_PATTERN.findall(text.casefold()):
        tokens.append(token)
        if _COMPONENT_PATTERN.search(token):
            tokens.extend(component for component in _COMPONENT_PATTERN.split(token) if component)
    return tokens


def build_bm25(chunks: list[dict]) -> tuple[BM25Okapi, list[list[str]]]:
    """Build an in-memory BM25 index and retain its tokenized chunk corpus."""
    chunk_tokens = [tokenize(chunk["text"]) for chunk in chunks]
    return BM25Okapi(chunk_tokens), chunk_tokens


def vector_search(
    index, embedding_model, search_queries: list[str], candidate_count: int, chunk_count: int
) -> list[int]:
    """Return unique chunk positions ranked by their best FAISS score."""
    if not search_queries or not chunk_count:
        return []
    embeddings = np.asarray(embedding_model.encode(search_queries))
    faiss.normalize_L2(embeddings)
    scores, ids = index.search(embeddings, candidate_count)
    best_scores = {}
    for query_scores, query_ids in zip(scores, ids):
        for score, chunk_id in zip(query_scores, query_ids):
            chunk_id = int(chunk_id)
            if 0 <= chunk_id < chunk_count:
                best_scores[chunk_id] = max(best_scores.get(chunk_id, float("-inf")), float(score))
    return [
        position for position, _ in sorted(best_scores.items(), key=lambda item: (-item[1], item[0]))[:candidate_count]
    ]


def bm25_search(bm25, chunk_tokens: list[list[str]], search_queries: list[str], candidate_count: int) -> list[int]:
    """Return chunk positions ranked by their best BM25 score across queries."""
    if not search_queries or not chunk_tokens:
        return []
    query_tokens = [tokenize(query) for query in search_queries]
    matching_tokens = set().union(*map(set, query_tokens)) if query_tokens else set()
    eligible = {position for position, tokens in enumerate(chunk_tokens) if matching_tokens.intersection(tokens)}
    if not eligible:
        return []

    best_scores = {position: float("-inf") for position in eligible}
    for tokens in query_tokens:
        for position, score in enumerate(bm25.get_scores(tokens)):
            if position in eligible:
                best_scores[position] = max(best_scores[position], float(score))
    return [
        position for position, _ in sorted(best_scores.items(), key=lambda item: (-item[1], item[0]))[:candidate_count]
    ]


def reciprocal_rank_fusion(result_lists: list[list[int]], rrf_k: int = RRF_K, top_k: int = TOP_K) -> list[int]:
    """Fuse ranked chunk-position lists using one-based reciprocal ranks."""
    scores = {}
    best_ranks = {}
    for results in result_lists:
        seen_in_list = set()
        for rank, position in enumerate(results, start=1):
            if position in seen_in_list:
                continue
            seen_in_list.add(position)
            scores[position] = scores.get(position, 0.0) + 1.0 / (rrf_k + rank)
            best_ranks[position] = min(best_ranks.get(position, rank), rank)
    return [
        position
        for position, _ in sorted(scores.items(), key=lambda item: (-item[1], best_ranks[item[0]], item[0]))[:top_k]
    ]
