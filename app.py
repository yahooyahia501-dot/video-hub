from flask import Flask, render_template_string, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Aggregator Hub</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #0f0f0f; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; }
        h2 { color: #ff4757; text-align: center; }
        form { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="text"] { flex: 1; padding: 12px; font-size: 16px; background: #222; border: 1px solid #444; color: #fff; border-radius: 8px; }
        button { padding: 12px 20px; font-size: 16px; background: #ff4757; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        button:hover { background: #ff6b81; }
        .results-list { list-style: none; padding: 0; }
        .video-card { background: #1a1a1a; margin-bottom: 15px; padding: 15px; border-radius: 8px; border: 1px solid #333; }
        .video-title { font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #f1f1f1; }
        .video-link { display: inline-block; padding: 8px 12px; background: #2ed573; color: #000; text-decoration: none; border-radius: 5px; font-size: 14px; font-weight: bold; }
        .video-link:hover { background: #7bed9f; }
    </style>
</head>
<body>
    <div class="container">
        <h2>منصة التجميع والأرشفة</h2>
        <form method="POST">
            <input type="text" name="query" placeholder="أدخل اسم المقطع أو الكلمة البحثية..." required>
            <button type="submit">بحث</button>
        </form>
        
        {% if results %}
            <h3>النتائج المتاحة (بالوقت والجودة الأصلية):</h3>
            <ul class="results-list">
                {% for item in results %}
                    <li class="video-card">
                        <div class="video-title">{{ item.title }}</div>
                        <a class="video-link" href="{{ item.url }}" target="_blank">مشاهدة المقطع الأصلي</a>
                    </li>
                {% endfor %}
            </ul>
        {% elif searched %}
            <p style="text-align: center; color: #aaa;">لم يتم العثور على نتائج مطابقة، جرب كلمات بحث أخرى.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    searched = False
    if request.method == "POST":
        searched = True
        query = request.form.get("query")
        formatted_query = query.replace(" ", "+")
        
        search_url = f"https://www.google.com/search?q={formatted_query}+site:spankbang.com"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for g in soup.find_all('div', class_='g'):
                    anchor = g.find('a')
                    if anchor and 'href' in anchor.attrs:
                        link = anchor['href']
                        title_elem = g.find('h3')
                        title = title_elem.text if title_elem else "مقطع مؤرشف"
                        if "spankbang" in link and "http" in link:
                            results.append({"title": title, "url": link})
        except Exception as e:
            pass

    return render_template_string(HTML_TEMPLATE, results=results, searched=searched)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
