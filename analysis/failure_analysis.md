# Báo cáo Phân tích Thất bại (Failure Analysis Report)

## 1. Tổng quan Benchmark
- **Tổng số cases:** 50
- **Tỉ lệ Pass/Fail:** 30/20
- **Điểm RAGAS trung bình:**
    - Accuracy: 0.67
    - Tone: 0.98
    - Safety: 1.00
- **Điểm LLM-Judge trung bình:** 4.43 / 5.0

## 2. Phân nhóm lỗi (Failure Clustering)
| Nhóm lỗi | Số lượng | Nguyên nhân dự kiến |
|----------|----------|---------------------|
| Hallucination / Sai số liệu | ~10 | Retriever lấy đúng Context nhưng LLM bị nhiễu bởi kiến thức nền (sinh ra sai số CPU, RAM) |
| Incomplete | ~10 | Prompt chưa yêu cầu Agent tập trung cụ thể vào các chi tiết cấu hình nhỏ lẻ |
| Tone Mismatch | 0 | Agent luôn giữ được Tone chuyên nghiệp (RAGAS Tone = 0.98) |

## 3. Phân tích 5 Whys (Chọn 3 case tệ nhất)

### Case #1: Cần tối thiểu bao nhiêu CPU cores? (Score 3.66)
1. **Symptom:** Agent trả lời sai số lượng CPU (đưa ra 4 cores thay vì 2 cores như Ground Truth).
2. **Why 1:** LLM không trích xuất chính xác con số 2 cores từ context mà tự suy diễn (hallucination).
3. **Why 2:** Vector DB (Hit Rate = 1.0) đã đưa context vào nhưng đoạn text đó bị trôi dạt (Lost in the middle).
4. **Why 3:** Chunk chứa thông tin "2 CPU cores" nằm chung với nhiều thông tin không liên quan khác khiến LLM mất tập trung.
5. **Why 4:** Chunking size quá lớn làm loãng thông tin quan trọng.
6. **Root Cause:** Chiến lược Chunking không phù hợp để bóc tách các thông số kỹ thuật độc lập.

### Case #2: Yêu cầu phần cứng để sử dụng Oracle Database 23ai? (Score 3.83)
1. **Symptom:** Agent đưa ra một danh sách dài các yêu cầu phần cứng tự chế (16GB RAM) thay vì 2 cores và 12GB RAM.
2. **Why 1:** LLM coi trọng kiến thức được huấn luyện từ trước (pre-trained knowledge về tiêu chuẩn máy chủ) hơn là văn bản cung cấp.
3. **Why 2:** System Prompt chưa áp đặt quy tắc "Strict RAG Mode" (cấm tự suy diễn nếu không có trong context).
4. **Why 3:** Khung prompt chung cho hệ thống chưa tối ưu cho việc truy xuất thông số kỹ thuật khắt khe.
5. **Why 4:** ...
6. **Root Cause:** Thiếu Guardrails tại bước Generation để khóa cứng giới hạn kiến thức của LLM.

### Case #3: Bao nhiêu GB RAM là đủ cài đặt? (Score 4.0)
1. **Symptom:** Trả lời "8GB tối thiểu, 16GB khuyến nghị" thay vì 12GB.
2. **Why 1:** Agent nhầm lẫn giữa thông số 12GB trong văn bản và các tiêu chuẩn RAM chung chung.
3. **Why 2:** Thông tin con số 12GB không được nhấn mạnh (highlight) khi nạp vào LLM context.
4. **Why 3:** Pipeline thiếu một bước Reranker để đẩy câu chứa con số 12GB lên vị trí đầu tiên của ngữ cảnh.
5. **Why 4:** Hệ thống hiện tại chỉ dựa vào vector similarity (đôi khi không bắt được keyword về số đếm tốt như con người).
6. **Root Cause:** Khoảng cách giữa Embedding Similarity và Keyword Matching trong các câu hỏi về số liệu.

## 4. Kế hoạch cải tiến (Action Plan)
- [x] Thay đổi Chunking strategy từ Fixed-size sang Semantic Chunking hoặc Markdown Header Splitter.
- [x] Cập nhật System Prompt để nhấn mạnh vào việc "Chỉ trả lời dựa trên context, nghiêm cấm suy diễn số liệu kỹ thuật".
- [ ] Thêm bước Reranking vào Pipeline (vd: dùng BGE-Reranker) để tăng độ chuẩn xác cho các truy vấn mang tính thông số.
