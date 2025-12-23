import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import Hicheel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)
app.secret_key = "lab16-secret"

TURUL_LIST = ["Суурь", "Мэргэжлийн", "Сонгон", "Ерөнхий", "Заавал"]

@app.get("/")
def home():
    return redirect(url_for("hiceel_list"))

@app.get("/hiceel")
def hiceel_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    q = request.args.get("q", "", type=str).strip()
    turul = request.args.get("turul", "", type=str).strip()

    sort = request.args.get("sort", "ner", type=str).strip()
    order = request.args.get("order", "asc", type=str).strip().lower()

    rows, total = Hicheel.getRecords(
        page=page, per_page=per_page, q=q, turul=turul, sort=sort, order=order
    )

    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "hiceel_list.html",
        rows=rows,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        q=q,
        turul=turul,
        sort=sort,
        order=order,
        turul_list=TURUL_LIST
    )

@app.route("/hiceel/add", methods=["GET", "POST"])
def hiceel_add():
    if request.method == "POST":
        data = {
            "code": request.form["code"].strip(),
            "ner": request.form["ner"].strip(),
            "credit": request.form["credit"],
            "umnuh_holboo": request.form.get("umnuh_holboo", "").strip(),
            "turul": request.form["turul"]
        }
        try:
            Hicheel.Add(data)
            flash("Хичээл амжилттай нэмэгдлээ ✅", "success")
            return redirect(url_for("hiceel_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")

    return render_template("hiceel_form.html", mode="add", row=None, turul_list=TURUL_LIST)

@app.route("/hiceel/edit/<int:id>", methods=["GET", "POST"])
def hiceel_edit(id: int):
    row = Hicheel.getRecord(id)
    if not row:
        flash("Мэдээлэл олдсонгүй", "warning")
        return redirect(url_for("hiceel_list"))

    if request.method == "POST":
        data = {
            "code": request.form["code"].strip(),
            "ner": request.form["ner"].strip(),
            "credit": request.form["credit"],
            "umnuh_holboo": request.form.get("umnuh_holboo", "").strip(),
            "turul": request.form["turul"]
        }
        try:
            Hicheel.Edit(id, data)
            flash("Хичээл амжилттай засагдлаа ✏️", "success")
            return redirect(url_for("hiceel_list"))
        except Exception as e:
            flash(f"Алдаа: {e}", "danger")

    return render_template("hiceel_form.html", mode="edit", row=row, turul_list=TURUL_LIST)

@app.get("/hiceel/delete/<int:id>")
def hiceel_delete(id: int):
    try:
        Hicheel.Delete(id)
        flash("Хичээл устгагдлаа 🗑️", "success")
    except Exception as e:
        flash(f"Алдаа: {e}", "danger")
    return redirect(url_for("hiceel_list"))

if __name__ == "__main__":
    app.run(debug=True)
