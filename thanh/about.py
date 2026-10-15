from datetime import date
from flask import Flask, render_template, request

app = Flask(__name__)

# Danh sách bài viết mẫu (có thể mở rộng sau này)
POSTS = []

# Context processor: truyền biến toàn cục vào mọi template
@app.context_processor
def inject_globals():
    return {
        "site_name": "MiniBlog",
        "current_year": date.today().year,
        "post_count": len(POSTS),
    }

# Context processor: truyền hàm bổ trợ (helper function) vào mọi template
@app.context_processor
def inject_helpers():
    def is_active(endpoint):
        return ("active" if request.endpoint == endpoint else "")
    return {"is_active": is_active}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)