from flask import Flask, request, jsonify, url_for, abort, redirect, make_response
from markupsafe import escape

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

def tinh_tb_xep_loai(scores):
    """Tính điểm TB và Xếp loại đơn giản"""
    if not scores:
        return "-", "Chưa có điểm"
    
    tb = round(sum(scores.values()) / len(scores), 2)
    if tb >= 8.5: xl = "Giỏi"
    elif tb >= 7.0: xl = "Khá"
    elif tb >= 5.0: xl = "Trung bình"
    else: xl = "Yếu"
    return tb, xl

# ----------------- ROUTE CHÍNH (QUẢN LÝ BẢNG ĐIỂM) -----------------

@app.route('/')
def home():
    tong_sv = len(STUDENTS)
    danh_sach_lop = list(set(s['lop'] for s in STUDENTS.values()))
    tong_so_lop = len(danh_sach_lop)
    
    return f"""
    <h2>Hệ thống Quản lý Bảng điểm Sinh viên</h2>
    <p>Tổng số sinh viên: <b>{tong_sv}</b></p>
    <p>Số lớp: <b>{tong_so_lop}</b> ({', '.join(danh_sach_lop)})</p>
    <ul>
        <li><a href="{url_for('students')}">Xem danh sách sinh viên (/students)</a></li>
        <li><a href="{url_for('search')}">Tìm kiếm sinh viên (/search)</a></li>
        <li><a href="{url_for('api_students')}">API dữ liệu JSON (/api/students)</a></li>
    </ul>
    <hr>
    <h4>Các route thực hành khác:</h4>
    <ul>
        <li><a href="/chia_nhom">/chia_nhom</a></li>
        <li><a href="/square/5">/square/5</a></li>
        <li><a href="/sum/1,2,3,4,5">/sum/1,2,3,4,5</a></li>
        <li><a href="/user/admin">/user/admin</a></li>
    </ul>
    """

@app.route('/students')
def students():
    lop_loc = request.args.get('lop', '').strip().upper() 
    cac_lop = sorted(list(set(s['lop'] for s in STUDENTS.values()))) 
    
    links = [f'<a href="/students">Tất cả</a>']
    for l in cac_lop:
        links.append(f'<a href="/students?lop={l}">{l}</a>')
    
    html = f"<h3>Danh sách sinh viên</h3><div>Thanh lọc theo lớp: {' | '.join(links)}</div><br>"
    
    rows = ""
    for mssv, s in STUDENTS.items():
        if not lop_loc or s['lop'].upper() == lop_loc:
            tb, xl = tinh_tb_xep_loai(s['scores'])
            rows += f"""
            <tr>
                <td><a href="/students/{mssv}">{mssv}</a></td>
                <td>{s['name']}</td>
                <td>{s['lop']}</td>
                <td>{tb}</td>
                <td>{xl}</td>
            </tr>
            """
    
    if rows:
        html += f"""
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>MSSV</th><th>Họ tên</th><th>Lớp</th><th>Điểm TB</th><th>Xếp loại</th></tr>
            {rows}
        </table>
        """
    else:
        html += "<p><b>Không có sinh viên phù hợp.</b></p>"
        
    html += '<br><a href="/">← Về trang chủ</a>'
    return html

@app.route('/students/<mssv>')
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    s = STUDENTS[mssv]
    tb, xl = tinh_tb_xep_loai(s['scores'])

    if s['scores']:
        rows = ""
        for mon, diem in s['scores'].items():
            rows += f"<tr><td>{mon}</td><td>{diem}</td></tr>"
        bang_diem = f"""
        <h4>Bảng điểm</h4>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>Học phần</th><th>Điểm</th></tr>
            {rows}
        </table>
        """
    else:
        bang_diem = "<p><i>Chưa có điểm học phần nào.</i></p>"

    html = f"""
    <h3>Chi tiết sinh viên</h3>
    <p><b>Họ tên:</b> {s['name']}</p>
    <p><b>MSSV:</b> {mssv}</p>
    <p><b>Điểm TB:</b> {tb}</p>
    <p><b>Xếp loại:</b> {xl}</p>
    <p><b>Lớp:</b> <a href="/students?lop={s['lop']}">{s['lop']}</a></p>
    {bang_diem}
    <p><a href="/students/{mssv}/export"><b>Tải bảng điểm (CSV)</b></a></p>
    <p><b>Link rút gọn:</b> <a href="/sv/{mssv}">/sv/{mssv}</a></p>
    <br>
    <a href="/students">← Quay lại danh sách</a> | <a href="/">Trang chủ</a>
    """
    return html

@app.route('/students/<mssv>/export')
def student_export(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    s = STUDENTS[mssv]

    csv_content = "hoc_phan,diem\n"
    for mon, diem in s['scores'].items():
        csv_content += f"{mon},{diem}\n"

    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=diem_{mssv}.csv'
    return response

@app.route('/sv/<mssv>')
def sv_redirect(mssv):
    return redirect(f"/students/{mssv}", code=301)

@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    safe_q = escape(q)

    html = f"""
    <h3>Tìm kiếm sinh viên</h3>
    <form method="GET" action="/search">
        <input type="text" name="q" value="{safe_q}" placeholder="Nhập từ khoá họ tên hoặc MSSV...">
        <button type="submit">Tìm kiếm</button>
    </form>
    <br>
    """

    if q:
        q_lower = q.lower()
        ket_qua = []
        for mssv, s in STUDENTS.items():
            if q_lower in s['name'].lower() or q_lower in mssv.lower():
                ket_qua.append((mssv, s))

        html += f"<p>Tìm thấy <b>{len(ket_qua)}</b> kết quả cho \"{safe_q}\"</p>"

        if ket_qua:
            html += "<ul>"
            for mssv, s in ket_qua:
                html += f'<li><a href="/students/{mssv}">{escape(s["name"])} ({mssv})</a></li>'
            html += "</ul>"

    html += '<br><a href="/">← Về trang chủ</a>'
    return html

@app.route('/api/students')
def api_students():
    return jsonify(STUDENTS)

# ----------------- ROUTE BÀI TẬP PHỤ -----------------

@app.route("/user/<username>")
def user_profile(username):
    return f"Trang cá nhân của {username}"

@app.route('/chia_nhom')
def chia_nhom():
    so_bai = 12
    so_nhom = 0
    if so_nhom > 0:
        return f"Mỗi nhóm làm {so_bai / so_nhom} bài"
    else:
        return "Không có nhóm nào để chia bài."

@app.route('/square/<int:number>')
def square(number):
    return f"Bình phương của {number} là {number ** 2}"

@app.route('/sum/<number>')
def total(number):
    try:
        num_list = [float(n.strip()) for n in number.split(',')]
        total_sum = sum(num_list)
        return f"Tổng của {num_list} là {total_sum}"
    except ValueError:
        return "404"

if __name__ == '__main__':
    app.run(debug=True, port=8000)