"""
Main pipeline: extract -> build graph -> query -> benchmark
Run this to execute the full GraphRAG pipeline.
"""
import sys
import os
import subprocess


def get_start_step() -> int:
    """Determine which pipeline step to start from."""
    if os.getenv("START_STEP"):
        try:
            return max(1, int(os.getenv("START_STEP", "1")))
        except ValueError:
            return 1

    if os.getenv("SKIP_STEP_1", "0") == "1":
        return 2

    return 1

def run_step(script_name: str, description: str):
    """Run a Python script and catch errors."""
    print("\n" + "="*60)
    print(f"STEP: {description}")
    print("="*60)
    
    try:
        # Get project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(project_root, "src", script_name)
        
        # Run from project root to ensure relative paths work
        result = subprocess.run([sys.executable, script_path], cwd=project_root, capture_output=False)
        if result.returncode != 0:
            print(f"Error running {script_name}")
            return False
        return True
    except Exception as e:
        print(f"Exception in {script_name}: {e}")
        return False

def main():
    print("\n" + "*"*60)
    print("GraphRAG PIPELINE - FULL EXECUTION")
    print("*"*60)
    
    steps = [
        ("extract_triples.py", "1. Extract Entities & Relations from Corpus"),
        ("build_graph.py", "2. Build Knowledge Graph"),
        ("query_graph.py", "3. Query Graph (GraphRAG)"),
        ("flat_rag.py", "4. Flat RAG Baseline"),
        ("benchmark.py", "5. Compare & Benchmark Results"),
    ]

    start_step = get_start_step()
    if start_step > 1:
        print(f"Starting from step {start_step}; skipping earlier steps.")

    steps = steps[start_step - 1 :]
    
    success_count = 0
    for script, description in steps:
        if run_step(script, description):
            success_count += 1
        else:
            print(f"Warning: {description} failed, continuing...")
    
    print("\n" + "*"*60)
    print(f"PIPELINE COMPLETE: {success_count}/{len(steps)} steps succeeded")
    print("*"*60)
    
    print("\nOutput files generated:")
    print("  - outputs/entities.json")
    print("  - outputs/relationships.json")
    print("  - outputs/graph.json")
    print("  - outputs/graph.png")
    print("  - outputs/query_results.json")
    print("  - outputs/flat_rag_results.json")
    print("  - outputs/benchmark_results.csv")
    
    print("\nNext steps:")
    print("  1. Review outputs/graph.png to visualize the knowledge graph")
    print("  2. Check outputs/benchmark_results.csv for comparison")
    print("  3. Write final report in report/report.md")

if __name__ == "__main__":
    main()
