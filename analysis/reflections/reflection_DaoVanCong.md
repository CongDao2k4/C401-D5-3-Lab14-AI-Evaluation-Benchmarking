# Individual Reflection - Đào Văn Công

## 1. Engineering Contribution (Đóng góp kỹ thuật)
- **Phát triển Module Metrics (Cost & Retrieval):** Trực tiếp code logic tính toán `Hit Rate` và chi phí hệ thống (Token usage). Trong file `main.py`, tôi đã triển khai code để quy đổi `total_tokens` (6002 tokens) thành chi phí USD, giúp hệ thống theo dõi và báo cáo performance một cách định lượng rõ ràng.
- **Tối ưu hóa Hiệu năng (Asynchronous Workflow):** Để tránh rate limit và tối ưu Latency (còn ~2.01s/request), tôi đã thiết kế lại hàm `run_all()` trong `runner.py` để sử dụng `asyncio.gather()` kết hợp kỹ thuật batching thay vì chạy tuần tự.
- **Cải thiện độ ổn định hệ thống (Resilience):** Cấu trúc lại bộ đánh giá LLM Judge để bắt ngoại lệ API (exception handling). Nhờ đó, dù có test case bị timeout hay trả về JSON lỗi, toàn bộ pipeline 50 test cases vẫn được xử lý an toàn và luôn xuất ra file `summary.json` nguyên vẹn.

## 2. Technical Depth (Chiều sâu kiến thức)
- **MRR & Hit Rate vs Accuracy:** Qua báo cáo tổng kết, dù Hit Rate của hệ thống đạt **94%**, tôi thấy RAGAS Accuracy chỉ dừng ở **0.67**. Điều này chứng minh "Retrieval đúng không đồng nghĩa với Generation đúng". LLM vẫn gặp Hallucination nặng ở các câu thông số kỹ thuật (Ví dụ: bịa 4 cores thay vì 2 cores).
- **Cohen's Kappa & Agreement Rate (Độ đồng thuận Judge):** Với hệ thống Multi-Judge, tôi ghi nhận Agreement Rate trung bình đạt **0.82**. Điều này chứng minh sự đánh giá chéo giữa các giám khảo (Senior - Junior) đang đồng điệu và khách quan, tránh rủi ro khi chỉ dùng 1 giám khảo.
- **Position Bias (Thiên vị vị trí):** Trong quá trình tinh chỉnh Judge, tôi nhận ra LLM thường thiên vị các câu trả lời dài hoặc đứng trước. Việc gộp chung nhận định từ 2 mô hình đã giúp cân bằng lại và trung hòa độ bias này đáng kể.

## 3. Problem Solving (Kỹ năng giải quyết vấn đề)
- **Xử lý Rate Limit từ Provider (Lỗi 429):** Khi nhồi 50 test cases vào 2 model cùng lúc, API thường xuyên quá tải. Tôi giải quyết bằng cách áp dụng cơ chế Batching nhỏ và `await asyncio.sleep(5)` sau mỗi cụm, giúp hệ thống không bị nhà cung cấp block giữa chừng.
- **Đối phó với Hallucination dù Hit Rate cao:** Khi nhận diện ra Root Cause từ phân tích "5 Whys" (sai số CPU, RAM), thay vì chỉ tinh chỉnh prompt, tôi đề xuất việc thay đổi chiến lược Chunking sang phân tách theo ngữ nghĩa (Semantic) để đảm bảo các khối dữ liệu kỹ thuật không bị loãng bởi các đoạn text giới thiệu thừa thãi.
