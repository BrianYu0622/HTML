import os
from flask import Flask, request, redirect, url_for, session, render_template_string
from bs4 import BeautifulSoup  # 用於動態注入內容，免改原本的 HTML

app = Flask(__name__)
app.secret_key = 'magic_campus_secret_key_777'

# 預設的管理員密碼
ADMIN_PASSWORD = "password123"

# 後台管理的動態餐廳資料庫（初始資料）
restaurants = [
    {
        "id": 1,
        "name": "茶水間全日餐飲",
        "category": "breakfast lunch",
        "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500",
        "desc": "校門對面複合式早餐，三明治、鍋燒與日式炸物選擇多（後端動態載入）。",
        "link": "https://maps.google.com"
    },
    {
        "id": 2,
        "name": "Lazy Pasta 慵懶義式廚房",
        "category": "lunch",
        "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500",
        "desc": "義大利麵、燉飯與炸物輕食，適合同窗小聚的平價義式館（後端動態載入）。",
        "link": "https://maps.google.com"
    }
]

# ==================== 前台首頁：動態注入技術 ====================
@app.route('/')
def index():
    html_filename = 'campus-life-merged.html'
    
    # 1. 檢查原本的 HTML 檔案是否存在
    if not os.path.exists(html_filename):
        return f"<h3>錯誤：在同個資料夾下找不到 {html_filename} 檔案！請確認檔案位置。</h3>"
        
    # 2. 讀取你原本一字未改的 HTML 檔案
    with open(html_filename, 'r', encoding='utf-8') as f:
        raw_html = f.read()
        
    # 3. 使用 BeautifulSoup 解析網頁，找到餐廳容器標籤
    soup = BeautifulSoup(raw_html, 'html.parser')
    card_container = soup.find('div', class_='card-container')
    
    if card_container:
        # 4. 【核心魔法】清空原本網頁寫死的舊餐廳卡片
        card_container.clear()
        
        # 5. 根據後台現有的餐廳資料，即時組合出全新的 HTML 卡片
        dynamic_cards_html = ""
        for r in restaurants:
            dynamic_cards_html += f'''
            <a href="{r['link']}" target="_blank" class="card-link {r['category']}">
                <div class="card">
                    <div class="card-photo-wrap">
                        <img src="{r['image']}" class="card-multi-image" alt="{r['name']}">
                    </div>
                    <div class="card-info">
                        <h3>{r['name']}</h3>
                        <p>{r['desc']}</p>
                    </div>
                </div>
            </a>
            '''
        # 6. 把新組合好的動態卡片塞進原本的容器中
        new_cards_soup = BeautifulSoup(dynamic_cards_html, 'html.parser')
        card_container.append(new_cards_soup)
        
    # 7. 將魔法改造完畢的網頁直接傳送給瀏覽器
    return str(soup)


# ==================== 管理員登入頁面 ====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('admin'))
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = "密碼錯誤，請重新輸入！"
            
    return render_template_string('''
    <div style="max-width: 380px; margin: 100px auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); font-family: sans-serif; text-align: center; background: white;">
        <h2 style="color: #1d4ed8; margin-bottom: 20px;">校園指引管理系統</h2>
        {% if error %}<p style="color: #ef4444; font-size: 14px;">{{ error }}</p>{% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="請輸入管理密碼" style="width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box;" required>
            <button type="submit" style="width: 100%; padding: 10px; background: #1d4ed8; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px;">登入系統</button>
        </form>
    </div>
    ''', error=error)


# ==================== 后台管理面板 ====================
@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
        
    admin_ui = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>資料管理後台</title>
        <style>
            body { font-family: sans-serif; background: #f1f5f9; padding: 30px; color: #0f172a; }
            .container { max-width: 850px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
            h2, h3 { color: #1d4ed8; }
            .form-box { background: #f8fafc; padding: 20px; border-radius: 8px; margin-bottom: 30px; border: 1px solid #e2e8f0; }
            .form-group { margin-bottom: 12px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; font-size: 14px; }
            input, textarea { width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
            .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; color: white; font-weight: bold; text-decoration: none; }
            .btn-add { background: #10b981; }
            .btn-del { background: #ef4444; padding: 5px 10px; font-size: 13px; color: white; border:none; border-radius:4px; cursor:pointer;}
            .btn-logout { background: #64748b; float: right; text-decoration: none; padding: 8px 15px; font-size: 14px;}
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; border: 1px solid #e2e8f0; text-align: left; }
            th { background: #1d4ed8; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/logout" class="btn btn-logout">安全登出</a>
            <h2>校園生活指引 — 後台管理系統</h2>
            
            <div class="form-box">
                <h3>✨ 新增/上架新餐廳</h3>
                <form action="/admin/add" method="POST">
                    <div class="form-group">
                        <label>餐廳名稱</label>
                        <input type="text" name="name" required placeholder="例如：CoCo都可 興隆店">
                    </div>
                    <div class="form-group">
                        <label>分類標籤 (配合前端篩選按鈕，選多個請用空格隔開。例: breakfast lunch)</label>
                        <input type="text" name="category" required placeholder="可填項目：breakfast / lunch / drink">
                    </div>
                    <div class="form-group">
                        <label>圖片網址</label>
                        <input type="text" name="image" required placeholder="請貼上網頁圖片連結，或本地路徑如 images/xx.jpg">
                    </div>
                    <div class="form-group">
                        <label>餐廳簡介說明</label>
                        <textarea name="desc" rows="2" required placeholder="輸入這家餐廳的好吃特色..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>Google 地圖連結</label>
                        <input type="text" name="link" required placeholder="請貼上 Google Maps 分享連結">
                    </div>
                    <button type="submit" class="btn btn-add">加入並更新至前台</button>
                </form>
            </div>

            <h3>📋 目前運作中的餐廳清單</h3>
            <table>
                <tr>
                    <th>餐廳名稱</th>
                    <th>分類標籤</th>
                    <th>管理操作</th>
                </tr>
                {% for r in restaurants %}
                <tr>
                    <td><strong>{{ r.name }}</strong></td>
                    <td><code style="background:#e2e8f0; padding:2px 6px; border-radius:4px;">{{ r.category }}</code></td>
                    <td>
                        <form action="/admin/delete/{{ r.id }}" method="POST" style="display:inline;">
                            <button type="submit" class="btn btn-del" onclick="return confirm('確定要下架刪除「{{ r.name }}」嗎？')">下架刪除</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    '''
    return render_template_string(admin_ui, restaurants=restaurants)


# ==================== 後端動作 API ====================
@app.route('/admin/add', methods=['POST'])
def admin_add():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
        
    new_id = max([r['id'] for r in restaurants] + [0]) + 1
    new_restaurant = {
        "id": new_id,
        "name": request.form.get('name'),
        "category": request.form.get('category'),
        "image": request.form.get('image'),
        "desc": request.form.get('desc'),
        "link": request.form.get('link')
    }
    restaurants.append(new_restaurant)
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:res_id>', methods=['POST'])
def admin_delete(res_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
        
    global restaurants
    restaurants = [r for r in restaurants if r['id'] != res_id]
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("✨ 後端系統已啟動！")
    print("👉 觀看前台網頁結果：http://127.0.0.1:5000/")
    print("👉 登入管理員後台：http://127.0.0.1:5000/login  (密碼為 password123)")
    app.run(debug=True)