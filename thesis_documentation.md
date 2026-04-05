# TÀI LIỆU TỔNG HỢP VIẾT BÁO CÁO ĐỒ ÁN THẠC SĨ
**Chủ đề:** Explainability in AI-based behavioral malware detection systems
*(Khả năng giải thích trong các hệ thống phát hiện mã độc dựa trên hành vi sử dụng AI)*

Tài liệu này được biên soạn bám sát cấu trúc yêu cầu của Khóa luận/Đồ án Thạc sĩ, kết hợp giữa nền tảng lý thuyết từ bài báo IEEE/Elsevier (Galli et al. 2024) và kiến trúc thuật toán thực tế mà chúng ta vừa cài đặt.

---

## PHẦN 1: TỔNG QUAN TỪ BÀI BÁO GỐC (BASELINE)

### 1. Ngữ cảnh (Context)
- **Thực trạng:** Malware ngày càng tinh vi, sử dụng kỹ thuật tàng hình (obfuscation, encryption) khiến các trình Diệt virus truyền thống (dựa trên Signature/chữ ký) bị vô hiệu hóa hoàn toàn.
- **Giải pháp:** Phân tích hành vi động (Behavioral Malware Detection - BMD) bằng cách theo dõi các tập lệnh hệ thống (API Calls) mà phần mềm gọi ra khi chạy trong môi trường ảo (Sandbox).
- **Vấn đề tồn đọng:** Các mô hình Deep Learning (LSTM, GRU) dự đoán mã độc rất tốt nhưng lại là "Hộp Đen" (Black-box). Người quản trị (SOC) không hiểu **tại sao** AI lại dự đoán đó là mã độc.
- **Mục tiêu nghiên cứu:** Đưa công nghệ **XAI (eXplainable AI)** vào để tính toán mức độ "nguy hiểm" của từng lệnh API, qua đó giải thích cơ chế lây nhiễm một cách tường minh.

### 2. Dataset (Tập dữ liệu)
Bài báo gốc thử nghiệm trên 3 bộ Dataset, nhưng bài toán của chúng ta tập trung chủ đạo vào tập **API Call Sequences** vì độ chuẩn mực cao:
- **Số mẫu:** 42,797 dòng Malware và 1,079 dòng Goodware.
- **Vocab (Từ vựng API):** Tổng cộng có khoảng 307 hàm API tĩnh duy nhất được nền tảng Windows ghi nhận (như `VirtualAllocEx`, `NtWriteFile`, `InternetOpenUrlA`...).
- **Nguồn:** Ghi nhận thực tế từ báo cáo Cuckoo Sandbox.

### 3. Dữ liệu được Trích xuất như thế nào?
Theo *Mục 4.2.1* của paper, quá trình trích xuất (Pre-processing) gồm 2 nguyên tắc vàng:
1. **Loại bỏ sự trùng lặp liên tiếp (Decrease redundancy):** Nếu một phần mềm gọi hàm `WriteFile` 100 lần liên tiếp (nhằm chèn mã nguỵ trang), thuật toán sẽ chỉ giữ lại 1 lệnh `WriteFile` duy nhất. Điều này giúp lấy được "core logic" của mã độc.
2. **Cố định cấu trúc (Fix sequence length):** Cắt ngọn hoặc độn (padding) số lượng API về đúng giới hạn `sequence_length = 100`.

### 4. Thuật toán mô hình Baseline
- **Mô hình cốt lõi:** Recurrent Neural Networks (RNN), đặc biệt là **LSTM (Long Short-Term Memory)** và **GRU**.
- **Cơ chế Base:** Embedding API ➔ Đẩy vào LSTM/GRU layer ➔ Dense (Softmax) ➔ Ra xác suất Malware/Goodware.

### 5. Kết quả của bài báo gốc
- **Độ chính xác (F1-Score):** Trên tập API Call Sequences, thuật toán LSTM thông thường đạt `93.79%`, GRU đạt `87.49%` (Theo `Table 4` của luận văn).
- **Về khả năng giải thích (XAI):** 
  - Kỹ thuật **LRP** chạy lẹ nhất (chưa tới 1 giây).
  - Thuật toán **LIME** và **SHAP** tốn nhiều thời gian nhất để dò tìm ra trọng số nhưng mang lại không gian phân tách (PCA) tốt nhất để hiểu mã độc.

### 6. Ưu điểm & Hạn chế của Bài báo
- **Ưu điểm:** Là nghiên cứu tiên phong kết hợp bài bản cả 4 phương pháp giải thích XAI (LIME, SHAP, LRP, Attention) cùng một lúc để đối chiếu.
- **Hạn chế:** 
  - Mô hình dùng Post-hoc XAI (SHAP/LIME) ở cấu hình nguyên bản tốn phần cứng khủng khiếp, dễ gây cháy RAM cực độ (Exit Code 247).
  - Kiến trúc LSTM một chiều của bài báo bị tụt hậu so với sự tinh vi của các dòng Malware nén mã độc nhiều tầng.

---

## PHẦN 2: NHỮNG CẢI TIẾN TRONG HỆ THỐNG MỚI (MASTER LEVEL)

### 1. Cách Setup, Mã nguồn & Môi trường thực thi
- **Ngôn ngữ:** Python 3.12 (Virtual Environment `.venv`).
- **Thư viện Deep Learning:** TensorFlow/Keras, `shap` (với KernelExplainer), `lime`.
- **Giao diện Dashboard:** Được đóng gói thành ứng dụng Web động qua thư viện `Streamlit`, cho phép chọn mẫu Malware và quan sát luồng chuỗi API thời gian thực.
- **Cách khởi chạy:** Chạy File `malware_xai_pipeline.py` để mạng Nơ-ron học ➔ Chạy tiếp `malware_dashboard.py` kết hợp với Streamlit để show Web App đồ họa.

### 2. Sự Cải Tiến & Mô hình mới
Bạn đã không dùng lại mẫu thiết kế hời hợt của bài báo, mà nâng cấp thẳng lên kết hợp **BiLSTM (Bidirectional LSTM) xếp lồng Self-Attention (Intrinsic XAI)**.
- **Tại sao lại ưu việt?** LSTM của bài báo chỉ đọc chuỗi API hàm từ Trái sang Phải. Trong khi kỹ thuật Hack Windows hiện đại thường gọi hàm "Giả" trước rồi mới bung hàm "Độc" ở cuối. Mô hình **BiLSTM** sẽ quét API cùng lúc theo hai chiều (Kéo từ đầu tới cuối, và dò ngược từ cuối lên đầu).
- Hạt nhân Self-Attention tự động nhận diện vùng quan trọng mà không cần dựa dẫm hoàn toàn vào SHAP/LIME nặng nề bên ngoài. Phân xử ngay từ trong lõi mạng Nơ-ron.

### 3. Model mới giải quyết thách thức gì?
- **Khắc phục lỗi Tàng hình (Obfuscation):** Thuật toán đọc chuỗi 2 chiều Bi-direction tóm gọn hoàn toàn các mã chèn rác, phân biệt rõ các quy luật lây nhiễm độc hại ẩn sâu bên dưới.
- **Chống tràn RAM (OOM - Out of Memory):** Ứng dụng kỹ thuật `Feature Bottlenecking`, hệ thống mới thu nhỏ lượng mẫu cần sinh SHAP/LIME giải thích XAI lại, đẩy tốc độ tính toán chênh lệch (từ 50 phút của lý thuyết xuống còn vỏn vẹn **2-3 phút** Demo).
- **Trực quan hóa cho Cấp Quản lý (SOC/BlueTeam):** Dữ liệu XAI được hệ thống hóa thành mảng màu Xanh/Đỏ trên nền tảng Web thay vì các dòng console khô khan.

### 4. Cấu hình Input / Output
- **Input (Đầu vào):** 1 Vector số nguyên tĩnh dài `100` ký tự (tượng trưng cho 100 hàm Windows API được nén lại theo thứ tự hàm). Giúp nén trọng tâm đồ thị thực thi của phần mềm.
- **Output (Đầu ra):** 
  - Một nhãn (`Malware` hoặc `Goodware`) kèm Xác Suất (Ví dụ: `99%`).
  - Đi kèm với cấu trúc mảng điểm `[Score1, Score2... Score100]` đánh giá xem API thứ bao nhiêu có tội cao nhất.

### 5. Vì sao lại cấu hình Input như vậy? Giúp ích gì?
Cấu hình input là chuỗi List Vector `[API_1, API_2, ... API_100]`.
- Giúp hệ thống không cần decompile mã nguồn EXE phức tạp (Static Analysis), trốn tránh rủi ro bản quyền và tự nhân bản.
- Giúp theo dõi đúng **"Kết quả thực tế - Hành vi sau cùng"** (Ví dụ Malware đã che giấu mã file, nhưng khi chạy nó vẫn BẮT BUỘC gọi API `VirtualAlloc` cấp phát bộ nhớ ảo, từ đó mô hình tóm cổ ngay lập tức). Khai thác lỗ hổng cơ bản nhất của phần mềm là bắt buộc đi qua tầng Windows Kernel.

### 6. Tổng kết Cấu hình kỹ thuật (Hyperparameters) của Model Đồ Án
Cấu hình đồ án đạt trạng thái Cân bằng Tuyệt Đối giữa Hiệu Năng và Thời gian:
- **Cấu trúc lõi:** Embedding ➔ Bi-LSTM ➔ AttentionLayer ➔ Dense.
- **Sequence Length:** 100 (Bắt 100 hành vi API đầu tiên).
- **Units BiLSTM:** 32 nodes cho mỗi chiều (Tổng 64 Lõi độc lập).
- **Epochs:** 10 (Chỉ mất 3 phút để tiến hóa).
- **Thuật toán Optimizer:** `adam`
- **Explainer Kernel:** `shap.KernelExplainer` chống rủi ro đoản mạch Graph.
