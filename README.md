# Day 19 Lab: GraphRAG with Tech Company Corpus (NVIDIA API)

Hệ thống **GraphRAG** xây dựng đồ thị tri thức từ corpus công ty công nghệ và trả lời câu hỏi multi-hop bằng cách truy vấn đồ thị, sử dụng **NVIDIA API** cho LLM, so sánh với Flat RAG baseline.

## Cấu trúc thư mục

```
Day19_Lab_GraphRAG/
├── README.md
├── SPEC.md
├── QUICKSTART.md
├── requirements.txt
├── .gitignore
├── .env (create this file with API credentials)
│
├── data/
│   └── corpus.json              # Input corpus (JSON format)
│
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuration (NVIDIA API keys)
│   ├── quick_start.py           # Setup verification
│   ├── main.py                  # Full pipeline runner
│   ├── extract_triples.py       # Step 1: Extract entities/relations
│   ├── build_graph.py           # Step 2: Build knowledge graph
│   ├── query_graph.py           # Step 3: Query graph (GraphRAG)
│   ├── flat_rag.py              # Step 4: Flat RAG baseline
│   └── benchmark.py             # Step 5: Benchmark & compare
│
├── outputs/
│   ├── entities.json
│   ├── relationships.json
│   ├── graph.json
│   ├── graph.png
│   ├── query_results.json
│   ├── flat_rag_results.json
│   └── benchmark_results.csv
│
└── report/
    └── report.md                # Report template
```

## Setup

### 1. Cài đặt dependencies
```bash
cd d:\Git\Day19_Lab_GraphRAG
pip install -r requirements.txt
```

### 2. Setup NVIDIA API credentials

Tạo file `.env` trong project root:
```
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1/
AGENT_MODEL=openai/gpt-oss-20b
```

Hoặc set environment variables:

**Windows PowerShell:**
```powershell
$env:NVIDIA_API_KEY="your_key"
$env:NVIDIA_BASE_URL="https://integrate.api.nvidia.com/v1/"
$env:AGENT_MODEL="openai/gpt-oss-20b"
```

**macOS/Linux:**
```bash
export NVIDIA_API_KEY="your_key"
export NVIDIA_BASE_URL="https://integrate.api.nvidia.com/v1/"
export AGENT_MODEL="openai/gpt-oss-20b"
```

### 3. Chuẩn bị corpus

File `data/corpus.json` đã được chuẩn bị. Định dạng:
```json
[
  {
    "id": 1,
    "source": "Wikipedia",
    "title": "OpenAI",
    "url": "https://...",
    "content": "Long text about company..."
  },
  ...
]
```

## Chạy pipeline

```bash
# Kiểm tra setup
python src/quick_start.py

# Chạy full pipeline
python src/main.py

# Hoặc chạy từng bước
python src/extract_triples.py
python src/build_graph.py
python src/query_graph.py
python src/flat_rag.py
python src/benchmark.py
```

## Output

- `outputs/entities.json` — Danh sách entities
- `outputs/relationships.json` — Danh sách relationships
- `outputs/graph.json` — Đồ thị tri thức (JSON)
- `outputs/graph.png` — Biểu đồ đồ thị (PNG)
- `outputs/query_results.json` — Kết quả GraphRAG
- `outputs/flat_rag_results.json` — Kết quả Flat RAG
- `outputs/benchmark_results.csv` — So sánh 2 phương pháp
- `report/report.md` — Báo cáo phân tích

## API sử dụng

- **LLM**: NVIDIA API (OpenAI-compatible interface)
- **Model**: openai/gpt-oss-20b (hoặc model khác)
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Vector Store**: ChromaDB
- **Graph**: NetworkX

## Lưu ý

- Sử dụng NVIDIA API thay vì OpenAI
- Corpus được đọc từ `data/corpus.json` (JSON format)
- Cần set NVIDIA_API_KEY, NVIDIA_BASE_URL, AGENT_MODEL trong .env
- Xem QUICKSTART.md để hướng dẫn chi tiết