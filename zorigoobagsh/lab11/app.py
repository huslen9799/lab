from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db():
    db = sqlite3.connect("database.db")
    db.row_factory = sqlite3.Row
    return db


# -----------------------
#    HOME - Workers list
# -----------------------
@app.route("/")
def index():
    db = get_db()
    workers = db.execute("""
        SELECT Worker.id, Worker.wname, Branch.bname
        FROM Worker
        LEFT JOIN Branch ON Worker.bid = Branch.id
    """).fetchall()
    db.close()
    return render_template("index.html", workers=workers)


# -----------------------
#        WORKER CRUD
# -----------------------
@app.route("/add", methods=["GET", "POST"])
def add():
    db = get_db()

    if request.method == "POST":
        wname = request.form["wname"]
        bid = request.form.get("bid")  # << Fix for KeyError

        db.execute("INSERT INTO Worker (wname, bid) VALUES (?, ?)",
                   (wname, bid))
        db.commit()
        db.close()
        return redirect("/")

    branches = db.execute("SELECT * FROM Branch").fetchall()
    db.close()
    return render_template("worker_add.html", branches=branches)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    db = get_db()

    if request.method == "POST":
        wname = request.form["wname"]
        bid = request.form["bid"]

        db.execute("UPDATE Worker SET wname=?, bid=? WHERE id=?",
                   (wname, bid, id))
        db.commit()
        db.close()
        return redirect("/")

    worker = db.execute("SELECT * FROM Worker WHERE id=?", (id,)).fetchone()
    branches = db.execute("SELECT * FROM Branch").fetchall()

    db.close()
    return render_template("worker_edit.html", worker=worker, branches=branches)


@app.route("/delete/<int:id>")
def delete(id):
    db = get_db()
    db.execute("DELETE FROM Worker WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect("/")


# -----------------------
#        BRANCH CRUD
# -----------------------
@app.route("/branch")
def branch_list():
    db = get_db()
    branches = db.execute("SELECT * FROM Branch").fetchall()
    db.close()
    return render_template("branch_list.html", branches=branches)


@app.route("/branch/add", methods=["GET", "POST"])
def branch_add():
    if request.method == "POST":
        bname = request.form.get("bname")

        db = get_db()
        db.execute("INSERT INTO Branch (bname) VALUES (?)", (bname,))
        db.commit()
        db.close()
        return redirect("/branch")

    return render_template("branch_add.html")


@app.route("/branch/edit/<int:id>", methods=["GET", "POST"])
def branch_edit(id):
    db = get_db()

    if request.method == "POST":
        bname = request.form.get("bname")

        db.execute("UPDATE Branch SET bname=? WHERE id=?", (bname, id))
        db.commit()
        db.close()
        return redirect("/branch")

    branch = db.execute("SELECT * FROM Branch WHERE id=?", (id,)).fetchone()
    db.close()
    return render_template("branch_edit.html", branch=branch)


@app.route("/branch/delete/<int:id>")
def branch_delete(id):
    db = get_db()
    db.execute("DELETE FROM Branch WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect("/branch")


if __name__ == "__main__":
    app.run(debug=True)
