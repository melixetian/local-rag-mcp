import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.hybrid_search import bm25_search, build_bm25, reciprocal_rank_fusion
from rag.query import _run_retrieval_branches, retrieve
from rag.query_expansion import expand_query


class QueryExpansionTests(unittest.TestCase):
    def _response(self, content):
        response = Mock()
        response.json.return_value = {"response": content}
        response.raise_for_status.return_value = None
        return response

    @patch("rag.query_expansion.requests.post")
    def test_valid_json_fence_deduplication_and_limit(self, post):
        post.return_value = self._response(
            '```json\n{"queries": ["One", " one ", "Original", "Two", "Three", "Four"]}\n```'
        )
        self.assertEqual(expand_query("Original"), ["One", "Two", "Three"])

    @patch("rag.query_expansion.requests.post")
    def test_invalid_or_failed_expansion_returns_empty_list(self, post):
        for content in ["not json", "[]", '{"queries": "not a list"}', '{"queries": []}']:
            post.return_value = self._response(content)
            self.assertEqual(expand_query("original"), [])
        post.side_effect = __import__("requests").Timeout()
        self.assertEqual(expand_query("original"), [])
        post.side_effect = __import__("requests").HTTPError()
        self.assertEqual(expand_query("original"), [])


class HybridSearchTests(unittest.TestCase):
    def setUp(self):
        self.chunks = [
            {"text": "General deployment documentation", "source": "a", "chunk_id": 0},
            {"text": "Run docker-compose up to start the service", "source": "b", "chunk_id": 1},
            {"text": "Edit config.py before deploying", "source": "c", "chunk_id": 2},
        ]
        self.bm25, self.chunk_tokens = build_bm25(self.chunks)

    def test_bm25_ranks_filename_and_aggregates_multiple_queries(self):
        self.assertEqual(bm25_search(self.bm25, self.chunk_tokens, ["config.py"], 3)[0], 2)
        results = bm25_search(self.bm25, self.chunk_tokens, ["config.py", "docker-compose"], 3)
        self.assertEqual(set(results[:2]), {1, 2})

    def test_rrf_deduplicates_orders_deterministically_and_limits(self):
        self.assertEqual(reciprocal_rank_fusion([[2, 1, 2], [1, 3]], rrf_k=60, top_k=2), [1, 2])
        self.assertEqual(reciprocal_rank_fusion([[4], [3]], rrf_k=60, top_k=5), [3, 4])

    def test_branch_failure_preserves_other_branch(self):
        def fails():
            raise RuntimeError("unavailable")

        self.assertEqual(_run_retrieval_branches(lambda: [1, 2], fails), [[1, 2], []])
        self.assertEqual(_run_retrieval_branches(fails, lambda: [3]), [[], [3]])

    @patch("rag.query.bm25_search")
    @patch("rag.query.vector_search")
    @patch("rag.query._get_model", return_value=object())
    @patch("rag.query.expand_query", return_value=[])
    def test_retrieve_keeps_original_query_when_expansion_has_no_results(self, expand, get_model, vector, bm25):
        import rag.query as query_module

        old_state = (query_module.index, query_module.chunks, query_module.bm25_index, query_module.chunk_tokens)
        query_module.index = object()
        query_module.chunks = self.chunks
        query_module.bm25_index = object()
        query_module.chunk_tokens = self.chunk_tokens
        vector.return_value = [2]
        bm25.return_value = [1]
        try:
            retrieved = retrieve("Where is config?")
        finally:
            query_module.index, query_module.chunks, query_module.bm25_index, query_module.chunk_tokens = old_state

        self.assertEqual(expand.call_args.args[0], "Where is config?")
        self.assertEqual(vector.call_args.args[2], ["Where is config?"])
        self.assertEqual(bm25.call_args.args[2], ["Where is config?"])
        self.assertEqual({chunk["chunk_id"] for chunk in retrieved}, {1, 2})


if __name__ == "__main__":
    unittest.main()
