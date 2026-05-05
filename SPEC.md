# LAB DAY 19: Xây dựng hệ thống GraphRAG với Tech Company Corpus

## 1. Tổng quan

Bài lab này yêu cầu sinh viên xây dựng một hệ thống **GraphRAG** hoàn chỉnh trên một tập dữ liệu văn bản về các công ty công nghệ, gọi là **Tech Company Corpus**.

Khác với Flat RAG, vốn truy xuất thông tin bằng vector search trên các đoạn văn bản rời rạc, GraphRAG chuyển văn bản thành **đồ thị tri thức** gồm các thực thể, quan hệ và thuộc tính. Khi người dùng đặt câu hỏi, hệ thống có thể truy vấn theo các mối liên kết trong đồ thị để trả lời những câu hỏi cần suy luận nhiều bước.

Ví dụ các câu hỏi phù hợp với GraphRAG:

- OpenAI được thành lập bởi những ai?
- Microsoft có mối quan hệ gì với OpenAI?
- Công ty nào phát triển sản phẩm AI và có liên quan đến Alphabet?
- Một nhà sáng lập có liên quan đến nhiều công ty công nghệ nào?
- Công ty nào vừa đầu tư vào AI vừa sở hữu nền tảng cloud?

Kết quả cuối cùng của bài lab là một pipeline có khả năng lập chỉ mục dữ liệu, xây dựng đồ thị tri thức, truy vấn multi-hop và so sánh chất lượng trả lời với Flat RAG.

## 2. Mục tiêu bài học

Sau khi hoàn thành bài lab, sinh viên cần đạt được các mục tiêu sau:

1. Hiểu rõ quy trình trích xuất thực thể (**Entity Extraction**) và quan hệ (**Relation Extraction**) từ văn bản thô.
2. Phân biệt được **node**, **edge**, **entity**, **relation**, **attribute** và **triple** trong đồ thị tri thức.
3. Xây dựng được pipeline GraphRAG gồm các bước:
   - Nạp dữ liệu.
   - Chia nhỏ văn bản.
   - Trích xuất thực thể và quan hệ.
   - Chuẩn hóa và khử trùng lặp thực thể.
   - Xây dựng đồ thị tri thức.
   - Truy vấn đồ thị theo phạm vi 1-hop hoặc 2-hop.
   - Chuyển kết quả truy vấn thành ngữ cảnh văn bản để đưa vào LLM.
4. Làm quen với các công cụ quản lý và trực quan hóa đồ thị:
   - NetworkX.
   - Neo4j.
   - NodeRAG.
5. Đánh giá sự khác biệt giữa Flat RAG và GraphRAG về:
   - Độ chính xác.
   - Khả năng trả lời câu hỏi multi-hop.
   - Mức độ ảo giác.
   - Chi phí token.
   - Thời gian xử lý.

## 3. Kiến thức nền cần nghiên cứu

Trước khi bắt đầu code, sinh viên cần tìm hiểu và trả lời được các câu hỏi sau.

### 3.1. Entity Extraction

**Entity Extraction** là quá trình trích xuất các thực thể quan trọng từ văn bản.

Trong bài lab này, thực thể có thể thuộc các nhóm:

| Nhóm thực thể | Ví dụ |
| --- | --- |
| Company | OpenAI, Google, Microsoft, Meta, NVIDIA |
| Person | Sam Altman, Elon Musk, Sundar Pichai, Jensen Huang |
| Product | ChatGPT, Gemini, Azure, CUDA, Llama |
| Organization | Alphabet, Y Combinator, OpenAI LP |
| Location | San Francisco, Seattle, Mountain View |
| Time | 2015, 2023 |

Ví dụ văn bản đầu vào:

```text
OpenAI được thành lập bởi Sam Altman và Elon Musk vào năm 2015.
```

Các thực thể có thể trích xuất:

| Thực thể | Loại |
| --- | --- |
| OpenAI | Company |
| Sam Altman | Person |
| Elon Musk | Person |
| 2015 | Year |

Câu hỏi cần trả lời:

- Làm sao để LLM phân biệt đâu là thực thể và đâu là thuộc tính?
- Khi nào nên lưu một giá trị như node, khi nào nên lưu như attribute?
- Làm sao xử lý các tên riêng bị OCR sai hoặc viết không nhất quán?

### 3.2. Relation Extraction

**Relation Extraction** là quá trình xác định quan hệ giữa các thực thể.

Từ câu ví dụ:

```text
OpenAI được thành lập bởi Sam Altman và Elon Musk vào năm 2015.
```

Có thể trích xuất các triple:

```text
(OpenAI, FOUNDED_BY, Sam Altman)
(OpenAI, FOUNDED_BY, Elon Musk)
(OpenAI, FOUNDED_IN, 2015)
```

Mỗi triple gồm:

- **Subject**: thực thể nguồn.
- **Predicate**: loại quan hệ.
- **Object**: thực thể đích hoặc giá trị.

Danh sách predicate gợi ý:

| Predicate | Ý nghĩa |
| --- | --- |
| `FOUNDED_BY` | Được sáng lập bởi |
| `FOUNDED_IN` | Được thành lập vào năm |
| `CEO_OF` | Là CEO của |
| `OWNED_BY` | Thuộc sở hữu của |
| `SUBSIDIARY_OF` | Là công ty con của |
| `INVESTED_IN` | Đầu tư vào |
| `PARTNERED_WITH` | Hợp tác với |
| `DEVELOPED` | Phát triển sản phẩm |
| `USES` | Sử dụng công nghệ hoặc nền tảng |
| `LOCATED_IN` | Đặt tại địa điểm |

Yêu cầu quan trọng:

- Không tạo triple nếu câu gốc không có bằng chứng.
- Mỗi triple nên lưu kèm `evidence`.
- Predicate phải được đặt tên nhất quán.
- Nếu LLM không chắc chắn, cần đánh dấu hoặc loại bỏ triple đó.

### 3.3. Graph Construction

**Graph Construction** là quá trình chuyển danh sách triple thành đồ thị tri thức.

Ví dụ:

```text
OpenAI --FOUNDED_BY--> Sam Altman
OpenAI --FOUNDED_BY--> Elon Musk
OpenAI --FOUNDED_IN--> 2015
```

Trong đồ thị:

- Node biểu diễn thực thể.
- Edge biểu diễn quan hệ.
- Thuộc tính node có thể gồm `name`, `type`, `description`, `source`.
- Thuộc tính edge có thể gồm `relation`, `evidence`, `chunk_id`, `confidence`.

Câu hỏi cần trả lời:

- Tại sao khử trùng lặp (**Deduplication**) lại quan trọng trong đồ thị?
- Điều gì xảy ra nếu `Sam Altman`, `Sam Altmann` và `S. Altman` bị tạo thành ba node khác nhau?
- Làm sao lưu lại nguồn gốc của từng quan hệ để kiểm chứng câu trả lời?

### 3.4. Deduplication

Deduplication là bước gộp các thực thể hoặc quan hệ bị trùng lặp.

Ví dụ các cách viết cần được chuẩn hóa:

| Giá trị lỗi hoặc không nhất quán | Giá trị chuẩn |
| --- | --- |
| Open AI | OpenAI |
| Sam Altmann | Sam Altman |
| Google LLC | Google |
| Alphabet Inc. | Alphabet |
| Micro soft | Microsoft |

Gợi ý cách xử lý:

- Chuẩn hóa khoảng trắng.
- Chuyển tên về dạng thống nhất.
- Dùng alias dictionary cho các tên phổ biến.
- So khớp chuỗi gần đúng.
- Dùng embedding hoặc LLM để xác nhận hai thực thể có phải cùng một đối tượng hay không.

### 3.5. Query Answering

Trong GraphRAG, quá trình trả lời câu hỏi thường gồm:

1. Nhận câu hỏi từ người dùng.
2. Trích xuất thực thể chính trong câu hỏi.
3. Tìm node tương ứng trong đồ thị.
4. Duyệt các node lân cận trong phạm vi 1-hop hoặc 2-hop.
5. Thu thập các triple liên quan.
6. Chuyển triple thành ngữ cảnh văn bản.
7. Gửi câu hỏi và ngữ cảnh cho LLM.
8. Trả về câu trả lời kèm bằng chứng.

Ví dụ câu hỏi:

```text
OpenAI có mối liên hệ nào với Microsoft?
```

GraphRAG có thể tìm được các đường liên kết:

```text
Microsoft --INVESTED_IN--> OpenAI
OpenAI --USES--> Azure
Azure --OWNED_BY--> Microsoft
```

Sau đó hệ thống chuyển các triple thành ngữ cảnh để LLM tổng hợp câu trả lời.

### 3.6. BFS và vector search

**BFS (Breadth-First Search)** là thuật toán duyệt đồ thị theo từng lớp lân cận.

Nếu bắt đầu từ node `OpenAI`:

- 1-hop có thể gồm: Sam Altman, Elon Musk, ChatGPT, Microsoft.
- 2-hop có thể gồm: Azure, Satya Nadella, GitHub, Y Combinator.

**Vector search** tìm các chunk gần nhất với câu hỏi dựa trên embedding similarity.

| Tiêu chí | BFS trên đồ thị | Vector search |
| --- | --- | --- |
| Đơn vị truy vấn | Node và edge | Chunk văn bản |
| Phù hợp với | Quan hệ, suy luận nhiều bước | Tìm đoạn văn gần nghĩa |
| Điểm mạnh | Có đường liên kết rõ ràng | Dễ triển khai |
| Điểm yếu | Cần đồ thị chất lượng tốt | Dễ thiếu thông tin multi-hop |

## 4. Công cụ sử dụng

### 4.1. NetworkX

NetworkX là thư viện Python dùng để tạo, xử lý và phân tích đồ thị.

Phù hợp khi:

- Muốn tạo prototype nhanh.
- Muốn chạy offline trong notebook.
- Muốn tự cài đặt thuật toán traversal.
- Muốn vẽ đồ thị bằng Matplotlib.

Hạn chế:

- Không tối ưu cho đồ thị rất lớn.
- Không có giao diện truy vấn trực quan như Neo4j Browser.

### 4.2. Neo4j

Neo4j là cơ sở dữ liệu đồ thị phổ biến, sử dụng ngôn ngữ truy vấn Cypher.

Phù hợp khi:

- Cần lưu trữ đồ thị bền vững.
- Muốn trực quan hóa node và edge.
- Muốn truy vấn đồ thị bằng Cypher.
- Muốn mở rộng bài lab thành ứng dụng GraphRAG lớn hơn.

Ví dụ Cypher:

```cypher
MATCH (c:Company {name: "OpenAI"})-[r]-(n)
RETURN c, r, n
```

Lưu ý:

- Sinh viên có thể dùng Neo4j Desktop hoặc chạy Neo4j bằng Docker.
- Khi tạo node và relationship, nên dùng `MERGE` để tránh trùng lặp.

### 4.3. NodeRAG

NodeRAG là framework mã nguồn mở hỗ trợ xây dựng GraphRAG trên nền Python và NetworkX.

Phù hợp khi:

- Muốn bắt đầu nhanh.
- Không muốn cấu hình database phức tạp.
- Muốn tập trung vào logic GraphRAG thay vì tự viết toàn bộ framework.

Nếu chọn NodeRAG, sinh viên vẫn cần giải thích pipeline bên trong hoạt động như thế nào, không chỉ chạy thư viện như một black box.

## 5. Thiết lập môi trường

### 5.1. Phiên bản khuyến nghị

- Python 3.10 trở lên.
- VS Code hoặc Jupyter Notebook.
- Tài khoản OpenAI hoặc một LLM provider tương đương.
- Neo4j Desktop hoặc Docker nếu chọn Neo4j.

### 5.2. Cài đặt thư viện

Cài đặt các thư viện cơ bản cho xử lý ngôn ngữ và đồ thị:

```bash
pip install networkx matplotlib neo4j openai pandas
```

Cài đặt NodeRAG:

```bash
pip install noderag
```

Nếu sử dụng LangChain để hỗ trợ pipeline:

```bash
pip install langchain langchain-openai
```

Nếu xây dựng Flat RAG baseline:

```bash
pip install chromadb faiss-cpu sentence-transformers
```

Thiết lập API key trên macOS/Linux:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Thiết lập API key trên Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

## 6. Dữ liệu đầu vào: Tech Company Corpus

Sinh viên cần chuẩn bị một corpus gồm ít nhất 20-30 câu về các công ty công nghệ.

Corpus nên bao gồm các nhóm thông tin:

- Nhà sáng lập.
- Năm thành lập.
- Sản phẩm.
- Công ty mẹ.
- Công ty con.
- Quan hệ đầu tư.
- Quan hệ đối tác.
- Địa điểm trụ sở.
- Lãnh đạo hiện tại hoặc cựu lãnh đạo.

Ví dụ corpus:

```text
OpenAI was founded in 2015 by Sam Altman, Greg Brockman, Ilya Sutskever, John Schulman, Wojciech Zaremba, and Elon Musk.
Microsoft invested in OpenAI and integrated OpenAI models into Azure.
Google is owned by Alphabet and developed Gemini as an AI assistant.
NVIDIA develops GPUs that are widely used for training large language models.
Meta developed Llama and released several open-weight language models.
```

Sinh viên có thể dùng tiếng Anh, tiếng Việt hoặc song ngữ. Tuy nhiên, tên thực thể cần được viết nhất quán để giảm lỗi trích xuất.

## 7. Hướng dẫn thực hiện

### Bước 1: Nạp và tiền xử lý dữ liệu

Yêu cầu:

1. Đọc corpus từ file `.txt`, `.md` hoặc danh sách string trong notebook.
2. Chia văn bản thành các chunk nhỏ.
3. Lưu metadata cho từng chunk:
   - `chunk_id`.
   - `source`.
   - `text`.

Gợi ý cấu trúc dữ liệu:

```python
chunks = [
    {
        "chunk_id": "chunk_001",
        "source": "tech_company_corpus.txt",
        "text": "OpenAI was founded in 2015 by Sam Altman..."
    }
]
```

### Bước 2: Trích xuất thực thể và quan hệ

Viết hàm dùng LLM để trích xuất entity và relationship từ từng chunk.

Prompt nên yêu cầu LLM trả về JSON có cấu trúc rõ ràng:

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
      "evidence": "OpenAI was founded in 2015 by Sam Altman..."
    }
  ]
}
```

Yêu cầu chất lượng:

- JSON phải parse được bằng code.
- Không tạo quan hệ nếu không có bằng chứng.
- Mỗi relationship phải có `subject`, `predicate`, `object` và `evidence`.
- Predicate nên viết hoa theo dạng snake case.
- Tên thực thể phải được chuẩn hóa trước khi đưa vào đồ thị.

### Bước 3: Chuẩn hóa và khử trùng lặp

Sinh viên cần viết hàm chuẩn hóa tên thực thể.

Ví dụ:

```python
def normalize_entity_name(name: str) -> str:
    return " ".join(name.strip().split())
```

Nên bổ sung alias map:

```python
ALIASES = {
    "Alphabet Inc.": "Alphabet",
    "Google LLC": "Google",
    "Open AI": "OpenAI",
    "Sam Altmann": "Sam Altman"
}
```

Yêu cầu:

- Gộp các node trùng tên sau khi normalize.
- Loại bỏ triple trùng lặp.
- Giữ lại danh sách evidence nếu một triple xuất hiện trong nhiều chunk.
- Ghi chú các trường hợp deduplication thủ công trong báo cáo.

### Bước 4: Xây dựng đồ thị

Sinh viên chọn một trong ba hướng triển khai.

#### Lựa chọn A: NetworkX

Phù hợp để chạy offline trong notebook.

Ví dụ:

```python
import networkx as nx

graph = nx.MultiDiGraph()

graph.add_node("OpenAI", type="Company")
graph.add_node("Sam Altman", type="Person")
graph.add_edge("OpenAI", "Sam Altman", relation="FOUNDED_BY")
```

Yêu cầu:

- Mỗi node có `name` và `type`.
- Mỗi edge có `relation`, `evidence` và `source`.
- Có hàm vẽ đồ thị bằng Matplotlib.
- Có hàm lấy các triple trong phạm vi 1-hop và 2-hop.

#### Lựa chọn B: Neo4j

Phù hợp nếu muốn trực quan hóa các mối liên kết bằng Neo4j Browser hoặc Bloom.

Ví dụ:

```cypher
MERGE (c:Company {name: "OpenAI"})
MERGE (p:Person {name: "Sam Altman"})
MERGE (c)-[:FOUNDED_BY]->(p)
```

Yêu cầu:

- Dùng `MERGE` để tránh tạo node trùng lặp.
- Lưu evidence trên relationship.
- Có ảnh chụp màn hình đồ thị từ Neo4j.
- Có ít nhất 3 câu lệnh Cypher dùng để kiểm tra đồ thị.

#### Lựa chọn C: NodeRAG

Phù hợp nếu muốn một giải pháp trọn gói đã có sẵn logic GraphRAG.

Yêu cầu:

- Mô tả cách NodeRAG lập chỉ mục dữ liệu.
- Mô tả cách NodeRAG sử dụng đồ thị khi truy vấn.
- Xuất được danh sách triple hoặc cấu trúc đồ thị trung gian để kiểm tra.
- So sánh kết quả NodeRAG với Flat RAG baseline.

### Bước 5: Truy vấn GraphRAG

Viết hàm xử lý truy vấn theo logic:

1. Nhận câu hỏi từ người dùng.
2. Trích xuất thực thể chính trong câu hỏi, ví dụ `Google`, `OpenAI`, `Microsoft`.
3. Tìm node tương ứng trong đồ thị.
4. Duyệt các node lân cận trong phạm vi 2-hop.
5. Gom các triple liên quan.
6. Chuyển triple thành văn bản.
7. Gửi văn bản và câu hỏi cho LLM.
8. Trả về câu trả lời và các triple hỗ trợ.

Ví dụ textualization:

```text
OpenAI was founded by Sam Altman.
OpenAI was founded by Elon Musk.
Microsoft invested in OpenAI.
OpenAI uses Azure.
Azure is owned by Microsoft.
```

Ví dụ output:

```json
{
  "question": "OpenAI có mối liên hệ nào với Microsoft?",
  "answer": "OpenAI có quan hệ với Microsoft thông qua đầu tư và hạ tầng Azure.",
  "supporting_triples": [
    ["Microsoft", "INVESTED_IN", "OpenAI"],
    ["OpenAI", "USES", "Azure"],
    ["Azure", "OWNED_BY", "Microsoft"]
  ]
}
```

### Bước 6: Xây dựng Flat RAG baseline

Để so sánh công bằng, sinh viên cần xây dựng một baseline Flat RAG.

Yêu cầu:

1. Chia corpus thành chunk.
2. Tạo embedding cho từng chunk.
3. Lưu embedding vào ChromaDB, FAISS hoặc vector store tương đương.
4. Khi có câu hỏi, lấy top-k chunk gần nhất.
5. Đưa các chunk vào LLM để tạo câu trả lời.

Flat RAG baseline không sử dụng đồ thị, không duyệt node và không dùng quan hệ đã trích xuất.

### Bước 7: So sánh và đánh giá

Sinh viên chạy ít nhất 20 câu hỏi benchmark trên cả hai hệ thống:

- Flat RAG: chỉ dùng vector search.
- GraphRAG: dùng đồ thị tri thức đã xây dựng.

Tập câu hỏi cần có:

- 5 câu hỏi fact lookup đơn giản.
- 5 câu hỏi về quan hệ giữa hai thực thể.
- 5 câu hỏi multi-hop.
- 5 câu hỏi dễ gây nhầm lẫn hoặc dễ khiến Flat RAG thiếu ngữ cảnh.

Ví dụ:

| Nhóm | Câu hỏi |
| --- | --- |
| Fact lookup | OpenAI được thành lập vào năm nào? |
| Fact lookup | Ai là CEO của Google? |
| Relation | Microsoft có quan hệ gì với OpenAI? |
| Relation | Alphabet sở hữu công ty nào trong corpus? |
| Multi-hop | Công ty nào phát triển sản phẩm AI và có liên quan đến Microsoft? |
| Multi-hop | Nhà sáng lập nào có liên quan đến cả OpenAI và Tesla? |
| Robustness | Công ty nào phát triển mô hình AI nhưng không phải công ty con của Alphabet? |

Bảng đánh giá cần có các cột:

| ID | Câu hỏi | Đáp án đúng | Flat RAG answer | GraphRAG answer | Flat RAG đúng? | GraphRAG đúng? | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- | --- |

Cần ghi lại các trường hợp Flat RAG bị ảo giác hoặc trả lời thiếu, trong khi GraphRAG trả lời đúng nhờ truy vấn theo quan hệ.

## 8. Báo cáo cần nộp

Báo cáo cuối cùng cần bao gồm:

1. Giới thiệu ngắn gọn về GraphRAG và mục tiêu bài lab.
2. Mô tả Tech Company Corpus đã sử dụng.
3. Mô tả pipeline trích xuất entity và relationship.
4. Thống kê đồ thị:
   - Số node.
   - Số edge.
   - Số loại entity.
   - Số loại relationship.
5. Ảnh chụp màn hình đồ thị tri thức:
   - Từ Neo4j Browser/Bloom, hoặc
   - Từ NetworkX + Matplotlib.
6. Mô tả cách hệ thống truy vấn 2-hop.
7. Bảng so sánh 20 câu hỏi benchmark giữa Flat RAG và GraphRAG.
8. Phân tích các trường hợp Flat RAG sai nhưng GraphRAG đúng.
9. Phân tích chi phí:
   - Token usage khi indexing.
   - Token usage khi querying.
   - Thời gian xây dựng đồ thị.
   - Thời gian trả lời trung bình.
10. Kết luận và đề xuất cải tiến.

## 9. Deliverables

Sinh viên nộp các thành phần sau:

1. Mã nguồn:
   - File `.py` hoặc `.ipynb`.
   - Nếu có nhiều file, cần có `README.md` hướng dẫn chạy.
2. Corpus:
   - File dữ liệu đầu vào, ví dụ `tech_company_corpus.txt`.
3. Kết quả trích xuất:
   - File JSON/CSV chứa entities và relationships.
4. Đồ thị tri thức:
   - File export, ví dụ GraphML, JSON hoặc Neo4j dump nếu có.
5. Ảnh chụp màn hình đồ thị.
6. Bảng benchmark 20 câu hỏi.
7. Báo cáo phân tích kết quả.

## 10. Tiêu chí chấm điểm

| Hạng mục | Điểm tối đa | Mô tả |
| --- | ---: | --- |
| Hiểu và mô tả đúng bài toán GraphRAG | 1.0 | Giải thích được Flat RAG, GraphRAG và lý do cần đồ thị |
| Trích xuất entity/relation | 2.0 | Triple đúng, có schema rõ ràng, có evidence |
| Xây dựng đồ thị | 2.0 | Node/edge hợp lý, có deduplication, có metadata |
| Truy vấn GraphRAG | 2.0 | Hỗ trợ truy vấn 2-hop, textualization tốt, câu trả lời có căn cứ |
| So sánh với Flat RAG | 1.5 | Có baseline và bảng benchmark tối thiểu 20 câu hỏi |
| Báo cáo và trực quan hóa | 1.0 | Có ảnh đồ thị, thống kê và phân tích lỗi |
| Chất lượng code | 0.5 | Code rõ ràng, dễ chạy, có hướng dẫn |

Tổng điểm: 10.

## 11. Gợi ý cấu trúc thư mục

```text
Day19_Lab_GraphRAG/
├── README.md
├── SPEC.md
├── data/
│   └── tech_company_corpus.txt
├── notebooks/
│   └── graphrag_lab.ipynb
├── src/
│   ├── extract_triples.py
│   ├── build_graph.py
│   ├── query_graph.py
│   └── flat_rag.py
├── outputs/
│   ├── entities.json
│   ├── relationships.json
│   ├── graph.png
│   └── benchmark_results.csv
└── report/
    └── report.md
```

## 12. Đề xuất công cụ

| Mục tiêu | Công cụ gợi ý | Lý do |
| --- | --- | --- |
| Dễ bắt đầu | NodeRAG | Tích hợp sẵn logic GraphRAG, không cần cấu hình database phức tạp |
| Trực quan hóa tốt nhất | Neo4j | Giao diện đồ họa giúp quan sát tri thức được kết nối như thế nào |
| Nghiên cứu thuật toán | NetworkX | Cho phép can thiệp sâu vào thuật toán đồ thị và traversal |
| So sánh với Flat RAG | ChromaDB hoặc FAISS | Phù hợp để xây dựng vector search baseline |

## 13. Lưu ý về lỗi OCR và chất lượng dữ liệu

Vì file gốc được copy từ OCR, sinh viên cần chú ý sửa các lỗi thường gặp trước khi đưa dữ liệu vào pipeline:

- Lỗi dấu tiếng Việt.
- Tách sai tên riêng.
- Nhầm ký tự `l`, `I`, `1`.
- Nhầm ký tự `O`, `0`.
- Thừa khoảng trắng.
- Xuống dòng sai giữa câu.
- Sai tên thư viện hoặc tên công cụ, ví dụ `Neo4j`, `NetworkX`, `NodeRAG`.

Trong quá trình xây dựng GraphRAG, không nên để LLM tự suy đoán khi dữ liệu gốc không rõ ràng. Nếu corpus không chứa đủ thông tin, hệ thống nên trả lời:

```text
Không đủ thông tin trong corpus.
```

## 14. Kết quả kỳ vọng

Sau bài lab, sinh viên có một hệ thống GraphRAG có khả năng:

1. Đọc corpus về các công ty công nghệ.
2. Trích xuất danh sách thực thể và quan hệ.
3. Xây dựng đồ thị tri thức có thể trực quan hóa.
4. Trả lời câu hỏi bằng truy vấn đồ thị 2-hop.
5. So sánh kết quả với Flat RAG.
6. Phân tích ưu điểm, hạn chế và chi phí của GraphRAG.
