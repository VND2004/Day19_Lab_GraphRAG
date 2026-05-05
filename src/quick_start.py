"""
Quick start guide and sanity check.
Run this first to verify setup and understand pipeline.
"""
import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def check_environment():
    """Check if required packages are installed."""
    print("Checking environment...")
    
    required_packages = [
        "networkx",
        "matplotlib",
        "chromadb",
        "sentence_transformers",
        "openai"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_api_key():
    """Check if NVIDIA API credentials are set."""
    print("\nChecking NVIDIA API credentials...")
    
    api_key = os.getenv("NVIDIA_API_KEY")
    api_url = os.getenv("NVIDIA_BASE_URL")
    agent_model = os.getenv("AGENT_MODEL")
    
    if api_key:
        print(f"  ✓ NVIDIA_API_KEY is set (first 10 chars: {api_key[:10]}...)")
    else:
        print("  ✗ NVIDIA_API_KEY not found")
        return False
    
    if api_url:
        print(f"  ✓ NVIDIA_BASE_URL is set ({api_url})")
    else:
        print("  ✗ NVIDIA_BASE_URL not found (will use default)")
    
    if agent_model:
        print(f"  ✓ AGENT_MODEL is set ({agent_model})")
    else:
        print("  ✗ AGENT_MODEL not found (will use default)")
    
    return True if api_key else False

def check_data_files():
    """Check if required data files exist."""
    print("\nChecking data files...")
    
    files_to_check = [
        "data/corpus.json",
    ]
    
    all_exist = True
    for filepath in files_to_check:
        if os.path.exists(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  ✓ {filepath} ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ {filepath} (not found)")
            all_exist = False
    
    return all_exist

def print_pipeline_overview():
    """Print overview of the pipeline."""
    print("\n" + "="*60)
    print("GRAPHRAG PIPELINE OVERVIEW")
    print("="*60)
    
    pipeline_steps = [
        ("1. Extract", "extract_triples.py", 
         "- Uses LLM to extract entities and relationships from corpus\n"
         "- Outputs: entities.json, relationships.json"),
        
        ("2. Build Graph", "build_graph.py",
         "- Builds NetworkX graph with deduplication\n"
         "- Visualizes with Matplotlib\n"
         "- Outputs: graph.json, graph.png"),
        
        ("3. Query Graph", "query_graph.py",
         "- Implements 2-hop BFS traversal\n"
         "- Collects supporting triples\n"
         "- Uses LLM to synthesize answers\n"
         "- Outputs: query_results.json"),
        
        ("4. Flat RAG", "flat_rag.py",
         "- Vector search baseline using ChromaDB\n"
         "- Retrieves top-k chunks\n"
         "- Uses LLM to synthesize answers\n"
         "- Outputs: flat_rag_results.json"),
        
        ("5. Benchmark", "benchmark.py",
         "- Compares GraphRAG vs Flat RAG\n"
         "- Generates CSV with results\n"
         "- Outputs: benchmark_results.csv"),
    ]
    
    for step_name, script, details in pipeline_steps:
        print(f"\n{step_name}: {script}")
        for line in details.split("\n"):
            print(f"  {line}")
    
    print("\n" + "="*60)

def main():
    print("\n" + "*"*60)
    print("GRAPHRAG QUICK START")
    print("*"*60)
    
    # Checks
    env_ok = check_environment()
    api_ok = check_api_key()
    data_ok = check_data_files()
    
    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    print(f"Environment: {'✓ OK' if env_ok else '✗ FAILED'}")
    print(f"API Key: {'✓ OK' if api_ok else '✗ FAILED'}")
    print(f"Data Files: {'✓ OK' if data_ok else '✗ FAILED'}")
    
    if not (env_ok and api_ok and data_ok):
        print("\nPlease fix the issues above before proceeding.")
        return False
    
    print("\n✓ All checks passed! Ready to run pipeline.")
    
    # Pipeline overview
    print_pipeline_overview()
    
    # Next steps
    print("\nNEXT STEPS:")
    print("1. Run full pipeline:")
    print("   python src/main.py")
    print("\n2. Or run individual steps:")
    print("   python src/extract_triples.py")
    print("   python src/build_graph.py")
    print("   python src/query_graph.py")
    print("   python src/flat_rag.py")
    print("   python src/benchmark.py")
    print("\n3. Check outputs/ directory for results")
    print("\n" + "*"*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
