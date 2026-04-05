import json
import os

def generate_training_report(output_data, out_path_html):
    history = output_data.get("training_history", {})
    if not history:
        print("[WARNING] Không tìm thấy dữ liệu Training History.")
        return
        
    config = output_data.get("config", {})
    lstm_cr = output_data.get("classification_report", {})
    att_cr = output_data.get("attention_classification_report", {})

    # Hàm render từng bảng Classification Report
    def render_cr_table(cr, title):
        rows = ""
        for key, metrics in cr.items():
            if isinstance(metrics, dict):
                rows += f"""
                <tr class="border-b border-gray-700 bg-gray-800 hover:bg-gray-700">
                    <td class="px-6 py-4 font-medium text-white">{key}</td>
                    <td class="px-6 py-4 text-center">{metrics['precision']:.3f}</td>
                    <td class="px-6 py-4 text-center">{metrics['recall']:.3f}</td>
                    <td class="px-6 py-4 text-center">{metrics['f1-score']:.3f}</td>
                    <td class="px-6 py-4 text-center">{int(metrics['support'])}</td>
                </tr>
                """
            elif key == "accuracy":
                rows += f"""
                <tr class="border-b border-gray-700 bg-indigo-900 border-indigo-500 hover:bg-indigo-800">
                    <td class="px-6 py-4 font-bold text-white">Overall Accuracy</td>
                    <td class="px-6 py-4 text-center font-bold text-indigo-300" colspan="3">{metrics:.3f}</td>
                    <td class="px-6 py-4 text-center text-gray-400">-</td>
                </tr>
                """
        return f"""
        <div class="relative overflow-x-auto shadow-xl sm:rounded-lg mb-8 border border-gray-700">
            <h3 class="p-4 text-xl font-bold bg-gray-900 text-indigo-400 border-b border-gray-700">{title}</h3>
            <table class="w-full text-sm text-left text-gray-300">
                <thead class="text-xs text-gray-400 uppercase bg-gray-900">
                    <tr>
                        <th scope="col" class="px-6 py-3">Class/Metric</th>
                        <th scope="col" class="px-6 py-3 text-center">Precision</th>
                        <th scope="col" class="px-6 py-3 text-center">Recall</th>
                        <th scope="col" class="px-6 py-3 text-center">F1-Score</th>
                        <th scope="col" class="px-6 py-3 text-center">Support</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo Cáo Đào Tạo AI - Đồ Án Mã Độc</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ background-color: #0d1117; color: #c9d1d9; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }}
        .glass-panel {{ background: rgba(22, 27, 34, 0.8); backdrop-filter: blur(10px); border: 1px solid #30363d; border-radius: 12px; }}
        .gradient-text {{ background: linear-gradient(90deg, #A78BFA, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>
</head>
<body class="p-6 md:p-10">

    <!-- Header Section -->
    <header class="mb-10 text-center">
        <h1 class="text-4xl md:text-5xl font-extrabold mb-3 gradient-text uppercase tracking-wider">
            Báo Cáo Nghiệm Thu Mô Hình
        </h1>
        <p class="text-gray-400 text-lg">Phân Tích Hành Vi Mã Độc - BiLSTM & Self-Attention XAI</p>
    </header>

    <!-- Config Parameters -->
    <div class="glass-panel p-6 shadow-2xl mb-10 max-w-5xl mx-auto">
        <h2 class="text-2xl font-bold text-white mb-4 border-b border-gray-700 pb-2">Tham Số Phần Cứng (Hyperparameters)</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div class="bg-gray-800 p-4 rounded-lg">
                <div class="text-gray-400 text-sm">Sequence Length</div>
                <div class="text-xl font-bold text-blue-400">{config.get('sequence_length')} API</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg">
                <div class="text-gray-400 text-sm">BiLSTM Units</div>
                <div class="text-xl font-bold text-purple-400">{config.get('lstm_units')} Lõi</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg">
                <div class="text-gray-400 text-sm">Batch Size</div>
                <div class="text-xl font-bold text-green-400">{config.get('batch_size')}</div>
            </div>
            <div class="bg-gray-800 p-4 rounded-lg">
                <div class="text-gray-400 text-sm">Epochs (Vòng Lặp)</div>
                <div class="text-xl font-bold text-pink-400">{config.get('epochs')} Cycles</div>
            </div>
        </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-7xl mx-auto mb-10">
        <!-- Accuracy Chart -->
        <div class="glass-panel p-6 shadow-2xl flex flex-col items-center">
            <h2 class="text-2xl font-bold text-white mb-4">Biểu Đồ Tiến Hoá: Accuracy</h2>
            <div class="w-full relative" style="height: 350px;">
                <canvas id="accChart"></canvas>
            </div>
        </div>
        
        <!-- Loss Chart -->
        <div class="glass-panel p-6 shadow-2xl flex flex-col items-center">
            <h2 class="text-2xl font-bold text-white mb-4">Biểu Đồ Chống Lỗi: Cấu Trúc Trọng Số (Loss)</h2>
            <div class="w-full relative" style="height: 350px;">
                <canvas id="lossChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Classification Reports -->
    <div class="max-w-5xl mx-auto">
        <h2 class="text-3xl font-bold text-white mb-6 border-l-4 border-indigo-500 pl-4">Kết Quả Kiểm Soát (Classification Reports)</h2>
        
        {render_cr_table(lstm_cr, "Baseline: Mô Hình LSTM 1 Chiều")}
        {render_cr_table(att_cr, "Sáng Kiến Đồ Án: Mô Hình BiLSTM Tích Hợp Self-Attention (Đề Nghị)")}
        
    </div>

    <footer class="mt-16 text-center text-gray-500 text-sm pb-8">
        Hệ thống được phát xuất tự động từ Pipeline Antigravity MLOps. 
    </footer>

    <!-- Script rendering the charts -->
    <script>
        const epochs = Array.from({{ length: {config.get('epochs', 10)} }}, (_, i) => "Epoch " + (i + 1));
        
        // Dữ liệu từ Python JSON
        const historyData = {json.dumps(history)};
        
        // ACCURACY CHART CONFIG
        const accCtx = document.getElementById('accChart').getContext('2d');
        new Chart(accCtx, {{
            type: 'line',
            data: {{
                labels: epochs,
                datasets: [
                    {{
                        label: 'Train Acc (BiLSTM+Attention)',
                        data: historyData.attention.accuracy,
                        borderColor: '#A78BFA',
                        backgroundColor: 'rgba(167, 139, 250, 0.1)',
                        borderWidth: 3,
                        tension: 0.3,
                        fill: false
                    }},
                    {{
                        label: 'Val Acc (BiLSTM+Attention)',
                        data: historyData.attention.val_accuracy,
                        borderColor: '#8B5CF6',
                        borderDash: [5, 5],
                        borderWidth: 3,
                        tension: 0.3
                    }},
                    {{
                        label: 'Train Acc (LSTM)',
                        data: historyData.lstm.accuracy,
                        borderColor: '#60A5FA',
                        backgroundColor: 'rgba(96, 165, 250, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false
                    }},
                    {{
                        label: 'Val Acc (LSTM)',
                        data: historyData.lstm.val_accuracy,
                        borderColor: '#3B82F6',
                        borderDash: [5, 5],
                        borderWidth: 2,
                        tension: 0.3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#c9d1d9' }} }}
                }},
                scales: {{
                    x: {{ ticks: {{ color: '#8b949e' }}, grid: {{ color: '#30363d' }} }},
                    y: {{ ticks: {{ color: '#8b949e' }}, grid: {{ color: '#30363d' }} }}
                }}
            }}
        }});
        
        // LOSS CHART CONFIG
        const lossCtx = document.getElementById('lossChart').getContext('2d');
        new Chart(lossCtx, {{
            type: 'line',
            data: {{
                labels: epochs,
                datasets: [
                    {{
                        label: 'Train Loss (BiLSTM+Attention)',
                        data: historyData.attention.loss,
                        borderColor: '#F87171',
                        borderWidth: 3,
                        tension: 0.3,
                        fill: false
                    }},
                    {{
                        label: 'Val Loss (BiLSTM+Attention)',
                        data: historyData.attention.val_loss,
                        borderColor: '#EF4444',
                        borderDash: [5, 5],
                        borderWidth: 3,
                        tension: 0.3
                    }},
                    {{
                        label: 'Train Loss (LSTM)',
                        data: historyData.lstm.loss,
                        borderColor: '#FBBF24',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false
                    }},
                    {{
                        label: 'Val Loss (LSTM)',
                        data: historyData.lstm.val_loss,
                        borderColor: '#F59E0B',
                        borderDash: [5, 5],
                        borderWidth: 2,
                        tension: 0.3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#c9d1d9' }} }}
                }},
                scales: {{
                    x: {{ ticks: {{ color: '#8b949e' }}, grid: {{ color: '#30363d' }} }},
                    y: {{ ticks: {{ color: '#8b949e' }}, grid: {{ color: '#30363d' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    with open(out_path_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n[REPORT] Báo cáo Hội Đồng đã được xuất tại: {out_path_html}")

if __name__ == "__main__":
    pass
