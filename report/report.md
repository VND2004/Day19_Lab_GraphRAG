# GraphRAG Lab Report

**Name:** [Your Name]  
**Date:** [Date]  
**Course:** Day 19 Lab - Xây dựng hệ thống GraphRAG  

---

## 1. Giới thiệu

### 1.1 GraphRAG là gì?
[Giải thích khái niệm GraphRAG, sự khác biệt với Flat RAG]

### 1.2 Mục tiêu bài lab
[Mô tả các mục tiêu chính của bài lab này]

### 1.3 Tech Company Corpus
[Mô tả corpus được sử dụng: số lượng câu, loại thông tin, ...]

---

## 2. Mô tả Pipeline

### 2.1 Trích xuất Entity và Relation

**Phương pháp:**
- LLM được sử dụng: GPT-3.5-turbo
- Prompt strategy: [Mô tả cách yêu cầu LLM]

**Kết quả:**
- Số lượng entities: [X]
- Số lượng relationships: [Y]

**Ví dụ:**
```json
{
  "entities": [
    {"name": "OpenAI", "type": "Company"},
    {"name": "Sam Altman", "type": "Person"}
  ],
  "relationships": [
    {
      "subject": "OpenAI",
      "predicate": "FOUNDED_BY",
      "object": "Sam Altman",
      "evidence": "OpenAI was founded by Sam Altman..."
    }
  ]
}
```

### 2.2 Chuẩn hóa và Khử trùng lặp

**Phương pháp:**
- Chuẩn hóa khoảng trắng
- Alias mapping
- [Các phương pháp khác]

**Kết quả:**
- Số entities trước deduplication: [X]
- Số entities sau deduplication: [Y]
- Lợi suất deduplication: [Y/X]%

### 2.3 Xây dựng Knowledge Graph

**Công cụ sử dụng:** NetworkX

**Cấu trúc:**
- Node: Thực thể (companies, people, ...)
- Edge: Quan hệ (FOUNDED_BY, INVESTED_IN, ...)
- Node attributes: name, type, mentions
- Edge attributes: relation, evidence, chunk_id

**Thống kê đồ thị:**
- Số nodes: [X]
- Số edges: [Y]
- Loại entities: [list]
- Loại relations: [list]

### 2.4 Truy vấn GraphRAG

**Phương pháp:**
1. Trích xuất entities từ câu hỏi
2. Tìm matching nodes trong graph
3. BFS 2-hop traversal
4. Collect supporting triples
5. Textualize + LLM synthesis

**Ví dụ truy vấn:**
```
Q: "Microsoft có mối quan hệ gì với OpenAI?"
A: "Microsoft invested in OpenAI and integrated OpenAI models into Azure."
Supporting triples: [(Microsoft, INVESTED_IN, OpenAI), ...]
```

### 2.5 Flat RAG Baseline

**Phương pháp:**
- Vector store: ChromaDB
- Embedding model: all-MiniLM-L6-v2
- Retrieval: Top-5 chunks by similarity
- Synthesis: LLM

---

## 3. Kết quả

### 3.1 Đồ thị tri thức

[Đặt ảnh graph.png ở đây]

**Mô tả:** [Giải thích cấu trúc chính, những quan hệ quan trọng]

### 3.2 Benchmark Results

| ID | Câu hỏi | Đáp án đúng | GraphRAG | Flat RAG | Đúng? | Ghi chú |
|----|---------|-----------|----------|----------|-------|---------|
| 1 | Q1 | [Answer] | [Answer] | [Answer] | ✓/✗ | |
| 2 | Q2 | [Answer] | [Answer] | [Answer] | ✓/✗ | |
| ... | ... | ... | ... | ... | ... | ... |

### 3.3 Tính toán sai số (Nếu có ground truth)

- **Accuracy (GraphRAG):** [X]%
- **Accuracy (Flat RAG):** [Y]%
- **Precision/Recall:** [...]

---

## 4. Phân tích so sánh

### 4.1 Ưu điểm của GraphRAG

- [Ưu điểm 1]: Giải thích tại sao GraphRAG tốt hơn trong trường hợp này
- [Ưu điểm 2]: ...

**Ví dụ:**
- Multi-hop reasoning: GraphRAG có thể trả lời "Công ty nào phát triển AI và liên quan đến Microsoft?" bằng cách traverse 2-3 hops
- Traceability: Có thể theo dõi từng bước trong BFS để kiểm chứng kết quả

### 4.2 Ưu điểm của Flat RAG

- [Ưu điểm 1]
- [Ưu điểm 2]

### 4.3 Trường hợp Flat RAG bị ảo giác

[Liệt kê những câu hỏi mà Flat RAG trả lời sai/ảo giác, nhưng GraphRAG đúng]

---

## 5. Chi phí và Performance

| Metric | GraphRAG | Flat RAG | Ghi chú |
|--------|----------|----------|---------|
| Thời gian indexing (s) | X | Y | |
| Token dùng indexing | X | Y | |
| Thời gian truy vấn trung bình (s) | X | Y | |
| Token dùng truy vấn trung bình | X | Y | |
| Tổng chi phí | X | Y | |

---

## 6. Kết luận

### 6.1 Kết quả chính
[Tóm tắt kết quả chính, so sánh giữa hai phương pháp]

### 6.2 Khi nào nên dùng GraphRAG
[Tình huống phù hợp]

### 6.3 Khi nào nên dùng Flat RAG
[Tình huống phù hợp]

### 6.4 Đề xuất cải tiến

1. **Entity Linking:** Dùng NER model chuyên biệt thay vì LLM
2. **Relation Confidence:** Thêm confidence score cho mỗi relation
3. **Knowledge Update:** Cơ chế cập nhật graph khi có dữ liệu mới
4. **Multi-language:** Hỗ trợ tiếng Việt tốt hơn
5. **Visualization:** Neo4j Browser cho trực quan hóa interactively

---

## 7. Tài liệu tham khảo

- [SPEC.md](../SPEC.md) - Specification chi tiết
- NetworkX: https://networkx.org/
- ChromaDB: https://docs.trychroma.com/
- OpenAI API: https://platform.openai.com/docs/

---

## Phụ lục

### A. Danh sách 20 câu hỏi Benchmark

[Liệt kê đầy đủ 20 câu hỏi test, kết quả so sánh]

### B. Cấu trúc dữ liệu

[Mô tả chi tiết entities.json, relationships.json, graph.json]

### C. Cách chạy code

```bash
# Setup
pip install -r requirements.txt
export OPENAI_API_KEY="your_key"

# Run pipeline
python src/main.py

# Or individual steps
python src/quick_start.py  # Setup check
python src/extract_triples.py
python src/build_graph.py
python src/query_graph.py
python src/flat_rag.py
python src/benchmark.py
```

### D. Lỗi và cách khắc phục

**Lỗi 1: OPENAI_API_KEY not set**
- Giải pháp: Set environment variable trước khi chạy

**Lỗi 2: ChromaDB initialization error**
- Giải pháp: Xóa `.chroma` directory và chạy lại

---

*Report generated on [Date]*
