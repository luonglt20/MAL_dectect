# 🛡️ PE Windows Malware Detection — XAI Dashboard

> **Đồ án Thạc sĩ** | An Toàn Thông Tin  
> *Ứng dụng Explainable AI (XAI) trong Nhận diện Mã Độc qua Hành vi Chuỗi API*

Dựa trên nghiên cứu: **Galli et al. (2024)** — *"Explainability in AI-based behavioral malware detection systems"*, Computers & Security, Elsevier.

---

## Tổng quan

Hệ thống phát hiện mã độc PE Windows thế hệ mới, kết hợp:
- Mô hình **BiLSTM + Self-Attention** (Intrinsic XAI) để phân loại hành vi mã độc
- Bốn thuật toán giải thích: **SHAP, LIME, LRP, Attention Weights**
- Giao diện **Web Dashboard** (Streamlit) trực quan hóa chuỗi API nguy hiểm theo màu nhiệt

Thay vì phân tích tĩnh (static analysis), hệ thống theo dõi **chuỗi 100 lệnh API đầu tiên** mà phần mềm gọi tới Windows Kernel khi thực thi trong môi trường Sandbox — bộc lộ bản chất của mã độc dù nó được mã hóa hay che giấu đến mức nào.

---

## Cải tiến so với bài báo gốc (SOTA)

| Tiêu chí | Baseline (Galli et al. 2024) | Bản nâng cấp |
|---|---|---|
| Kiến trúc | LSTM 1 chiều | **Bidirectional LSTM** |
| Khả năng giải thích | Post-hoc XAI (SHAP/LIME nặng) | **Intrinsic XAI** (Self-Attention tích hợp) |
| Giao diện | Console log / ma trận chéo | **Web Dashboard** màu nhiệt tương tác |
| Phần cứng | Dễ OOM (Exit Code 247) | Feature Bottlenecking — chạy ổn trên MacOS / RAM 8GB |
| Tốc độ XAI | ~50 phút | **~3 phút** (demo thời gian thực) |

---

## Cấu trúc dự án

```
XAI/
├── malware_xai_pipeline.py      # Pipeline huấn luyện chính (BiLSTM + XAI)
├── malware_dashboard.py         # Web App Streamlit
├── generate_html_report.py      # Xuất báo cáo HTML nghiệm thu
├── api_call_sequences.csv       # Dataset chuỗi API (43,876 mẫu)
├── xai_results/
│   └── results.json             # Kết quả XAI sau khi train
└── README.md
```

---

## 
Hướng dẫn cài đặt

### Yêu cầu môi trường

- Python 3.12+
- Hệ điều hành: macOS / Linux / Windows
- RAM tối thiểu: 8 GB

### Cài đặt thư viện

```bash
# Tạo virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# hoặc: .venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install tensorflow keras numpy pandas scikit-learn
pip install shap lime streamlit
```

---

## Chạy hệ thống

### Bước 1 — Huấn luyện mô hình & sinh kết quả XAI

```bash
python3 malware_xai_pipeline.py
```

Lệnh này sẽ:
1. Nạp **43,876 mẫu** (42,797 malware + 1,079 goodware) từ dataset API Call Sequences
2. Huấn luyện mô hình **BiLSTM + Self-Attention** (≈ 3 phút)
3. Chạy giải thích XAI trên 10 mẫu điển hình (SHAP, LIME, LRP, Attention)
4. Xuất kết quả ra `xai_results/results.json`

### Bước 2 — Mở Web Dashboard

```bash
python3 -m streamlit run malware_dashboard.py
```

Trình duyệt tự động mở trang **"🛡️ PE Windows Malware Detection - XAI Dashboard"**.

---

## Kiến trúc mô hình

```
Input (100 API indices)
        │
   Embedding Layer (dim=16)
        │
  Bidirectional LSTM (units=32 × 2 chiều)
        │
   Self-Attention Layer  ◄─── Intrinsic XAI
        │
    Dropout (0.3)
        │
  Dense + Softmax
        │
  Output: Malware / Goodware + Confidence %
```

### Siêu tham số (Hyperparameters)

| Tham số | Giá trị | Lý do |
|---|---|---|
| `sequence_length` | 100 | Mã độc bộc lộ bản chất trong 100 API đầu |
| `embedding_dim` | 16 | Nén 307 từ vựng API → vector ngữ nghĩa 16 chiều |
| `lstm_units` | 32 (×2 chiều = 64) | Cân bằng năng lực mô hình và tốc độ học |
| `batch_size` | 128 | Gradient descent ổn định, hội tụ trơn |
| `epochs` | 10 | Đạt convergence ~98.9% ở epoch 8-9 |
| `optimizer` | Adam | Adaptive learning rate |

---

## Kết quả

| Mô hình | Accuracy | F1-Score |
|---|---|---|
| LSTM (Baseline) | 99.43% | 93.79% |
| **BiLSTM + Attention (Đồ án)** | **~98.9%** | **Cải thiện XAI** |

> BiLSTM không chỉ nhắm tới accuracy tối đa mà ưu tiên **khả năng giải thích** và **phát hiện obfuscated malware** — giá trị cốt lõi của đồ án thạc sĩ.

### Hiệu quả các phương pháp XAI

| Phương pháp | Tốc độ | Stability | Perturbation |
|---|---|---|---|
| LRP | Nhanh nhất (~0.17s) | ✅ 1.000 | Tốt |
| SHAP (KernelExplainer) | Chậm | ✅ ~0.80 | **Tốt nhất** |
| LIME | Chậm | ❌ ~0.08 (kém) | Trung bình |
| Attention | Tức thì | ✅ 1.000 | Trung bình |

---

## Giao diện Dashboard

Dashboard phân tích chuỗi API theo màu nhiệt:

- 🔴 **Nền đỏ** → API đóng góp cao vào dự đoán **Malware** (nguy hiểm)
- 🟢 **Nền xanh** → API đóng góp vào nhận định **Goodware** (an toàn)
- Hover vào từng token để xem giá trị score chi tiết

Sidebar cho phép chọn **mẫu phân tích** và **thuật toán XAI** (SHAP / LIME / LRP / Attention).

---

## Dataset

**API Call Sequences** (de Oliveira & Sassi, 2023)
- Nguồn: Báo cáo Cuckoo Sandbox
- 42,797 chuỗi malware + 1,079 chuỗi goodware
- 307 hàm API Windows duy nhất
- Mỗi chuỗi: 100 lệnh API không lặp liên tiếp đầu tiên
- Tải tại: [IEEE DataPort](https://ieee-dataport.org/open-access/malware-analysis-datasets-api-call-sequences)

---

## 📖 Tài liệu tham khảo

```bibtex
@article{galli2024explainability,
  title={Explainability in AI-based behavioral malware detection systems},
  author={Galli, Antonio and La Gatta, Valerio and Moscato, Vincenzo 
          and Postiglione, Marco and Sperl{\`\i}, Giancarlo},
  journal={Computers \& Security},
  volume={141},
  pages={103842},
  year={2024},
  publisher={Elsevier}
}
```

---

## 👤 Tác giả đồ án

**Lê Tuấn Lương** — Chuyên ngành An Toàn Thông Tin  
Trường Đại học Công nghệ Thông tin — ĐHQG TP.HCM (UIT)

---

*Đồ án được phát triển với mục tiêu học thuật. Toàn bộ mã nguồn phục vụ nghiên cứu và thực nghiệm luận văn thạc sĩ.*
