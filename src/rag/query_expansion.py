"""Safe Ollama-backed query expansion for hybrid retrieval."""

import json
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    OLLAMA_MODEL,
    OLLAMA_URL,
    QUERY_EXPANSION_COUNT,
    QUERY_EXPANSION_TEMPERATURE,
    QUERY_EXPANSION_TIMEOUT_SECONDS,
)


def _remove_code_fence(value: str) -> str:
    """Remove one optional outer Markdown code fence from a response."""
    match = re.fullmatch(r"\s*```(?:json)?\s*\n?(.*?)\n?```\s*", value, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else value.strip()


def expand_query(query: str) -> list[str]:
    """Return up to QUERY_EXPANSION_COUNT alternative search queries."""
    prompt = (
        "Create 2-3 short search queries for this question. Keep its language.\n"
        'Return JSON only: {"queries":["..."]}\n'
        f"Question: {query}"
    )
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": QUERY_EXPANSION_TEMPERATURE},
            },
            timeout=QUERY_EXPANSION_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        value = json.loads(_remove_code_fence(payload["response"]))
        if not isinstance(value, dict) or not isinstance(value.get("queries"), list):
            return []
    except (requests.RequestException, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return []

    alternatives = []
    seen = {query.strip().casefold()}
    for item in value["queries"]:
        if not isinstance(item, str):
            return []
        item = item.strip()
        normalized = item.casefold()
        if item and normalized not in seen:
            alternatives.append(item)
            seen.add(normalized)
        if len(alternatives) == QUERY_EXPANSION_COUNT:
            break
    return alternatives
