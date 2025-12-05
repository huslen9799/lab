from flask import Flask, render_template, request, redirect, url_for
from models import Branch, Worker

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('worker_list'))

@app.route('/worker')
def worker_list():
    workers = Worker.getRecords()
    return render_template('worker.html', workers=workers)

@app.route('/add', methods=['GET', 'POST'])
def add_worker():
    branches = Branch.getRecords()

    if request.method == 'POST':
        wname = request.form['wname']
        bid = request.form['bid']
        Worker.Add(wname, bid)
        return redirect(url_for('worker_list'))

    return render_template('add_worker.html', branches=branches)

if __name__ == '__main__':
    app.run(debug=True)
