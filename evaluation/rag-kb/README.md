# Northstar Labs RAG Test Knowledge Base

This is a fictional knowledge base designed to test hybrid retrieval in `local-rag-mcp`.

## Installation

Copy the seven files from `docs/` into the repository's `src/docs/` directory. Then rebuild the index from `src/`:

```bash
python main.py build-index
```

Start the assistant:

```bash
python main.py
```

Use the questions in `TEST_CASES.md`. The facts, people, systems, commands, identifiers, and policies in this corpus are entirely fictional.

## What the corpus tests

- semantic retrieval from paraphrased questions;
- exact lexical retrieval of policy codes, filenames, paths, and commands;
- query expansion from everyday wording to domain terminology;
- RRF when vector and BM25 retrieval find the same chunk;
- discrimination between documents with overlapping vocabulary;
- refusal when the requested information is absent.

