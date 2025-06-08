from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = 'expenses.db'

# 初始化資料庫
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                note TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# 首頁：顯示收支記錄與統計
@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM records ORDER BY timestamp DESC")
        records = c.fetchall()

        c.execute("SELECT SUM(amount) FROM records WHERE type='收入'")
        income = c.fetchone()[0] or 0

        c.execute("SELECT SUM(amount) FROM records WHERE type='支出'")
        expense = c.fetchone()[0] or 0

    return render_template('index.html', records=records, income=income, expense=expense)

# 新增頁面
@app.route('/add', methods=['GET', 'POST'])
def add():
    error = None
    if request.method == 'POST':
        try:
            amount_raw = request.form['amount']
            type_ = request.form['type']
            note = request.form['note']

            # 檢查金額是否為數字
            try:
                amount = float(amount_raw)
            except ValueError:
                raise ValueError("金額必須是數字")

            # 檢查類型是否有效
            if type_ not in ['收入', '支出']:
                raise ValueError("請選擇有效的類型")

            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO records (amount, type, note) VALUES (?, ?, ?)", (amount, type_, note))
                conn.commit()
            return redirect('/')
        except Exception as e:
            error = f"新增失敗：{str(e)}"

    return render_template('add.html', error=error)


# 主程式執行
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
