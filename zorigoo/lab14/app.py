from flask import Flask, render_template, request, redirect, url_for, flash
from models import Bagsh, Oyutan

app = Flask(__name__)
app.secret_key = "lab14-secret"

TENHIM_LIST = [
    "Компьютерийн ухааны тэнхим",
    "Мэдээллийн системийн тэнхим",
    "Гадаад хэлний тэнхим",
]

MERGEJIL_LIST = [
    "Програм хангамж",
    "Мэдээллийн систем",
    "Сүлжээ",
]

@app.get("/")
def home():
    return redirect(url_for("bagsh_list"))

# ---------------- BAGSH ----------------
@app.get("/bagsh")
def bagsh_list():
    return render_template("bagsh_list.html", rows=Bagsh.getRecords())

@app.route("/bagsh/add", methods=["GET", "POST"])
def bagsh_add():
    if request.method == "POST":
        data = {
            "code": request.form["code"].strip(),
            "ovog": request.form["ovog"].strip(),
            "ner": request.form["ner"].strip(),
            "huis": request.form.get("huis", "Эр"),
            "ajild_orson": request.form["ajild_orson"],
            "tenhim": request.form["tenhim"],
        }
        try:
            Bagsh.Add(data)
            flash("Багш амжилттай хадгалагдлаа ✅", "success")
            return redirect(url_for("bagsh_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")

    return render_template("bagsh_form.html", mode="add", tenhim_list=TENHIM_LIST, row=None)

@app.route("/bagsh/edit/<int:id>", methods=["GET", "POST"])
def bagsh_edit(id: int):
    row = Bagsh.getRecord(id)
    if not row:
        flash("Мэдээлэл олдсонгүй", "warning")
        return redirect(url_for("bagsh_list"))

    if request.method == "POST":
        data = {
            "code": request.form["code"].strip(),
            "ovog": request.form["ovog"].strip(),
            "ner": request.form["ner"].strip(),
            "huis": request.form.get("huis", "Эр"),
            "ajild_orson": request.form["ajild_orson"],
            "tenhim": request.form["tenhim"],
        }
        try:
            Bagsh.Edit(id, data)
            flash("Багш амжилттай засагдлаа ✏️", "success")
            return redirect(url_for("bagsh_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")

    return render_template("bagsh_form.html", mode="edit", tenhim_list=TENHIM_LIST, row=row)

@app.get("/bagsh/delete/<int:id>")
def bagsh_delete(id: int):
    try:
        Bagsh.Delete(id)
        flash("Багш устгагдлаа 🗑️", "success")
    except Exception as e:
        flash(f"Алдаа: {e}", "danger")
    return redirect(url_for("bagsh_list"))

# ---------------- OYUTAN ----------------
@app.get("/oyutan")
def oyutan_list():
    return render_template("oyutan_list.html", rows=Oyutan.getRecords())

@app.route("/oyutan/add", methods=["GET", "POST"])
def oyutan_add():
    if request.method == "POST":
        data = {
            "code": request.form["code"].strip(),
            "ovog": request.form["ovog"].strip(),
            "ner": request.form["ner"].strip(),
            "huis": request.form.get("huis", "Эр"),
            "elselt_ognoo": request.form["elselt_ognoo"],
            "mergejil": request.form["mergejil"],
        }
        try:
            Oyutan.Add(data)
            flash("Оюутан амжилттай хадгалагдлаа ✅", "success")
            return redirect(url_for("oyutan_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")

    return render_template("oyutan_form.html", mode="add", mergejil_list=MERGEJIL_LIST, row=None)

@app.route("/oyutan/edit/<int:id>", methods=["GET", "POST"])
def oyutan_edit(id: int):
    row = Oyutan.getRecord(id)
    if not row:
        flash("Мэдээлэл олдсонгүй", "warning")
        return redirect(url_for("oyutan_list"))

    if request.method == "POST":
        data = {
            "code": request.form["code"].strip(),
            "ovog": request.form["ovog"].strip(),
            "ner": request.form["ner"].strip(),
            "huis": request.form.get("huis", "Эр"),
            "elselt_ognoo": request.form["elselt_ognoo"],
            "mergejil": request.form["mergejil"],
        }
        try:
            Oyutan.Edit(id, data)
            flash("Оюутан амжилттай засагдлаа ✏️", "success")
            return redirect(url_for("oyutan_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")

    return render_template("oyutan_form.html", mode="edit", mergejil_list=MERGEJIL_LIST, row=row)

@app.get("/oyutan/delete/<int:id>")
def oyutan_delete(id: int):
    try:
        Oyutan.Delete(id)
        flash("Оюутан устгагдлаа 🗑️", "success")
    except Exception as e:
        flash(f"Алдаа: {e}", "danger")
    return redirect(url_for("oyutan_list"))

if __name__ == "__main__":
    app.run(debug=True)
