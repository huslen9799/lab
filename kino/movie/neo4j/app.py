from shutil import move
from flask import Flask, make_response, render_template, request, redirect, url_for, session, jsonify
from neo4j import Driver, GraphDatabase

from myneo4j import Neo4jConnection
import os
import bcrypt
# ----------------------------
# Flask setup
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')


app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 

# Static folders
MOVIE_IMG = os.path.join('static', 'movies')
PERSON_IMG = os.path.join('static', 'people')
os.makedirs(MOVIE_IMG, exist_ok=True)
os.makedirs(PERSON_IMG, exist_ok=True)
app.config['MOVIE_UPLOAD'] = MOVIE_IMG
app.config['PERSON_UPLOAD'] = PERSON_IMG

# ----------------------------
# Neo4j connection
# ----------------------------


class Neo4jConnection:
    def __init__(self, uri, user, pwd, database):
        self._driver = GraphDatabase.driver(uri, auth=(user, pwd))
        self.database = database  # ✅ Энэ нь таны database нэр

    def query(self, query, parameters=None, single=False):
        try:
            with self._driver.session(database=self.database) as session:
                result = session.run(query, parameters)
                return result.single() if single else list(result)
        except Exception as e:
            print("❌ Neo4j ERROR:", e)
            return []

# Neo4j-тай холбогдох
conn = Neo4jConnection(
    uri="neo4j://127.0.0.1:7687",
    user="neo4j",
    pwd="12345678",
    database="neo4j1"  # ✅ таны DB нэр
)
# ----------------------------
# Users
# ----------------------------
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'}
}

# ----------------------------
# Index page
# ----------------------------
@app.route("/", methods=['GET'])
def index():
    query_text = request.args.get('txtMovieTitle', '').strip()
    year_from = request.args.get('year_from', '').strip()
    year_to = request.args.get('year_to', '').strip()

    query = "MATCH (m:Movie) WHERE 1=1"

    # Нэрээр шүүх
    if query_text:
        safe_text = query_text.replace("'", "\\'")
        query += " AND toLower(m.title) CONTAINS toLower('{safe_text}')"

    # Он дээр шүүх
    if year_from.isdigit(): 
        query += " AND m.released >= {year_from}"
    if year_to.isdigit():
        query += " AND m.released <= {year_to}"

    query += " RETURN m.title AS title, m.released AS year, m.image AS image ORDER BY m.released DESC LIMIT 50"

    movies = conn.query(query)

    return render_template(
        "index.html",
        movies=movies,
        query=query_text,
        year_from=year_from,
        year_to=year_to,
        role=session.get('role', 'guest')
    )


# ----------------------------
# Login / Logout / Register
# Admin хэрэглэгчийн мэдээлэл

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # 1️⃣ Admin USERS dict-аас шалгах
        user_info = USERS.get(username)
        if user_info and isinstance(user_info, dict):
            if user_info.get('password') == password:
                session["username"] = username
                session["role"] = user_info.get('role', 'admin')
                return redirect(url_for('index'))
            else:
                error = "Нууц үг буруу байна!"
        else:
            # 2️⃣ Neo4j-аас бусад хэрэглэгч шалгах
            query = """
                MATCH (u:User {{username: '{username.replace("'", "\\'")}'}})
                RETURN u.password AS password, u.role AS role
            """
            result = conn.query(query)

            if not result:
                error = "Хэрэглэгч олдсонгүй!"
            else:
                stored_pw = result[0].get('password')
                user_role = result[0].get('role', 'member')

                if stored_pw == password:
                    session["username"] = username
                    session["role"] = user_role
                    return redirect(url_for('index'))
                else:
                    error = "Нууц үг буруу байна!"

    return render_template("login.html", error=error)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        confirm = request.form.get('confirm').strip()

        if password != confirm:
            return render_template("register.html", error="Нууц үг таарахгүй!")

        # Давхар хэрэглэгч байгаа эсэх
        check = conn.query("""
            MATCH (u:User {{username: '{username.replace("'", "\\'")}'}})
            RETURN u
        """)

        if check:
            return render_template("register.html", error="Хэрэглэгчийн нэр давхцаж байна!")

        # Хэрэглэгч үүсгэх (default role = member)
        conn.query("""
            CREATE (u:User {{
                username:'{username.replace("'", "\\'")}', 
                password:'{password.replace("'", "\\'")}',
                role:'member'
            }})
        """)

        # Session
        session['username'] = username
        session['role'] = "member"
        return redirect(url_for('index'))

    return render_template("register.html", error=error)

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    error = None
    success = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()

        user = conn.query("""
            MATCH (u:User {{username:'{username.replace("'", "\\'")}'}})
            RETURN u
        """)

        if not user:
            error = "Ийм хэрэглэгч байхгүй!"
        else:
            # Reset page рүү шилжих
            return redirect(url_for("reset_password_direct", username=username))

    # ❗ Хамгийн чухал — GET үед HTML буцаах!!
    return render_template("forgot_password.html", error=error, success=success)


@app.route("/reset/<username>", methods=["GET", "POST"])
def reset_password_direct(username):
    error = None
    success = None

    if request.method == "POST":
        new_password = request.form.get("new_password").strip()
        confirm = request.form.get("confirm").strip()

        if new_password != confirm:
            error = "Нууц үг таарахгүй байна!"
        else:
            conn.query("""
                MATCH (u:User {{username:'{username.replace("'", "\\'")}'}})
                SET u.password = '{new_password.replace("'", "\\'")}'
            """)
            success = "Нууц үг амжилттай солигдлоо!"

    return render_template("reset_password_direct.html", username=username, error=error, success=success)




# ----------------------------
# Movie detail + Reviews
# ----------------------------
def format_person_list(person_list, default_image="default.jpg", include_alias=False):
    formatted = []
    for p in person_list:
        person_dict = {
            "name": p.get("name") or "Мэдээлэлгүй",
            "image": p.get("image") or default_image
        }
        if include_alias:
            person_dict["alias"] = p.get("alias") or []
        return formatted.append(person_dict)
    return formatted

@app.route("/movie/<path:title>")
def movie_detail(title):
    conn = Neo4jConnection(
        uri="neo4j://127.0.0.1:7687",
        user="neo4j",
        pwd="12345678",
        database="neo4j1"
    )

    # Кино мэдээлэл ба баг
    query = """
    MATCH (m:Movie {title:$title})
    OPTIONAL MATCH (a:Person)-[r:ACTED_IN]->(m)
    OPTIONAL MATCH (d:Person)-[:DIRECTED]->(m)
    OPTIONAL MATCH (w:Person)-[:WROTE]->(m)
    OPTIONAL MATCH (p:Person)-[:PRODUCED]->(m)
    RETURN m.title AS title,
           m.released AS year,
           m.image AS image,
           collect(DISTINCT {name:a.name, image:a.image, alias:r.alias}) AS actors,
           collect(DISTINCT {name:d.name, image:d.image}) AS directors,
           collect(DISTINCT {name:w.name, image:w.image}) AS writers,
           collect(DISTINCT {name:p.name, image:p.image}) AS producers
    """
    records = conn.query(query, {"title": title})
    if not records:
        return "Кино олдсонгүй", 404

    r = records[0]
    movie = {
        "title": r.get("title"),
        "released": r.get("year"),
        "image": r.get("image") or "default.jpg",
        "actors": r.get("actors") or [],
        "directors": r.get("directors") or [],
        "writers": r.get("writers") or [],
        "producers": r.get("producers") or []
    }

    # Reviews-г авч дундаж үнэлгээ тооцох
    reviews = conn.query("""
        MATCH (u:User)-[r:REVIEWED]->(m:Movie {title:$title})
        RETURN u.username AS username, r.rating AS rating, r.summary AS summary
    """, {"title": title})

    review_list = [dict(x) for x in reviews] if reviews else []
    movie["reviews"] = review_list

    # Дундаж үнэлгээ
    if review_list:
        movie["avg_rating"] = round(sum(r["rating"] for r in review_list) / len(review_list), 1)
    else:
        movie["avg_rating"] = 0

    return render_template("movie_detail.html", movie=movie)




# Flask app.py дотор
def get_movie_actors(title):
    query = """
    MATCH (p:Person)-[r:ACTED_IN]->(m:Movie {title:$title})
    RETURN p.name AS name, p.image AS image, r.alias AS alias
    """
    records = conn.query(query)
    if not records:  # records нь None эсвэл хоосон бол хоосон list буцаана
        return []
    return [
        {"name": r["name"], "image": r["image"], "alias": r["alias"]}
        for r in records
    ]


def get_movie_directors(title):
    query = """
    MATCH (p:Person)-[:DIRECTED]->(m:Movie {title:$title})
    RETURN p.name AS name, p.image AS image
    """
    records = conn.query(query, {"title": title})
    return [{"name": r["name"], "image": r["image"]} for r in records]

def get_movie_writers(title):
    query = """
    MATCH (p:Person)-[:WROTE]->(m:Movie {title:$title})
    RETURN p.name AS name, p.image AS image
    """
    records = conn.query(query, {"title": title})
    return [{"name": r["name"], "image": r["image"]} for r in records]

def get_movie_info(title):
    query = """
    MATCH (m:Movie {title:$title})
    OPTIONAL MATCH (a:Person)-[r:ACTED_IN]->(m)
    OPTIONAL MATCH (d:Person)-[dr:DIRECTED]->(m)
    OPTIONAL MATCH (w:Person)-[wr:WROTE]->(m)
    OPTIONAL MATCH (p:Person)-[pr:PRODUCED]->(m)
    RETURN m.title AS title, m.year AS year, m.image AS image, m.avg_rating AS avg_rating,
           collect(DISTINCT {name:a.name, image:a.image, alias:r.alias}) AS actors,
           collect(DISTINCT {name:d.name, image:d.image}) AS directors,
           collect(DISTINCT {name:w.name, image:w.image}) AS writers,
           collect(DISTINCT {name:p.name, image:p.image}) AS producers
    """
    records = conn.query(query, {"title": title})
    if not records:
        return None
    record = records[0]
    return {
        "title": record["title"],
        "year": record["year"],
        "image": record["image"],
        "avg_rating": record["avg_rating"],
        "actors": record["actors"],      # alias энд байна
        "directors": record["directors"],
        "writers": record["writers"],
        "producers": record["producers"]
    }



@app.route("/admin/search_person")
def search_person():
    if session.get("role") != "admin":
        return jsonify([])

    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    q_safe = q.replace("'", "\\'")

    query = f"""
    MATCH (p:Person)
    WHERE toLower(p.name) CONTAINS toLower('{q_safe}')
    RETURN p.name AS name
    LIMIT 10
    """

    result = conn.query(query)

    people = [{"name": r["name"]} for r in result] if result else []
    return jsonify(people)

@app.route("/add_member_quick", methods=["POST"])
def add_member_quick():
    person_name = request.form.get("person", "").strip()
    role = request.form.get("role", "").strip()
    movie_title = request.form.get("movie_title", "").strip()
    alias_input = request.form.get("alias", "").strip()

    if not person_name or not role or not movie_title:
        return jsonify({"success": False, "message": "Бүх талбарыг бөглөх шаардлагатай."})

    # Alias-г list болгох
    alias_list = []
    if role == "ACTED_IN":
        if alias_input:
            alias_list = [a.strip() for a in alias_input.split(",") if a.strip()]
        if not alias_list:
            alias_list = [person_name]

    try:
        query = """
        MERGE (p:Person {{name:$person_name}})
        MERGE (m:Movie {{title:$movie_title}})
        MERGE (p)-[r:{role}]->(m)
        SET r.alias = $alias_list
        """
        conn.query(query, {"person_name": person_name, "movie_title": movie_title, "alias_list": alias_list})

        return jsonify({"success": True, "message": "{person_name} кино багт амжилттай нэмэгдлээ.", "alias": alias_list})
    except Exception as e:
        return jsonify({"success": False, "message": "Алдаа гарлаа: {str(e)}"})

def add_person_to_movie(movie_title, person_name, role, alias_list=None):
    alias_list = alias_list or []
    query = """
    MERGE (p:Person {{name: $person_name}})
    MERGE (m:Movie {{title: $movie_title}})
    MERGE (p)-[r:{role}]->(m)
    SET r.alias = $alias_list
    """
    conn.query(query, {"person_name": person_name, "movie_title": movie_title, "alias_list": alias_list})

@app.route('/update_alias', methods=['POST'])
def update_alias():
    person = request.form.get('person')
    movie_title = request.form.get('movie_title')
    alias = request.form.get('alias')  # Жишээ: "ssas,as"

    try:
        # 🟢 Alias-г таслалаар салгаж жагсаалт болгох
        aliases = [a.strip() for a in alias.split(",") if a.strip()]

        # Хэрвээ alias хоосон байвал None утгаар нэг MERGE
        for single_alias in aliases or [None]:
            query = """
            MATCH (p:Person {name:$person})-[r:ACTED_IN]->(m:Movie {title:$movie})
            SET r.alias = $alias
            """
            conn.query(query, {"person": person, "movie": movie_title, "alias": single_alias})

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ----------------------------
# Add Review
# ----------------------------
@app.route("/movie/<title>/review", methods=['POST'])
def add_review(title):
    # Нэвтрээгүй хэрэглэгчийг хаах
    if 'username' not in session or session.get('role') == 'guest':
        return "Та нэвтэрсэн байх шаардлагатай!"

    # Формоос утгыг авна
    summary = request.form.get('summary', '').strip()
    try:
        rating = int(request.form.get('rating', 0))
    except ValueError:
        rating = 0

    username = session['username']

    # Neo4j query - параметр ашиглах
    query = """
    MERGE (u:User {username:$username})
    MERGE (m:Movie {title:$title})
    MERGE (u)-[r:REVIEWED]->(m)
    SET r.summary = $summary, r.rating = $rating
    """
    conn.query(query, {"username": username, "title": title, "summary": summary, "rating": rating})

    # Кино detail рүү буцах
    return redirect(url_for('movie_detail', title=title))


# ----------------------------
# Admin: Add Movie / Person / Movie Member
# ----------------------------
@app.route("/admin/movie/add", methods=['GET', 'POST'])
def add_movie():
    if session.get('role') != 'admin':
        return "Зөвшөөрөгдсөнгүй!", 403

    if request.method == 'POST':
        # Формоос авна
        title = request.form.get('title', '').strip()
        released = request.form.get('released', '0').strip()
        try:
            released = int(released)
        except ValueError:
            released = 0

        # Зураг хадгалах
        img_file = request.files.get('image')
        img_name = 'default.jpg'
        if img_file and img_file.filename:
            img_name = img_file.filename
            img_file.save(os.path.join(app.config['MOVIE_UPLOAD'], img_name))

        # Neo4j-д нэмэх (параметр ашиглах)
        query = """
        MERGE (m:Movie {title:$title})
        SET m.released = $released, m.image = $image
        """
        conn.query(query, {"title": title, "released": released, "image": img_name})

        return redirect(url_for('index'))

    return render_template("admin_add_movie.html")



@app.route("/admin/movie/<title>/add_member_full", methods=['GET', 'POST'])
def add_member_full(title):
    if session.get('role') != 'admin':
        return "Зөвшөөрөгдсөнгүй!", 403

    if request.method == 'POST':
        # Autocomplete-аас ирсэн POST
        person_name = request.form.get('person')
        role = request.form.get('role')
        query = """
        MATCH (m:Movie {{title: '{title}'}}), (p:Person {{name: '{person_name}'}})
        MERGE (p)-[:{role.upper()}]->(m)
        """
        conn.query(query)
        return redirect(url_for('movie_detail', title=title))

    # GET үед template харуулах
    people = conn.query("MATCH (p:Person) RETURN p.name AS name ORDER BY p.name")
    resp = make_response(render_template("admin_add_member_full.html", title=title, people=people))
    
    # Cache-control нэмэх
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp


 
@app.route("/admin/person/add", methods=['GET', 'POST'])
def add_person():
    if session.get('role') != 'admin':
        return "Зөвшөөрөгдсөнгүй!"
    
    if request.method == 'POST':
        name = request.form.get('name', '').replace("'", "\\'")
        image_file = request.files.get('image')
        image_name = image_file.filename if image_file else 'default.jpg'
        if image_file:
            image_file.save(os.path.join(app.config['PERSON_UPLOAD'], image_name))
        
        # MERGE ашиглаж ижил нэртэй хүн давхар үүсгэхээс сэргийлнэ
        query = """
        MERGE (p:Person {{name: '{name}'}})
        SET p.image = '{image_name}'
        """
        conn.query(query)
        return redirect(url_for('index'))
    
    return render_template("admin_add_person.html")

# Person detail
# ----------------------------
@app.route("/person/<name>")
def person_detail(name):
    query = """
        MATCH (p:Person {name: $name})
        OPTIONAL MATCH (p)-[:ACTED_IN]->(m1:Movie)
        OPTIONAL MATCH (p)-[:DIRECTED]->(m2:Movie)
        OPTIONAL MATCH (p)-[:WROTE]->(m3:Movie)
        OPTIONAL MATCH (p)-[:PRODUCED]->(m4:Movie)
        RETURN p,
            collect(DISTINCT m1) AS acted_movies,
            collect(DISTINCT m2) AS directed_movies,
            collect(DISTINCT m3) AS written_movies,
            collect(DISTINCT m4) AS produced_movies
    """

    result = conn.query(query, {"name": name})

    if not result:
        return "Хүн олдсонгүй", 404

    record = result[0]

    return render_template(
        "person_detail.html",
        person=record["p"],
        acted=record["acted_movies"],
        directed=record["directed_movies"],
        written=record["written_movies"],
        produced=record["produced_movies"],
        role=session.get("role", "guest")
    )


# ----------------------------
# People pages with filter (function нэг удаа тодорхойлсон)
# ----------------------------
def people_by_role(role, title):
    role_map = {
        "actor": "ACTED_IN",
        "director": "DIRECTED",
        "writer": "WROTE",
        "producer": "PRODUCED"
    }
    rel = role_map.get(role.lower())
    if not rel:
        return "Invalid role", 400

    name_filter = request.args.get("name", "").strip()
    born_from = request.args.get("born_from", "").strip()
    born_to = request.args.get("born_to", "").strip()

    query = f"MATCH (p:Person)-[:{rel}]->(m:Movie) WHERE 1=1"

    if name_filter:
        safe = name_filter.replace("'", "\\'")
        query += f" AND toLower(p.name) CONTAINS toLower('{safe}')"

    if born_from.isdigit():
        query += f" AND p.born >= {born_from}"
    if born_to.isdigit():
        query += f" AND p.born <= {born_to}"

    query += """
    RETURN p.name AS name, p.born AS born, p.image AS image,
           collect({title:m.title, year:m.released, image:m.image}) AS movies
    ORDER BY p.name
    LIMIT 50
    """

    people = [dict(p) for p in conn.query(query)]
    return render_template("people_list.html", people=people, title=title, role=session.get("role", "guest"))

@app.route("/admin/movie/<title>/add_member_full2", methods=['GET', 'POST'])
def add_member_full2(title):
    if session.get('role') != 'admin':
        return "Зөвшөөрөгдсөнгүй!"

    if request.method == 'POST':
        person_name = request.form.get('person')
        role = request.form.get('role')
        query = """
        MATCH (m:Movie {{title: '{title}'}}), (p:Person {{name: '{person_name}'}})
        MERGE (p)-[:{role.upper()}]->(m)
        """
        conn.query(query)
        return redirect(url_for('movie_detail', title=title))

    return render_template("admin_add_member_full2.html", title=title)







# ----------------------------
# Person movies by role
# ----------------------------
@app.route("/actors")
def actors():
    return people_by_role("actor", "Жүжигчид")

@app.route("/directors")
def directors():
    return people_by_role("director", "Найруулагч")

@app.route("/writers")
def writers():
    return people_by_role("writer", "Зохиолч")

@app.route("/producers")
def producers():
    return people_by_role("producer", "Продюсер")


# ----------------------------
# Admin: Edit Person
# ----------------------------
@app.route("/admin/person/<name>/edit", methods=['GET', 'POST'])
def edit_person(name):
    if session.get("role") != "admin":
        return "Access Denied", 403

    name_safe = name.replace("'", "\\'")

    # POST — update person info
    if request.method == 'POST':
        new_name = request.form.get("name").replace("'", "\\'")
        born = request.form.get("born", "0")
        role = request.form.get("role", "actor")
        img_file = request.files.get("image")

        # New image → save
        if img_file and img_file.filename:
            img_name = img_file.filename
            img_file.save(os.path.join(app.config['PERSON_UPLOAD'], img_name))
        else:
            # Keep old image
            old = conn.query("""
                MATCH (p:Person {{name:'{name_safe}'}})
                RETURN p.image AS image
            """)
            img_name = old[0]["image"] if old else "default.jpg"

        # Update Neo4j
        query = """
        MATCH (p:Person {{name:'{name_safe}'}})
        SET p.name='{new_name}', p.born={born}, p.role='{role}', p.image='{img_name}'
        """
        conn.query(query)

        return redirect(url_for("person_detail", name=new_name))

    # GET — load data
    result = conn.query("""
        MATCH (p:Person {{name:'{name_safe}'}})
        RETURN p.name AS name, p.born AS born, p.role AS role, p.image AS image
    """)

    if not result:
        return "Person not found", 404

    person = result[0]
    return render_template("admin_edit_person.html", person=person)

@app.route("/admin/person/<name>/delete", methods=['POST'])
def delete_person(name):
    if session.get("role") != "admin":
        return "Access Denied", 403

    name_safe = name.replace("'", "\\'")
    conn.query("MATCH (p:Person {{name:'{name_safe}'}}) DETACH DELETE p")
    return redirect(url_for('index'))

# ----------------------------
# Reviewers
# ----------------------------
@app.route("/reviewers")
def reviewers():
    name_filter = request.args.get('name', '').strip()
    query = "MATCH (u:User)-[r:REVIEWED]->(m:Movie) RETURN u.username AS name, count(r) AS reviews ORDER BY u.username LIMIT 50"
    if name_filter:
        query = """
        MATCH (u:User)-[r:REVIEWED]->(m:Movie)
        WHERE toLower(u.username) CONTAINS toLower('{name_filter.replace('\'', '\\\'')}')
        RETURN u.username AS name, count(r) AS reviews ORDER BY u.username LIMIT 50
        """
    reviewers = conn.query(query)
    reviewers = [dict(r) if not isinstance(r, dict) else r for r in reviewers]
    return render_template("reviewers_list.html", reviewers=reviewers, role=session.get('role', 'guest'), title="Кино шүүмжлэгчид")
    # return render_template("actors.html", actors=actors)
    # return render_template("directors.html", directors=directors)
    # return render_template("writers.html", writers=writers)
    # return render_template("producers.html", producers=producers) 
# ----------------------------
# Admin: Delete Movie
# ----------------------------
@app.route('/admin/movie/<title>/delete', methods=['POST'])
def delete_movie(title):
    if session.get("role") != "admin":
        return {"success": False, "message": "Access Denied"}, 403

    try:
        conn.query(
            "MATCH (m:Movie {title:$title}) DETACH DELETE m",
            {"title": title}
        )
        return {"success": True, "message": f"'{title}' кино устгагдлаа."}
    except Exception as e:
        return {"success": False, "message": str(e)}





@app.route('/admin/movie/<title>/edit', methods=['GET', 'POST'])
def edit_movie(title):
    if session.get("role") != "admin":
        return "Access Denied", 403

    # ---------- POST ----------
    if request.method == "POST":
        new_title = request.form.get("title")
        released = int(request.form.get("released"))
        img_file = request.files.get("image")

        if img_file and img_file.filename:
            img_name = img_file.filename
            img_file.save(os.path.join(app.config['MOVIE_UPLOAD'], img_name))
        else:
            img_res = conn.query(
                "MATCH (m:Movie {title:$title}) RETURN m.image AS image",
                {"title": title}
            )
            img_name = img_res[0]["image"] if img_res else "default.jpg"

        conn.query(
            """
            MATCH (m:Movie {title:$old_title})
            SET m.title=$new_title,
                m.released=$released,
                m.image=$image
            """,
            {
                "old_title": title,
                "new_title": new_title,
                "released": released,
                "image": img_name
            }
        )

        return redirect(url_for("movie_detail", title=new_title))

    # ---------- GET ----------
    result = conn.query(
        """
        MATCH (m:Movie {title:$title})
        RETURN m.title AS title,
               m.released AS released,
               m.image AS image
        """,
        {"title": title}
    )

    if not result:
        return "Movie not found", 404

    movie = result[0]
    return render_template("admin_edit_movie.html", movie=movie)




# ----------------------------
# Run Flask
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
