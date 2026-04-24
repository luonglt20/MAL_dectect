# Project Final Submission: XAI for Behavioral Malware Detection

Thư mục này chứa toàn bộ các thành phần quan trọng của dự án "Giải thích mô hình học sâu trong phát hiện mã độc dựa trên hành vi (XAI)".

## Cấu trúc thư mục

### 1. Source_Code/
Chứa mã nguồn cốt lõi của hệ thống:
*   `malware_xai_pipeline.py`: Pipeline chính để huấn luyện mô hình BiLSTM+Attention và chạy các thuật toán XAI (LIME, SHAP, LRP).
*   `generate_html_report.py`: Công cụ tạo báo cáo HTML trực quan từ kết quả XAI.
*   `malware_dashboard.py`: Dashboard phân tích mẫu mã độc.

### 2. Reports/
Chứa các kết quả và báo cáo đã được tạo ra:
*   `chuong_trinh_bao_cao.html`: Báo cáo hội đồng chi tiết với các biểu đồ so sánh.
*   `results.json`: Dữ liệu thô của các kết quả giải thích XAI.
*   `comparison_report.html`: Báo cáo so sánh các phương pháp XAI.

### 3. Documentation/
Tài liệu hướng dẫn và báo cáo thuyết trình:
*   `thesis_documentation.md`: Tài liệu tóm tắt nội dung luận văn/đồ án.
*   `bao_cao_ky_thuat_chi_tiet.md`: Báo cáo chi tiết về kỹ thuật và kiến trúc.
*   `G04-Report.pptx`: File slide thuyết trình cho hội đồng.
*   `Paper.pdf`: Tài liệu tham khảo (Bài báo gốc Galli et al. 2024).

### 4. Data/
Chứa các tập dữ liệu được sử dụng:
*   `api_call_sequences.csv`: Tập dữ liệu chuỗi API.
*   `malware.csv`: Tập dữ liệu phụ trợ.

---
**Hướng dẫn nhanh:** 
Để xem kết quả tổng quát nhất, hãy mở file `Reports/chuong_trinh_bao_cao.html` bằng trình duyệt web.
