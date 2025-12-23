import os, uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models import AlbanTushaal, ErdmiinZereg, Tenhim, Bagsh, Oyutan

app = Flask(__name__)
app.secret_key = "full-crud-secret"

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(name: str) -> bool:
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def save_image(file_storage):
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError("Зураг зөвшөөрөгдөх төрөл биш (png/jpg/jpeg/gif/webp)")
    original = secure_filename(file_storage.filename)
    ext = original.rsplit(".", 1)[1].lower()
    new_name = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(UPLOAD_FOLDER, new_name))
    return new_name

def delete_image(filename: str):
    if not filename:
        return
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)

@app.get("/")
def home():
    return redirect(url_for("oyutan_list"))

# ---------- ALBAN ----------
@app.get("/alban")
def alban_list():
    return render_template("alban_list.html", rows=AlbanTushaal.getRecords())

@app.route("/alban/add", methods=["GET","POST"])
def alban_add():
    if request.method == "POST":
        try:
            AlbanTushaal.Add({"ner": request.form["ner"].strip()})
            flash("Албан тушаал нэмэгдлээ ✅", "success")
            return redirect(url_for("alban_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")
    return render_template("alban_form.html", mode="add", row=None)

@app.route("/alban/edit/<int:id>", methods=["GET","POST"])
def alban_edit(id: int):
    row = AlbanTushaal.getRecord(id)
    if not row:
        flash("Мэдээлэл олдсонгүй", "warning")
        return redirect(url_for("alban_list"))
    if request.method == "POST":
        try:
            AlbanTushaal.Edit(id, {"ner": request.form["ner"].strip()})
            flash("Албан тушаал засагдлаа ✏️", "success")
            return redirect(url_for("alban_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")
    return render_template("alban_form.html", mode="edit", row=row)

@app.get("/alban/delete/<int:id>")
def alban_delete(id: int):
    try:
        AlbanTushaal.Delete(id)
        flash("Албан тушаал устгагдлаа 🗑️", "success")
    except Exception as e:
        flash(f"Алдаа: {e}", "danger")
    return redirect(url_for("alban_list"))

# ---------- ZEREG ----------
@app.get("/zereg")
def zereg_list():
    return render_template("zereg_list.html", rows=ErdmiinZereg.getRecords())

@app.route("/zereg/add", methods=["GET","POST"])
def zereg_add():
    if request.method == "POST":
        try:
            ErdmiinZereg.Add({"ner": request.form["ner"].strip()})
            flash("Эрдмийн зэрэг нэмэгдлээ ✅", "success")
            return redirect(url_for("zereg_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")
    return render_template("zereg_form.html", mode="add", row=None)

@app.route("/zereg/edit/<int:id>", methods=["GET","POST"])
def zereg_edit(id: int):
    row = ErdmiinZereg.getRecord(id)
    if not row:
        flash("Мэдээлэл олдсонгүй", "warning")
        return redirect(url_for("zereg_list"))
    if request.method == "POST":
        try:
            ErdmiinZereg.Edit(id, {"ner": request.form["ner"].strip()})
            flash("Эрдмийн зэрэг засагдлаа ✏️", "success")
            return redirect(url_for("zereg_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")
    return render_template("zereg_form.html", mode="edit", row=row)

@app.get("/zereg/delete/<int:id>")
def zereg_delete(id: int):
    try:
        ErdmiinZereg.Delete(id)
        flash("Эрдмийн зэрэг устгагдлаа 🗑️", "success")
    except Exception as e:
        flash(f"Алдаа: {e}", "danger")
    return redirect(url_for("zereg_list"))

# ---------- TENHIM ----------
@app.get("/tenhim")
def tenhim_list():
    return render_template("tenhim_list.html", rows=Tenhim.getRecords())

@app.route("/tenhim/add", methods=["GET","POST"])
def tenhim_add():
    if request.method == "POST":
        try:
            Tenhim.Add({"ner": request.form["ner"].strip()})
            flash("Тэнхим нэмэгдлээ ✅", "success")
            return redirect(url_for("tenhim_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")
    return render_template("tenhim_form.html", mode="add", row=None)

@app.route("/tenhim/edit/<int:id>", methods=["GET","POST"])
def tenhim_edit(id: int):
    row = Tenhim.getRecord(id)
    if not row:
        flash("Мэдээлэл олдсонгүй", "warning")
        return redirect(url_for("tenhim_list"))
    if request.method == "POST":
        try:
            Tenhim.Edit(id, {"ner": request.form["ner"].strip()})
            flash("Тэнхим засагдлаа ✏️", "success")
            return redirect(url_for("tenhim_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")
    return render_template("tenhim_form.html", mode="edit", row=row)

@app.get("/tenhim/delete/<int:id>")
def tenhim_delete(id: int):
    try:
        Tenhim.Delete(id)
        flash("Тэнхим устгагдлаа 🗑️", "success")
    except Exception as e:
        flash(f"Алдаа: {e}", "danger")
    return redirect(url_for("tenhim_list"))

# ---------- BAGSH ----------
@app.get("/bagsh")
def bagsh_list():
    return render_template("bagsh_list.html", rows=Bagsh.getRecords())

@app.route("/bagsh/add", methods=["GET","POST"])
def bagsh_add():
    tenhim = Tenhim.getRecords()
    alban = AlbanTushaal.getRecords()
    zereg = ErdmiinZereg.getRecords()

    if request.method == "POST":
        data = {
            "code": request.form["code"].strip(),
            "ovog": request.form["ovog"].strip(),
            "ner": request.form["ner"].strip(),
            "huis": request.form.get("huis", "Эр"),
            "ajild_orson": request.form["ajild_orson"],
            "tenhim_id": int(request.form["tenhim_id"]),
            "alban_tushaal_id": int(request.form["alban_tushaal_id"]),
            "erdmiin_zereg_id": int(request.form["erdmiin_zereg_id"]),
        }
        try:
            Bagsh.Add(data)
            flash("Багш нэмэгдлээ ✅", "success")
            return redirect(url_for("bagsh_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")

    return render_template("bagsh_form.html", mode="add", row=None,
                           tenhim=tenhim, alban=alban, zereg=zereg)

@app.route("/bagsh/edit/<int:id>", methods=["GET","POST"])
def bagsh_edit(id: int):
    row = Bagsh.getRecord(id)
    if not row:
        flash("Мэдээлэл олдсонгүй", "warning")
        return redirect(url_for("bagsh_list"))

    tenhim = Tenhim.getRecords()
    alban = AlbanTushaal.getRecords()
    zereg = ErdmiinZereg.getRecords()

    if request.method == "POST":
        data = {
            "code": request.form["code"].strip(),
            "ovog": request.form["ovog"].strip(),
            "ner": request.form["ner"].strip(),
            "huis": request.form.get("huis", "Эр"),
            "ajild_orson": request.form["ajild_orson"],
            "tenhim_id": int(request.form["tenhim_id"]),
            "alban_tushaal_id": int(request.form["alban_tushaal_id"]),
            "erdmiin_zereg_id": int(request.form["erdmiin_zereg_id"]),
        }
        try:
            Bagsh.Edit(id, data)
            flash("Багш засагдлаа ✏️", "success")
            return redirect(url_for("bagsh_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")

    return render_template("bagsh_form.html", mode="edit", row=row,
                           tenhim=tenhim, alban=alban, zereg=zereg)

@app.get("/bagsh/delete/<int:id>")
def bagsh_delete(id: int):
    try:
        Bagsh.Delete(id)
        flash("Багш устгагдлаа 🗑️", "success")
    except Exception as e:
        flash(f"Алдаа: {e}", "danger")
    return redirect(url_for("bagsh_list"))

# ---------- OYUTAN (зурагтай) ----------
@app.get("/oyutan")
def oyutan_list():
    return render_template("oyutan_list.html", rows=Oyutan.getRecords())

@app.route("/oyutan/add", methods=["GET","POST"])
def oyutan_add():
    tenhim = Tenhim.getRecords()
    if request.method == "POST":
        data = {
            "code": request.form["code"].strip(),
            "ovog": request.form["ovog"].strip(),
            "ner": request.form["ner"].strip(),
            "huis": request.form.get("huis", "Эр"),
            "elselt_ognoo": request.form["elselt_ognoo"],
            "tenhim_id": int(request.form["tenhim_id"]),
            "zurag": None
        }
        try:
            img = save_image(request.files.get("zurag"))
            data["zurag"] = img
            Oyutan.Add(data)
            flash("Оюутан нэмэгдлээ ✅", "success")
            return redirect(url_for("oyutan_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")

    return render_template("oyutan_form.html", mode="add", row=None, tenhim=tenhim)

@app.route("/oyutan/edit/<int:id>", methods=["GET","POST"])
def oyutan_edit(id: int):
    row = Oyutan.getRecord(id)
    if not row:
        flash("Мэдээлэл олдсонгүй", "warning")
        return redirect(url_for("oyutan_list"))

    tenhim = Tenhim.getRecords()

    if request.method == "POST":
        data = {
            "code": request.form["code"].strip(),
            "ovog": request.form["ovog"].strip(),
            "ner": request.form["ner"].strip(),
            "huis": request.form.get("huis", "Эр"),
            "elselt_ognoo": request.form["elselt_ognoo"],
            "tenhim_id": int(request.form["tenhim_id"]),
            "zurag": row.get("zurag")
        }
        try:
            new_img = request.files.get("zurag")
            if new_img and new_img.filename:
                saved = save_image(new_img)
                delete_image(row.get("zurag"))
                data["zurag"] = saved

            Oyutan.Edit(id, data)
            flash("Оюутан засагдлаа ✏️", "success")
            return redirect(url_for("oyutan_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")

    return render_template("oyutan_form.html", mode="edit", row=row, tenhim=tenhim)

@app.get("/oyutan/delete/<int:id>")
def oyutan_delete(id: int):
    row = Oyutan.getRecord(id)
    if not row:
        flash("Мэдээлэл олдсонгүй", "warning")
        return redirect(url_for("oyutan_list"))
    try:
        delete_image(row.get("zurag"))
        Oyutan.Delete(id)
        flash("Оюутан устгагдлаа 🗑️", "success")
    except Exception as e:
        flash(f"Алдаа: {e}", "danger")
    return redirect(url_for("oyutan_list"))

if __name__ == "__main__":
    app.run(debug=True)