import webbrowser
from flask import Flask, render_template_string
import threading
import os

app = Flask(__name__)

data_files = [
    {"name": "Balo và vali", "image": "balo.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Điện gia dụng", "image": "diengiadung.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Điện tử & Điện lạnh", "image": "dientudienlanh.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Đồ chơi Mẹ & Bé", "image": "dochoimebe.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Đồng hồ & Trang sức", "image": "donghotrangsuc.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Giày dép Nam", "image": "giaydepnam.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Giày dép nữ", "image": "giaydepnu.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Bách hóa", "image": "groceries.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Hàng Quốc tế", "image": "hangquocte.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Chăm sóc nhà cửa", "image": "homecaring.jpg", "redirect_url": "http://127.0.0.1:5000"},
    {"name": "Điện thoại & Máy tính bảng", "image": "smartphone.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Sức khỏe & Làm đẹp", "image": "suckhoelamdep.jpg", "redirect_url": "http://localhost:8000"},
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DS Project Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            text-align: center;
        }
        .container {
            display: grid;
            grid-template-columns: repeat(4, 1fr); 
            gap: 20px;
            padding: 20px;
            max-width: 1200px;
            margin: auto;
        }
        .item {
            position: relative;
            cursor: pointer;
            height: 250px;
            overflow: hidden;
            border-radius: 10px;
        }
        .item img {
            width: 100%;
            height: 100%;
            object-fit: cover; 
        }
        .item .title {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.5);
            color: white;
            font-weight: bold;
            text-align: center;
            padding: 10px;
            font-size: 16px;
        }
        h1 {
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>Select data categories</h1>
    <div class="container">
        {% for file in data_files %}
        <div class="item" onclick="window.location.href='{{ file['redirect_url'] }}'">
            <img src="/static/{{ file['image'] }}" alt="{{ file['name'] }}">
            <div class="title">{{ file['name'] }}</div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, data_files=data_files)

def open_browser():
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=True)
