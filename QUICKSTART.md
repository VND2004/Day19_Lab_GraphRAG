# GraphRAG Lab - Setup & Execution Guide

## Project Structure

```
Day19_Lab_GraphRAG/
├── README.md                      # General overview
├── SPEC.md                        # Lab specification
├── QUICKSTART.md                  # This file
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
│
├── data/
│   └── tech_company_corpus.txt    # Input corpus (pre-filled with sample data)
│
├── src/
│   ├── __init__.py
│   ├── config.py                  # Configuration & constants
│   ├── quick_start.py             # Setup verification
│   ├── main.py                    # Full pipeline runner
│   ├── extract_triples.py         # Step 1: Extract entities/relations
│   ├── build_graph.py             # Step 2: Build knowledge graph
│   ├── query_graph.py             # Step 3: Query graph (GraphRAG)
│   ├── flat_rag.py                # Step 4: Flat RAG baseline
│   └── benchmark.py               # Step 5: Benchmark & compare
│
├── outputs/                       # Generated output files
│   ├── entities.json
│   ├── relationships.json
│   ├── graph.json
│   ├── graph.png
│   ├── query_results.json
│   ├── flat_rag_results.json
│   └── benchmark_results.csv
│
└── report/
    └── report.md                  # Report template (fill in manually)
```

---

## Installation

### Prerequisites
- Python 3.10+
- OpenAI API key (https://platform.openai.com/api-keys)

### Step 1: Install Python Dependencies

```bash
cd d:\Git\Day19_Lab_GraphRAG
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed networkx matplotlib neo4j openai pandas ...
```

### Step 2: Set OpenAI API Key

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-proj-your-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-proj-your-key-here
```

**macOS/Linux (Bash):**
```bash
export OPENAI_API_KEY="sk-proj-your-key-here"
```

**To verify API key is set:**
```powershell
echo $env:OPENAI_API_KEY
```

### Step 3: Verify Setup

```bash
python src/quick_start.py
```

Expected checks:
```
Environment: ✓ OK
API Key: ✓ OK
Data Files: ✓ OK
```

---

## Running the Pipeline

### Option 1: Run Full Pipeline (Recommended for first-time)

```bash
python src/main.py
```

This will execute all 5 steps in sequence:
1. Extract entities & relations
2. Build knowledge graph
3. Query using GraphRAG
4. Flat RAG baseline
5. Benchmark comparison

**Execution time:** ~2-5 minutes (depending on corpus size and API latency)

### Option 2: Run Individual Steps

If you want to debug or run specific steps:

```bash
# Step 1: Extract entities and relations
python src/extract_triples.py

# Step 2: Build knowledge graph
python src/build_graph.py

# Step 3: Query the graph (GraphRAG)
python src/query_graph.py

# Step 4: Run Flat RAG baseline
python src/flat_rag.py

# Step 5: Benchmark and compare
python src/benchmark.py
```

---

## Understanding the Output

### After `extract_triples.py`:
- `outputs/entities.json` - List of extracted entities with types
- `outputs/relationships.json` - List of extracted relations (triples)

**Example:**
```json
{
  "entities": [
    {"name": "OpenAI", "type": "Company", "chunk_id": "chunk_000"}
  ],
  "relationships": [
    {
      "subject": "OpenAI",
      "predicate": "FOUNDED_BY",
      "object": "Sam Altman",
      "evidence": "OpenAI was founded by Sam Altman...",
      "chunk_id": "chunk_000"
    }
  ]
}
```

### After `build_graph.py`:
- `outputs/graph.json` - Knowledge graph in JSON format (nodes + edges)
- `outputs/graph.png` - Visual representation of the graph

**Graph statistics printed:**
```
Graph contains 25 nodes and 35 edges
Entity types: {'Company': 10, 'Person': 12, 'Product': 3}
Relation types: {'FOUNDED_BY': 8, 'INVESTED_IN': 6, ...}
```

### After `query_graph.py`:
- `outputs/query_results.json` - GraphRAG results for test questions

**Example:**
```json
{
  "question": "Microsoft có mối quan hệ nào với OpenAI?",
  "answer": "Microsoft invested in OpenAI and integrated OpenAI models into Azure.",
  "supporting_triples": [
    ["Microsoft", "INVESTED_IN", "OpenAI"],
    ["OpenAI", "USES", "Azure"]
  ],
  "extraction_method": "graph_2hop"
}
```

### After `flat_rag.py`:
- `outputs/flat_rag_results.json` - Flat RAG results for same questions

### After `benchmark.py`:
- `outputs/benchmark_results.csv` - Side-by-side comparison

**View results:**
```bash
cat outputs/benchmark_results.csv
```

---

## Customizing the Pipeline

### Change Input Corpus

Replace `data/tech_company_corpus.txt` with your own corpus:
```
One sentence about companies.
Another sentence with entities and relationships.
...
```

**Note:** Each sentence should be a complete statement for better extraction.

### Modify Test Questions

Edit the `test_questions` list in `src/query_graph.py` or `src/flat_rag.py`:

```python
test_questions = [
    "Your question 1?",
    "Your question 2?",
    # ...
]
```

### Adjust Graph Parameters

Edit `src/config.py`:

```python
MAX_HOPS = 2                    # BFS depth (1 or 2)
TOP_K_CHUNKS = 5                # Top-k for Flat RAG
BATCH_SIZE = 10                 # Process N chunks at a time
```

### Use Different LLM

Edit `src/config.py`:
```python
LLM_MODEL = "gpt-4"  # or "gpt-3.5-turbo"
```

---

## Troubleshooting

### Error 1: `OPENAI_API_KEY not set`
**Solution:** Set the API key using the commands in "Step 2" above.

### Error 2: `ModuleNotFoundError: No module named 'openai'`
**Solution:** Run `pip install -r requirements.txt`

### Error 3: `API Rate Limit Exceeded`
**Solution:** Wait a few minutes and retry. Or use `gpt-3.5-turbo` instead of `gpt-4`.

### Error 4: `File not found: data/tech_company_corpus.txt`
**Solution:** The corpus file is pre-filled. If deleted, re-create it with sample sentences.

### Error 5: `graph.png too large / memory error`
**Solution:** Reduce corpus size or increase `MAX_HOPS` to 1 (smaller graph).

---

## Next Steps After Running

1. **Review the Knowledge Graph:**
   - Open `outputs/graph.png` to visualize entities and relationships
   - Check the graph statistics in console output

2. **Compare Results:**
   - Open `outputs/benchmark_results.csv` with Excel/Sheets
   - Compare GraphRAG vs Flat RAG answers

3. **Write the Report:**
   - Use `report/report.md` as a template
   - Fill in sections with your analysis
   - Add screenshots of the knowledge graph

4. **Optional: Deeper Analysis**
   - Modify test questions to explore edge cases
   - Try different corpus sizes
   - Implement entity linking improvements

---

## Pipeline Internals

### Entity Extraction Prompt
The LLM is prompted to extract:
- Entities: Companies, People, Products, Organizations, Locations, Times
- Relations: FOUNDED_BY, INVESTED_IN, CEO_OF, DEVELOPED, etc.

### Deduplication Strategy
- Normalize whitespace and aliases
- Merge nodes with same normalized name
- Preserve original names in metadata
- Track multiple mentions per entity

### Graph Traversal (BFS)
For each entity in the question:
1. Find matching node in graph
2. Explore all neighbors (1-hop)
3. For each 1-hop neighbor, explore their neighbors (2-hop)
4. Collect all connecting edges (relations)
5. Convert to natural language

### Flat RAG Baseline
1. Embed corpus chunks with Sentence Transformers
2. Store in ChromaDB with embeddings
3. For each query, retrieve top-5 most similar chunks
4. Send chunks + question to LLM for synthesis

---

## Performance Expectations

| Component | Time |
|-----------|------|
| Extract (30 sentences) | ~30-60s |
| Build Graph | ~5s |
| Query Graph (5 questions) | ~15-30s |
| Flat RAG (5 questions) | ~15-30s |
| Benchmark | ~5s |
| **Total** | **~1-3 minutes** |

---

## File Size Expectations

| File | Size |
|------|------|
| entities.json | ~10-50 KB |
| relationships.json | ~20-100 KB |
| graph.json | ~30-150 KB |
| graph.png | ~100-500 KB |
| query_results.json | ~20-50 KB |
| flat_rag_results.json | ~20-50 KB |
| benchmark_results.csv | ~10-30 KB |

---

## Quick Reference Commands

```bash
# Full pipeline
python src/main.py

# Just setup check
python src/quick_start.py

# Extract only
python src/extract_triples.py && python src/build_graph.py

# Query with verbose output
python src/query_graph.py

# View results
cat outputs/benchmark_results.csv
```

---

## What's Next?

1. ✓ Setup & install dependencies
2. ✓ Run pipeline
3. ✓ Review outputs
4. ⚠️ **Write report.md** (manually fill in analysis)
5. ⚠️ **Prepare presentation** (screenshots, insights)

---

## Questions?

Refer to [SPEC.md](../SPEC.md) for detailed specification and learning objectives.
