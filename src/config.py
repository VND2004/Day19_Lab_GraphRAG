"""
Configuration and constants for GraphRAG pipeline.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
REPORT_DIR = PROJECT_ROOT / "report"
SRC_DIR = PROJECT_ROOT / "src"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

# Files
CORPUS_FILE = DATA_DIR / "tech_company_corpus.txt"
ENTITIES_FILE = OUTPUT_DIR / "entities.json"
RELATIONSHIPS_FILE = OUTPUT_DIR / "relationships.json"
GRAPH_FILE = OUTPUT_DIR / "graph.json"
GRAPH_IMAGE_FILE = OUTPUT_DIR / "graph.png"
QUERY_RESULTS_FILE = OUTPUT_DIR / "query_results.json"
FLAT_RAG_RESULTS_FILE = OUTPUT_DIR / "flat_rag_results.json"
BENCHMARK_RESULTS_FILE = OUTPUT_DIR / "benchmark_results.csv"

# Model and API settings (NVIDIA API)
LLM_MODEL = os.getenv("AGENT_MODEL", "openai/gpt-oss-20b")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence-Transformers model
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1/")

# Graph settings
MAX_HOPS = 2  # Maximum hops for BFS traversal
TOP_K_CHUNKS = 5  # Top-k chunks to retrieve for Flat RAG
TOP_K_NODES = 5  # Top-k nodes to consider for GraphRAG

# Entity and relation types
ENTITY_TYPES = {
    "Company", "Person", "Product", "Organization", "Location", "Time"
}

RELATION_TYPES = {
    "FOUNDED_BY",
    "FOUNDED_IN",
    "CEO_OF",
    "OWNED_BY",
    "SUBSIDIARY_OF",
    "INVESTED_IN",
    "PARTNERED_WITH",
    "DEVELOPED",
    "USES",
    "LOCATED_IN",
}

# Deduplication aliases
ALIASES = {
    "Alphabet Inc.": "Alphabet",
    "Google LLC": "Google",
    "Open AI": "OpenAI",
    "Sam Altmann": "Sam Altman",
    "Microsoft Corp": "Microsoft",
    "Meta Platforms": "Meta",
    "NVIDIA Corp": "NVIDIA",
}

# Batch processing
BATCH_SIZE = 10  # Process N chunks at a time

# Verbosity
VERBOSE = True
DEBUG = False

def get_config() -> dict:
    """Return all configuration as a dictionary."""
    return {
        "llm_model": LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "max_hops": MAX_HOPS,
        "top_k_chunks": TOP_K_CHUNKS,
        "top_k_nodes": TOP_K_NODES,
        "entity_types": ENTITY_TYPES,
        "relation_types": RELATION_TYPES,
    }

def verify_config() -> bool:
    """Verify configuration is valid."""
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not set")
        return False
    
    if not CORPUS_FILE.exists():
        print(f"Error: Corpus file not found at {CORPUS_FILE}")
        return False
    
    return True
