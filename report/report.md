# GraphRAG Lab Report

**Name:** Vũ Như Đức  
**Date:** 5/5/2026  
**Course:** Day 19 Lab - Xây dựng hệ thống GraphRAG

---

## 1. Giới thiệu

### 1.1 GraphRAG là gì?
GraphRAG là cách kết hợp truy hồi thông tin bằng đồ thị tri thức với khả năng sinh ngôn ngữ của LLM. Thay vì chỉ tìm các đoạn văn gần nhất như Flat RAG, GraphRAG dùng entity linking, đồ thị quan hệ và traversal nhiều hop để gom các triple liên quan trước khi sinh câu trả lời. Cách này hữu ích khi câu hỏi cần suy luận qua nhiều thực thể, ví dụ mối quan hệ giữa hai công ty, người sáng lập, hoặc chuỗi sở hữu/investment.

### 1.2 Mục tiêu bài lab
Mục tiêu của bài lab là xây dựng một pipeline GraphRAG hoàn chỉnh trên corpus công ty công nghệ, gồm các bước: trích xuất entity/relation, tạo knowledge graph, truy vấn graph bằng BFS, so sánh với Flat RAG baseline, và tổng hợp kết quả thành báo cáo. Trong phiên bản này, toàn bộ phần sinh câu trả lời đã được chuyển sang NVIDIA API với model `openai/gpt-oss-20b`.

### 1.3 Tech Company Corpus
Corpus đầu vào là `data/corpus.json`, gồm 5 tài liệu gốc với các chủ đề: OpenAI, Qualcomm, Vingroup, Google, và Viettel. Sau khi tách theo đoạn văn, pipeline tạo ra 1912 chunks để xử lý. Corpus chứa nhiều loại thông tin như lịch sử công ty, quan hệ sở hữu, đầu tư, sản phẩm, tổ chức liên quan, và các mốc thời gian.

---

## 2. Mô tả Pipeline

### 2.1 Trích xuất Entity và Relation

**Phương pháp:**
- LLM được sử dụng: NVIDIA API qua OpenAI-compatible client
- Model: `openai/gpt-oss-20b`
- Prompt strategy: yêu cầu model trả về JSON thuần, gồm danh sách entities và relationships, chỉ giữ các quan hệ được nêu rõ trong văn bản

**Kết quả:**
- Số lượng entities: 764
- Số lượng relationships: 64

**Ví dụ output:**
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
- Chuẩn hóa tên entity bằng alias mapping trong cấu hình
- Gộp các thực thể trùng nhau theo tên chuẩn hóa
- Loại bỏ các node lặp khi xây graph bằng NetworkX

**Kết quả:**
- Số entities trước deduplication: 764
- Số entities sau deduplication: 475
- Tỷ lệ giữ lại sau deduplication: 62.2%

### 2.3 Xây dựng Knowledge Graph

**Công cụ sử dụng:** NetworkX

**Cấu trúc:**
- Node: thực thể như company, person, product, location, time
- Edge: quan hệ như FOUNDED_BY, INVESTED_IN, PARTNERED_WITH, DEVELOPED, OWNED_BY
- Node attributes: `type`, `original_name`, `mentions`
- Edge attributes: `relation`, `evidence`, `chunk_id`

**Thống kê đồ thị:**
- Số nodes: 475
- Số edges: 64
- Loại entities: Company, Location, Organization, Person, Product, Time
- Loại relations: CEO_OF, DEVELOPED, FOUNDED_BY, FOUNDED_IN, INVESTED_IN, LOCATED_IN, OWNED_BY, PARTNERED_WITH, USES

### 2.4 Truy vấn GraphRAG

**Phương pháp:**
1. Trích xuất entity từ câu hỏi bằng LLM
2. Tìm node khớp trong graph theo matching gần đúng
3. BFS traversal trong phạm vi 1-hop khi chạy nhanh
4. Thu thập supporting triples
5. Ghép context và sinh câu trả lời bằng NVIDIA API

**Ví dụ truy vấn thực tế:**
```text
Q: Who founded OpenAI?
A: No matching entities found in knowledge graph.
Supporting triples: []

Q: What is the relationship between Microsoft and OpenAI?
A: Microsoft is a key investor, strategic partner, and major shareholder of OpenAI.
Supporting triples used: 46 triples
```

### 2.5 Flat RAG Baseline

**Phương pháp:**
- Vector store: ChromaDB
- Embedding model: `all-MiniLM-L6-v2`
- Retrieval: top-k chunks theo độ tương đồng
- Synthesis: NVIDIA API model `openai/gpt-oss-20b`

---

## 3. Kết quả

### 3.1 Đồ thị tri thức

![Knowledge Graph](../outputs/graph.png)

Đồ thị cho thấy corpus xoay quanh các thực thể trung tâm như OpenAI, Microsoft, Google, Nvidia và một số nhân vật như Sam Altman, Elon Musk. Đồ thị khá dày ở vùng quanh OpenAI và Microsoft, phản ánh số lượng quan hệ đầu tư, hợp tác và sở hữu. Tuy nhiên nhiều node phụ vẫn là ngày tháng, tên nguồn tin hoặc thực thể ít thông tin, nên graph còn khá nhiễu và chưa gọn.

### 3.2 Benchmark Results

Dữ liệu benchmark hiện tại là một đợt chạy nhanh với 2 câu hỏi mẫu, nên chưa phải bộ test đầy đủ 20 câu. Bảng dưới đây phản ánh đúng kết quả trong `outputs/benchmark_results.csv`.

| ID | Câu hỏi | GraphRAG | Flat RAG | Graph Triples Used | Flat RAG Chunks Used | Nhận xét |
|----|---------|----------|----------|-------------------:|---------------------:|---------|
| 1 | Who founded OpenAI? | No matching entities found in knowledge graph. | The context does not provide the names of the individuals who founded OpenAI. | 0 | 3 | Cả hai đều không xác định được người sáng lập từ run này; Flat RAG trả lời tự nhiên hơn. |
| 2 | What is the relationship between Microsoft and OpenAI? | Microsoft is a key investor, strategic partner, and major shareholder of OpenAI. | Microsoft has made substantial financial investments in OpenAI and provides Azure cloud resources. | 46 | 3 | GraphRAG gom nhiều triple hơn và thể hiện traceability tốt hơn. |

### 3.3 Tính toán sai số

Trong lần chạy này chưa có ground truth chuẩn để tính accuracy chính thức. Vì vậy không thể tính precision/recall hay accuracy một cách nghiêm ngặt. Tuy nhiên, từ 2 câu hỏi mẫu có thể thấy:
- GraphRAG mạnh hơn khi cần trace các quan hệ phức tạp giữa Microsoft và OpenAI
- Flat RAG cho câu trả lời mạch lạc hơn ở câu hỏi không tìm được entity khớp trực tiếp

---

## 4. Phân tích so sánh

### 4.1 Ưu điểm của GraphRAG
- Có thể truy xuất nhiều triple liên quan trong một vùng lân cận của graph, phù hợp với câu hỏi multi-hop.
- Dễ kiểm tra nguồn gốc câu trả lời nhờ supporting triples.
- Với câu hỏi về Microsoft và OpenAI, GraphRAG thu được 46 triples, cho thấy khả năng gom ngữ cảnh tốt.

### 4.2 Ưu điểm của Flat RAG
- Triển khai đơn giản hơn, không cần xây graph hay entity linking phức tạp.
- Với câu hỏi không khớp entity rõ ràng, Flat RAG vẫn trả lời được nhờ đoạn văn liên quan.
- Số chunks truy hồi thấp hơn, nên pipeline nhẹ hơn ở bước truy vấn.

### 4.3 Trường hợp Flat RAG tốt hơn trong run này
- Câu hỏi “Who founded OpenAI?”: GraphRAG không tìm được node khớp, trong khi Flat RAG vẫn suy ra được rằng context không cung cấp tên người sáng lập.
- Đây là dấu hiệu cho thấy chất lượng entity matching là điểm yếu hiện tại của GraphRAG, không phải bản thân graph reasoning.

---

## 5. Chi phí và Performance

Pipeline đã được chạy ở chế độ tối ưu nhanh, nên thông số timing/token chưa được đo đầy đủ trong log hiện tại. Vì vậy phần này ghi nhận ở mức định tính.

| Metric | GraphRAG | Flat RAG | Ghi chú |
|--------|----------|----------|---------|
| Thời gian indexing (s) | N/A | N/A | Chưa benchmark thời gian chi tiết |
| Token dùng indexing | N/A | N/A | Chưa log token usage |
| Thời gian truy vấn trung bình (s) | N/A | N/A | Chưa benchmark chi tiết |
| Token dùng truy vấn trung bình | N/A | N/A | Chưa log token usage |
| Tổng chi phí | N/A | N/A | Không đủ dữ liệu để quy đổi chi phí |

---

## 6. Kết luận

### 6.1 Kết quả chính
Bài lab đã xây dựng được pipeline GraphRAG hoàn chỉnh với NVIDIA API, đọc trực tiếp từ `data/corpus.json`, xây knowledge graph bằng NetworkX, và tạo baseline Flat RAG bằng ChromaDB. Kết quả chạy thực tế cho thấy graph có 475 nodes và 64 edges sau deduplication, với 9 loại relation khác nhau. Benchmark mẫu cho thấy GraphRAG hữu ích trong truy vấn có nhiều quan hệ, còn Flat RAG linh hoạt hơn khi entity matching chưa tốt.

### 6.2 Khi nào nên dùng GraphRAG
GraphRAG phù hợp khi câu hỏi cần nhiều bước suy luận, cần truy vết nguồn gốc câu trả lời, hoặc dữ liệu có cấu trúc quan hệ rõ ràng như công ty, người, sản phẩm, đầu tư, sở hữu, hợp tác.

### 6.3 Khi nào nên dùng Flat RAG
Flat RAG phù hợp khi cần triển khai nhanh, dữ liệu chủ yếu là văn bản tự do, hoặc khi hệ thống entity linking chưa đủ tốt để xây graph chất lượng cao.

### 6.4 Đề xuất cải tiến
1. Entity Linking: Dùng NER model chuyên biệt thay vì LLM để giảm nhiễu.
2. Relation Confidence: Gắn confidence score cho từng quan hệ để lọc triple yếu.
3. Knowledge Update: Thêm cơ chế cập nhật graph khi có corpus mới.
4. Multi-language: Hỗ trợ tiếng Việt tốt hơn trong cả extraction và retrieval.
5. Visualization: Chuyển sang Neo4j Browser hoặc dashboard tương tác để khám phá graph tốt hơn.

---

## 7. Tài liệu tham khảo

- [SPEC.md](../SPEC.md) - Specification chi tiết
- [outputs/graph.png](../outputs/graph.png) - Ảnh đồ thị tri thức
- [outputs/benchmark_results.csv](../outputs/benchmark_results.csv) - Kết quả benchmark mẫu
- NetworkX: https://networkx.org/
- ChromaDB: https://docs.trychroma.com/
- NVIDIA API: https://integrate.api.nvidia.com/

---

## Phụ lục

### A. Danh sách câu hỏi benchmark đã chạy
1. Who founded OpenAI?
2. What is the relationship between Microsoft and OpenAI?

### B. Cấu trúc dữ liệu
- `entities.json`: danh sách thực thể trích xuất từ corpus
- `relationships.json`: danh sách quan hệ có evidence
- `graph.json`: đồ thị đã dedup và export từ NetworkX
- `query_results.json`: kết quả truy vấn GraphRAG
- `flat_rag_results.json`: kết quả Flat RAG
- `benchmark_results.csv`: bảng so sánh hai phương pháp

### C. Cách chạy code
```bash
pip install -r requirements.txt

# Chạy chế độ nhanh mặc định
python src/main.py

# Hoặc chạy từng bước
python src/quick_start.py
python src/extract_triples.py
python src/build_graph.py
python src/query_graph.py
python src/flat_rag.py
python src/benchmark.py
```

### D. Lưu ý về môi trường
- Dùng `NVIDIA_API_KEY` thay vì `OPENAI_API_KEY`
- Model mặc định: `openai/gpt-oss-20b`
- Tập dữ liệu đầu vào: `data/corpus.json`
- Chế độ nhanh được bật mặc định trong `main.py` nếu chưa ghi đè bằng biến môi trường

---

*Report generated on 5/6/2026*
