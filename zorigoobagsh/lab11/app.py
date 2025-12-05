from flask import Flask, render_template, request, redirect, url_for
from models import Branch, Worker
import os
import sqlite3

app = Flask(__name__)
DB_FILE = "database.db"

# # Database үүсгэх (хэрвээ байхгүй бол)
# if not os.path.exists(DB_FILE):
#     conn = sqlite3.connect(DB_FILE)
#     conn.execute("""
#         CREATE TABLE Branch (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             bname TEXT NOT NULL
#         )
#     """)
#     conn.execute("""
#         CREATE TABLE Worker (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             wname TEXT NOT NULL,
#             bid INTEGER,
#             FOREIGN KEY(bid) REFERENCES Branch(id)
#         )
#     """)
#     # Жишээ өгөгдөл
#     conn.execute("INSERT INTO Branch (bname) VALUES (?)", ("Дархан",))
#     conn.execute("INSERT INTO Branch (bname) VALUES (?)", ("Салбар2",))
#     conn.execute("INSERT INTO Branch (bname) VALUES (?)", ("Салбар3",))
#     conn.execute("INSERT INTO Worker (wname, bid) VALUES (?, ?)", ("Бат", 1))
#     conn.execute("INSERT INTO Worker (wname, bid) VALUES (?, ?)", ("Сүхээ", 2))
#     conn.execute("INSERT INTO Worker (wname, bid) VALUES (?, ?)", ("Дулмаа", 3))
#     conn.commit()
#     conn.close()

# Home
@app.route("/")
def index():
    branches = Branch.all()
    workers = Worker.all()
    return render_template("index.html", branches=branches, workers=workers)

# Branch add
@app.route("/branch/add", methods=["GET", "POST"])
def branch_add():
    if request.method == "POST":
        bname = request.form["bname"]
        branch = Branch(bname=bname)
        branch.save()
        return redirect(url_for("index"))
    return render_template("branch_add.html")

# Branch edit
@app.route("/branch/edit/<int:id>", methods=["GET", "POST"])
def branch_edit(id):
    branch = Branch.get(id)
    if request.method == "POST":
        branch.bname = request.form["bname"]
        branch.save()
        return redirect(url_for("index"))
    return render_template("branch_edit.html", branch=branch)

# Branch delete
@app.route("/branch/delete/<int:id>")
def branch_delete(id):
    branch = Branch.get(id)
    if branch:
        branch.delete()
    return redirect(url_for("index"))

# Worker add
@app.route("/worker/add", methods=["GET", "POST"])
def worker_add():
    branches = Branch.all()
    if request.method == "POST":
        wname = request.form["wname"]
        bid = request.form.get("bid")
        worker = Worker(wname=wname, bid=bid)
        worker.save()
        return redirect(url_for("index"))
    return render_template("worker_add.html", branches=branches)

# Worker edit
@app.route("/worker/edit/<int:id>", methods=["GET", "POST"])
def worker_edit(id):
    worker = Worker.get(id)
    branches = Branch.all()
    if request.method == "POST":
        worker.wname = request.form["wname"]
        worker.bid = request.form.get("bid")
        worker.save()
        return redirect(url_for("index"))
    return render_template("worker_edit.html", worker=worker, branches=branches)

# Worker delete
@app.route("/worker/delete/<int:id>")
def worker_delete(id):
    worker = Worker.get(id)
    if worker:
        worker.delete()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
