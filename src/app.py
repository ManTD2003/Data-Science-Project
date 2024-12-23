import webbrowser
from flask import Flask, render_template_string
import threading
import os

app = Flask(__name__)

data_files = [
    {"name": "Balo và vali", "image": "balo.jpg", "redirect_url": "http://localhost:5001"},
    {"name": "Điện gia dụng", "image": "diengiadung.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Điện tử & Điện lạnh", "image": "dientudienlanh.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Đồ chơi Mẹ & Bé", "image": "dochoimebe.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Đồng hồ & Trang sức", "image": "donghotrangsuc.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Giày dép Nam", "image": "giaydepnam.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Giày dép nữ", "image": "giaydepnu.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Bách hóa", "image": "groceries.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Hàng Quốc tế", "image": "hangquocte.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Chăm sóc nhà cửa", "image": "homecaring.jpg", "redirect_url": "http://localhost:5001"},
    {"name": "Điện thoại & Máy tính bảng", "image": "smartphone.jpg", "redirect_url": "http://localhost:8000"},
    {"name": "Sức khỏe & Làm đẹp", "image": "suckhoelamdep.jpg", "redirect_url": "http://localhost:8000"},
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --background-color: #f0f9ff;
            --text-color: #1e293b;
            --card-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.5;
        }

        .header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 2rem 1rem;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: var(--card-shadow);
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 1rem;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 1rem;
        }

        .card {
            background: white;
            border-radius: 1rem;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: var(--card-shadow);
            cursor: pointer;
            position: relative;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }

        .card-image {
            position: relative;
            padding-top: 75%;
            overflow: hidden;
        }

        .card-image img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }

        .card:hover .card-image img {
            transform: scale(1.1);
        }

        .card-content {
            padding: 1.5rem;
        }

        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 0.5rem;
        }

        .card-description {
            color: #64748b;
            font-size: 0.875rem;
            margin-bottom: 1rem;
        }

        .card-link {
            display: inline-flex;
            align-items: center;
            color: var(--primary-color);
            font-weight: 500;
            text-decoration: none;
            transition: color 0.2s ease;
        }

        .card-link:hover {
            color: var(--secondary-color);
        }

        .card-link i {
            margin-left: 0.5rem;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }

            .grid {
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1rem;
            }

            .card-content {
                padding: 1rem;
            }
        }

        .search-container {
            max-width: 600px;
            margin: 0 auto 2rem auto;
            padding: 0 1rem;
        }

        .search-box {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 0.5rem;
            font-size: 1rem;
            transition: border-color 0.2s ease;
        }

        .search-box:focus {
            outline: none;
            border-color: var(--primary-color);
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>SELECT DATA CATEGORIES</h1>
        <p>Nhấn vào danh mục để chuyển tới biểu đồ phân tích tương ứng</p>
    </header>

    <div class="search-container">
        <input type="text" class="search-box" placeholder="Tìm kiếm danh mục..." id="searchInput" oninput="filterCards()">
    </div>

    <div class="container">
        <div class="grid">
            {% for file in data_files %}
            <div class="card" onclick="window.location.href='{{ file['redirect_url'] }}'" data-name="{{ file['name'].lower() }}">
                <div class="card-image">
                    <img src="/static/{{ file['image'] }}" alt="{{ file['name'] }}">
                </div>
                <div class="card-content">
                    <h2 class="card-title">{{ file['name'] }}</h2>
                    <p class="card-description">{{ file['description'] }}</p>
                    <span class="card-link">
                        Click to redirect <i class="fas fa-arrow-right"></i>
                    </span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        function filterCards() {
            const searchInput = document.getElementById('searchInput');
            const filter = searchInput.value.toLowerCase();
            const cards = document.getElementsByClassName('card');

            for (let card of cards) {
                const name = card.getAttribute('data-name');
                if (name.includes(filter)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            }
        }
    </script>
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
    # threading.Timer(1, open_browser).start()
    app.run(debug=True)