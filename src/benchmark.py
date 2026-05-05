"""
Benchmark and compare GraphRAG vs Flat RAG.
Input: query_results.json, flat_rag_results.json
Output: benchmark_results.csv
"""
import json
import csv
import os
from typing import Dict, List

def load_results(filepath: str) -> List[Dict]:
    """Load query results from JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_results(graph_results: List[Dict], flat_results: List[Dict]) -> List[Dict]:
    """
    Compare GraphRAG and Flat RAG results.
    Returns list of comparison rows.
    """
    comparisons = []
    
    for i, (g_result, f_result) in enumerate(zip(graph_results, flat_results)):
        question = g_result.get("question", "")
        graph_answer = g_result.get("answer", "")
        flat_answer = f_result.get("answer", "")
        num_graph_triples = g_result.get("num_triples", 0)
        num_flat_chunks = f_result.get("num_chunks", 0)
        
        comparisons.append({
            "ID": i + 1,
            "Question": question,
            "GraphRAG Answer": graph_answer[:100],
            "Flat RAG Answer": flat_answer[:100],
            "Graph Triples Used": num_graph_triples,
            "Flat RAG Chunks Used": num_flat_chunks,
            "Method": "2-hop BFS vs Vector Search",
            "Notes": ""
        })
    
    return comparisons

def save_benchmark_csv(comparisons: List[Dict], output_path: str = "outputs/benchmark_results.csv"):
    """Save comparison results to CSV."""
    if not comparisons:
        print("No results to save")
        return
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = list(comparisons[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comparisons)
    
    print(f"Benchmark results saved to {output_path}")

def print_analysis(graph_results: List[Dict], flat_results: List[Dict]):
    """Print analysis of results."""
    print("\n" + "="*60)
    print("BENCHMARK ANALYSIS: GraphRAG vs Flat RAG")
    print("="*60)
    
    print(f"\nNumber of test questions: {len(graph_results)}")
    
    # Statistics
    graph_triples_total = sum(r.get("num_triples", 0) for r in graph_results)
    flat_chunks_total = sum(r.get("num_chunks", 0) for r in flat_results)
    
    print(f"\nGraphRAG Statistics:")
    print(f"  - Average triples per query: {graph_triples_total / len(graph_results):.1f}")
    print(f"  - Total triples used: {graph_triples_total}")
    print(f"  - Method: 2-hop BFS traversal")
    
    print(f"\nFlat RAG Statistics:")
    print(f"  - Average chunks per query: {flat_chunks_total / len(flat_results):.1f}")
    print(f"  - Total chunks used: {flat_chunks_total}")
    print(f"  - Method: Vector similarity search")
    
    print(f"\nExpected Advantages of GraphRAG:")
    print(f"  ✓ Better for multi-hop questions (relations between entities)")
    print(f"  ✓ More structured retrieval (entity-relation graph)")
    print(f"  ✓ Better interpretability (can trace reasoning path)")
    print(f"  ✓ Less hallucination (constrained to graph structure)")
    
    print(f"\nExpected Advantages of Flat RAG:")
    print(f"  ✓ Faster setup (no extraction + graph building)")
    print(f"  ✓ Better for fact lookup (direct semantic match)")
    print(f"  ✓ Less preprocessing required")
    
    print("\n" + "="*60)

def main():
    # Check if results files exist
    graph_results_path = "outputs/query_results.json"
    flat_results_path = "outputs/flat_rag_results.json"
    
    if not os.path.exists(graph_results_path):
        print(f"Error: {graph_results_path} not found. Run query_graph.py first.")
        return
    
    if not os.path.exists(flat_results_path):
        print(f"Error: {flat_results_path} not found. Run flat_rag.py first.")
        return
    
    # Load results
    print("Loading results...")
    graph_results = load_results(graph_results_path)
    flat_results = load_results(flat_results_path)
    
    print(f"Loaded {len(graph_results)} GraphRAG results")
    print(f"Loaded {len(flat_results)} Flat RAG results")
    
    # Compare
    print("\nComparing results...")
    comparisons = compare_results(graph_results, flat_results)
    
    # Save CSV
    os.makedirs("outputs", exist_ok=True)
    save_benchmark_csv(comparisons)
    
    # Print analysis
    print_analysis(graph_results, flat_results)
    
    # Print sample results
    print("\nSample Comparison (First 3 questions):")
    print("-" * 60)
    for comp in comparisons[:3]:
        print(f"\nID: {comp['ID']}")
        print(f"Q: {comp['Question']}")
        print(f"GraphRAG: {comp['GraphRAG Answer']}")
        print(f"Flat RAG: {comp['Flat RAG Answer']}")
        print(f"Data points: Graph={comp['Graph Triples Used']} triples, Flat={comp['Flat RAG Chunks Used']} chunks")

if __name__ == "__main__":
    main()
