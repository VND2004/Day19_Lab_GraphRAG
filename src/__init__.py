"""
GraphRAG Lab: Knowledge Graph RAG on Tech Company Corpus

This package implements a complete GraphRAG pipeline including:
- Entity and Relation Extraction from corpus
- Knowledge Graph Construction (NetworkX)
- Graph-based Querying with BFS traversal
- Flat RAG baseline for comparison
- Benchmarking and evaluation

Usage:
    python src/main.py                    # Run full pipeline
    python src/quick_start.py             # Verify setup
    python src/extract_triples.py         # Extract entities/relations
    python src/build_graph.py             # Build knowledge graph
    python src/query_graph.py             # Query using 2-hop traversal
    python src/flat_rag.py                # Flat RAG baseline
    python src/benchmark.py               # Compare results
"""

__version__ = "0.1.0"
__author__ = "GraphRAG Lab"

from .config import get_config, verify_config

__all__ = ["get_config", "verify_config"]
