from flask import Flask, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('Employee.db')
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/')
def home():
    return redirect(url_for('worker_list'))


@app.route('/worker')
def worker_list():
    conn = get_db_connection()
    workers = conn.execute('''
        SELECT w.wid, w.wname, b.bname
        FROM Worker w
        LEFT JOIN Branch b ON w.bid = b.id
    ''').fetchall()
    conn.close()
    return render_template('worker.html', workers=workers)


if __name__ == '__main__':
    app.run(debug=True)
