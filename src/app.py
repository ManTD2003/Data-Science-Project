import os
import webbrowser
import threading
import json
from io import BytesIO
import base64
from sentence_transformers import SentenceTransformer
from flask import Flask, render_template, request
from bertopic import BERTopic
import plotly.io as pio

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

# =========================
# 1) TRANG DANH MỤC
# =========================

data_files = [
    {
        "name": "Phụ kiện thời trang",
        "image": "donghotrangsuc.jpg",
        "redirect_url": "/analysis/phu-kien-thoi-trang"
    },
    {
        "name": "Điện thoại máy tính bảng",
        "image": "dochoimebe.jpg",
        "redirect_url": "/analysis/dien-thoai-may-tinh-bang"
    },
    {
        "name": "Laptop",
        "image": "hangquocte.jpg",
        "redirect_url": "/analysis/laptop-may-vi-tinh-linh-kien"
    },
    {
        "name": "thiết bị kts",
        "image": "dientudienlanh.jpg",
        "redirect_url": "/analysis/thiet-bi-kts-phu-kien-so"
    },
    {"name": "Balo và vali", "image": "balo.jpg", "redirect_url": ""},
    {"name": "Điện gia dụng", "image": "diengiadung.jpg", "redirect_url": ""},
    {"name": "Điện tử & Điện lạnh", "image": "dientudienlanh.jpg", "redirect_url": ""},
    {"name": "Đồ chơi Mẹ & Bé", "image": "dochoimebe.jpg", "redirect_url": ""},
    {"name": "Đồng hồ & Trang sức", "image": "donghotrangsuc.jpg", "redirect_url": ""},
    {"name": "Giày dép Nam", "image": "giaydepnam.jpg", "redirect_url": ""},
    {"name": "Giày dép nữ", "image": "giaydepnu.jpg", "redirect_url": ""},
    {"name": "Bách hóa", "image": "groceries.jpg", "redirect_url": ""},
    {"name": "Hàng Quốc tế", "image": "hangquocte.jpg", "redirect_url": ""},
    {"name": "Chăm sóc nhà cửa", "image": "homecaring.jpg", "redirect_url": ""},
    {"name": "Điện thoại & Máy tính bảng", "image": "smartphone.jpg", "redirect_url": ""},
    {"name": "Sức khỏe & Làm đẹp", "image": "suckhoelamdep.jpg", "redirect_url": ""},
]


@app.route("/")
def index_landing():
    """
    Trang chủ: hiển thị danh mục. 
    Mỗi mục link tới "/analysis/<model_name>" tuỳ cấu hình trong data_files.
    """
    return render_template("home.html", data_files=data_files)


# =========================
# 2) LOAD TẤT CẢ MODEL & BIỂU ĐỒ TRƯỚC (GLOBAL)
# =========================
models_cache = {}
chart_data_cache = {}

def load_all_models_and_charts(models_dir="models", eval_dir="eval"):
    """
    Duyệt folder models_dir, tìm các file mô hình (VD: model_a.pkl, model_b.pkl).
    Tương ứng, tìm file JSON trong eval_dir (VD: model_a.json).
    => Load model, tạo biểu đồ Plotly & matplotlib => Lưu cache.
    """
    if not os.path.isdir(models_dir):
        print(f"[WARN] Thư mục models_dir={models_dir} không tồn tại!")
        return

    for filename in os.listdir(models_dir):
        full_path = os.path.join(models_dir, filename)
        if not os.path.isfile(full_path):
            continue
        
        model_name, ext = os.path.splitext(filename)

        print(f"[INFO] Đang load mô hình: {filename}")
        model_obj = BERTopic.load(full_path)
        # cache_dir = 'cache'
        # model_obj.embedding_model =  SentenceTransformer('google-bert/bert-base-multilingual-cased', cache_folder=cache_dir, device='cpu')
        models_cache[model_name] = model_obj
        print(f"[INFO] Model '{model_name}' đã load xong.")

        json_path = os.path.join(eval_dir, model_name + ".json")
        if not os.path.exists(json_path):
            print(f"[WARN] Không tìm thấy file JSON: {json_path}")
            chart_data_cache[model_name] = {
                "topics_html": None,
                "barchart_html": None,
                "heatmap_html": None,
                "hierarchy_html": None,
                "evaluation_html": None
            }
            continue
        
        print(f"[INFO] Sinh biểu đồ cho '{model_name}'...")

        visualize_topics    = model_obj.visualize_topics()
        visualize_barchart  = model_obj.visualize_barchart(top_n_topics=10)
        visualize_heatmap   = model_obj.visualize_heatmap()
        visualize_hierarchy = model_obj.visualize_hierarchy()

        topics_html    = pio.to_html(visualize_topics,    full_html=False)
        barchart_html  = pio.to_html(visualize_barchart,  full_html=False)
        heatmap_html   = pio.to_html(visualize_heatmap,   full_html=False)
        hierarchy_html = pio.to_html(visualize_hierarchy, full_html=False)

        evaluation_html = generate_evaluation_charts(json_path)

        chart_data_cache[model_name] = {
            "topics_html": topics_html,
            "barchart_html": barchart_html,
            "heatmap_html": heatmap_html,
            "hierarchy_html": hierarchy_html,
            "evaluation_html": evaluation_html
        }
        print(f"[INFO] Hoàn thành chart cho '{model_name}'.")

def generate_evaluation_charts(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        results = json.load(f)

    nr_topics = [r['Params']['nr_topics'] for r in results]
    npmi_scores = [r['Scores']['npmi'] for r in results]
    diversity_scores = [r['Scores']['diversity'] for r in results]
    computation_times = [r['Computation Time'] for r in results]

    # Plot 1
    fig1, ax1 = plt.subplots(figsize=(12,6))
    ax1.plot(nr_topics, npmi_scores, marker='o', label='NPMI', color='blue')
    ax1.plot(nr_topics, diversity_scores, marker='s', label='Diversity', color='green')
    ax1.set_title('NPMI và Diversity vs Số lượng Topics')
    ax1.set_xlabel('Số lượng Topics')
    ax1.set_ylabel('Scores')
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.7, label='Baseline=0')
    ax1.legend()
    ax1.grid(alpha=0.3)
    plt.tight_layout()

    img1 = BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    chart1_url = base64.b64encode(img1.getvalue()).decode()
    plt.close(fig1)

    # Plot 2
    fig2, ax2 = plt.subplots(figsize=(8,5))
    ax2.bar(nr_topics, computation_times, color='orange', alpha=0.7)
    ax2.set_title('Thời gian tính toán vs Số lượng Topics')
    ax2.set_xlabel('Số lượng Topics')
    ax2.set_ylabel('Thời gian (s)')
    ax2.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    img2 = BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    chart2_url = base64.b64encode(img2.getvalue()).decode()
    plt.close(fig2)

    # Kết hợp HTML
    return f"""
    <div>
      <h3>NPMI và Diversity vs Số lượng Topics</h3>
      <img src="data:image/png;base64,{chart1_url}" />
    </div>
    <div>
      <h3>Thời gian tính toán vs Số lượng Topics</h3>
      <img src="data:image/png;base64,{chart2_url}" />
    </div>
    """


# =========================
# 3) ROUTE HIỂN THỊ BIỂU ĐỒ: /analysis/<model_name>
# =========================

@app.route("/analysis/<model_name>")
def analysis(model_name):
    """
    Trang hiển thị biểu đồ (Plotly + matplotlib) cho model_name.
    """
    if model_name not in chart_data_cache:
        return f"<h2>Không tìm thấy model: {model_name}</h2>", 404
    
    info = chart_data_cache[model_name]
    return render_template(
        "visualizations.html",
        topics_html    = info["topics_html"],
        barchart_html  = info["barchart_html"],
        heatmap_html   = info["heatmap_html"],
        hierarchy_html = info["hierarchy_html"],
        evaluation_html= info["evaluation_html"]
    )


# =========================
# 4) CHẠY APP
# =========================
def open_browser():
    """Tuỳ chọn: tự mở trình duyệt sau khi Flask start."""
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:5000")
        
print("[INFO] Đang load tất cả mô hình + biểu đồ. Vui lòng chờ...")
load_all_models_and_charts(models_dir="models", eval_dir="eval")
print("[INFO] Đã load xong tất cả mô hình + biểu đồ.")

if __name__ == "__main__":
    # threading.Timer(1, open_browser).start()
    app.run(debug=False, port=5000)
