from flask import Flask, render_template, request, redirect, url_for, flash
from db import close_db
from dao.alban import AlbanDAO
from dao.zereg import ZeregDAO
from dao.tenhim import TenhimDAO
from dao.mergejil import MergejilDAO

app = Flask(__name__)
app.secret_key = "lab13-secret-key"
app.teardown_appcontext(close_db)

albanDao = AlbanDAO()
zeregDao = ZeregDAO()
tenhimDao = TenhimDAO()
mergejilDao = MergejilDAO()

@app.route("/")
def home():
    return render_template("home.html")

# ---------- ALBAN ----------
@app.route("/alban")
def alban_index():
    rows = albanDao.getRecords()
    return render_template("alban/index.html", rows=rows)

@app.route("/alban/add", methods=["GET", "POST"])
def alban_add():
    if request.method == "POST":
        name = request.form.get("name", "")
        if not name.strip():
            flash("Нэр хоосон байж болохгүй!")
            return redirect(url_for("alban_add"))
        albanDao.Add(name)
        return redirect(url_for("alban_index"))
    return render_template("alban/form.html", title="Албан тушаал нэмэх", row=None)

@app.route("/alban/edit/<int:id>", methods=["GET", "POST"])
def alban_edit(id):
    row = albanDao.getRecord(id)
    if not row:
        flash("Бичлэг олдсонгүй!")
        return redirect(url_for("alban_index"))
    if request.method == "POST":
        name = request.form.get("name", "")
        albanDao.Edit(id, name)
        return redirect(url_for("alban_index"))
    return render_template("alban/form.html", title="Албан тушаал засах", row=row)

@app.route("/alban/delete/<int:id>", methods=["POST"])
def alban_delete(id):
    albanDao.Delete(id)
    return redirect(url_for("alban_index"))

# ---------- ZEREG ----------
@app.route("/zereg")
def zereg_index():
    rows = zeregDao.getRecords()
    return render_template("zereg/index.html", rows=rows)

@app.route("/zereg/add", methods=["GET", "POST"])
def zereg_add():
    if request.method == "POST":
        name = request.form.get("name", "")
        if not name.strip():
            flash("Нэр хоосон байж болохгүй!")
            return redirect(url_for("zereg_add"))
        zeregDao.Add(name)
        return redirect(url_for("zereg_index"))
    return render_template("zereg/form.html", title="Эрдмийн зэрэг нэмэх", row=None)

@app.route("/zereg/edit/<int:id>", methods=["GET", "POST"])
def zereg_edit(id):
    row = zeregDao.getRecord(id)
    if not row:
        flash("Бичлэг олдсонгүй!")
        return redirect(url_for("zereg_index"))
    if request.method == "POST":
        name = request.form.get("name", "")
        zeregDao.Edit(id, name)
        return redirect(url_for("zereg_index"))
    return render_template("zereg/form.html", title="Эрдмийн зэрэг засах", row=row)

@app.route("/zereg/delete/<int:id>", methods=["POST"])
def zereg_delete(id):
    zeregDao.Delete(id)
    return redirect(url_for("zereg_index"))

# ---------- TENHIM ----------
@app.route("/tenhim")
def tenhim_index():
    rows = tenhimDao.getRecords()
    return render_template("tenhim/index.html", rows=rows)

@app.route("/tenhim/add", methods=["GET", "POST"])
def tenhim_add():
    if request.method == "POST":
        name = request.form.get("name", "")
        if not name.strip():
            flash("Нэр хоосон байж болохгүй!")
            return redirect(url_for("tenhim_add"))
        tenhimDao.Add(name)
        return redirect(url_for("tenhim_index"))
    return render_template("tenhim/form.html", title="Тэнхим нэмэх", row=None)

@app.route("/tenhim/edit/<int:id>", methods=["GET", "POST"])
def tenhim_edit(id):
    row = tenhimDao.getRecord(id)
    if not row:
        flash("Бичлэг олдсонгүй!")
        return redirect(url_for("tenhim_index"))
    if request.method == "POST":
        name = request.form.get("name", "")
        tenhimDao.Edit(id, name)
        return redirect(url_for("tenhim_index"))
    return render_template("tenhim/form.html", title="Тэнхим засах", row=row)

@app.route("/tenhim/delete/<int:id>", methods=["POST"])
def tenhim_delete(id):
    tenhimDao.Delete(id)
    return redirect(url_for("tenhim_index"))

# ---------- MERGEJIL ----------
@app.route("/mergejil")
def mergejil_index():
    rows = mergejilDao.getRecords()
    return render_template("mergejil/index.html", rows=rows)

@app.route("/mergejil/add", methods=["GET", "POST"])
def mergejil_add():
    if request.method == "POST":
        name = request.form.get("name", "")
        if not name.strip():
            flash("Нэр хоосон байж болохгүй!")
            return redirect(url_for("mergejil_add"))
        mergejilDao.Add(name)
        return redirect(url_for("mergejil_index"))
    return render_template("mergejil/form.html", title="Мэргэжил нэмэх", row=None)

@app.route("/mergejil/edit/<int:id>", methods=["GET", "POST"])
def mergejil_edit(id):
    row = mergejilDao.getRecord(id)
    if not row:
        flash("Бичлэг олдсонгүй!")
        return redirect(url_for("mergejil_index"))
    if request.method == "POST":
        name = request.form.get("name", "")
        mergejilDao.Edit(id, name)
        return redirect(url_for("mergejil_index"))
    return render_template("mergejil/form.html", title="Мэргэжил засах", row=row)

@app.route("/mergejil/delete/<int:id>", methods=["POST"])
def mergejil_delete(id):
    mergejilDao.Delete(id)
    return redirect(url_for("mergejil_index"))

if __name__ == "__main__":
    app.run(debug=True)
