from flask import Flask, render_template, request, redirect, url_for, session
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
conn = Neo4jConnection(uri="neo4j://127.0.0.1:7687", user="neo4j", pwd="12345678")

# ----------------------------
# Users
# ----------------------------
USERS = {
    'guest': {'password': '', 'role': 'guest'},
    'member': {'password': 'member123', 'role': 'member'},
     'Huslen': {'password': 'huslen123', 'role': 'member'},
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
        query += f" AND toLower(m.title) CONTAINS toLower('{safe_text}')"

    # Он дээр шүүх
    if year_from.isdigit(): 
        query += f" AND m.released >= {year_from}"
    if year_to.isdigit():
        query += f" AND m.released <= {year_to}"

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
# ----------------------------
@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            error = "Нэвтрэхэд алдаа гарлаа!"
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
            error = "Нууц үг таарахгүй байна!"
            return render_template("register.html", error=error)

        # Neo4j дээр давхар хэрэглэгч байгаа эсэх шалгах
        check_query = "MATCH (u:User {{username: '{}'}}) RETURN u".format(username.replace("'", "\\'"))
        session['username'] = username
        session['role'] = 'member'


        existing = conn.query(check_query)
        if existing:
            error = "Энэ хэрэглэгчийн нэр аль хэдийн ашиглагдсан байна!"
            return render_template("register.html", error=error)

        # Хэрэглэгч нэмэх
        create_query = f"CREATE (u:User {{username: '{username.replace('\'','\\\'')}', password: '{password}'}})"
        conn.query(create_query)

        # Session тохируулах
        session['username'] = username
        session['role'] = 'member'

        return redirect(url_for('index'))

    return render_template("register.html", error=error)
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        # TODO: reset password логик энд нэмэх
        return "Password reset instructions sent!"  
    return render_template("forgot_password.html")

@app.route("/reset_password_direct", methods=["GET", "POST"])
def reset_password_direct():
    error = None
    success = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if new_password != confirm:
            error = "Нууц үг таарахгүй байна!"
        else:
            # Neo4j дээр хэрэглэгч байгаа эсэхийг шалгах
            user_check = conn.query(f"MATCH (u:User {{username: '{username.replace('\'','\\\'')}}}) RETURN u")
            if not user_check:
                error = "Хэрэглэгч олдсонгүй!"
            else:
                # Шинэ нууц үг хадгалах
                conn.query(f"""
                    MATCH (u:User {{username: '{username.replace('\'','\\\'')}}})
                    SET u.password = '{new_password.replace('\'','\\\'')}'
                """)
                success = "Нууц үг амжилттай солигдлоо!"

    return render_template("reset_password_direct.html", error=error, success=success)




# ----------------------------
# Movie detail + Reviews
# ----------------------------
@app.route("/movie/<title>")
def movie_detail(title):
    title_safe = title.replace("'", "\\'")
    
    query = f"""
    MATCH (m:Movie {{title: '{title_safe}'}})
    OPTIONAL MATCH (m)<-[r:REVIEWED]-(u:User)
    OPTIONAL MATCH (m)<-[a:ACTED_IN|DIRECTED|WROTE|PRODUCED]-(p:Person)
    RETURN m.title AS title, m.released AS year, m.image AS image,
           collect(DISTINCT {{username: u.username, summary: r.summary, rating: r.rating}}) AS reviews,
           collect(DISTINCT {{name: p.name, role: type(a), image: p.image}}) AS team
    """
    
    result = conn.query(query)
    if not result:
        return "Movie not found", 404
    
    movie = dict(result[0])

    # --- Дундаж үнэлгээ ---
    if movie["reviews"]:
        ratings = [rev["rating"] for rev in movie["reviews"] if rev["rating"] is not None]
        movie["avg_rating"] = round(sum(ratings) / len(ratings), 2) if ratings else None
    else:
        movie["avg_rating"] = None

    # --- Кино багийг төрөл тус бүрээр ангилах ---
    team = movie.get("team", [])

    actors =     [p for p in team if p["role"] == "ACTED_IN"]
    directors =  [p for p in team if p["role"] == "DIRECTED"]
    writers =    [p for p in team if p["role"] == "WROTE"]
    producers =  [p for p in team if p["role"] == "PRODUCED"]

    # --- Админ хүнүүдийн жагсаалт ---
    people = conn.query("MATCH (p:Person) RETURN p.name AS name ORDER BY p.name") \
             if session.get("role") == "admin" else []

    return render_template(
        "movie_detail.html",
        movie=movie,
        actors=actors,
        directors=directors,
        writers=writers,
        producers=producers,
        people=people,
        role=session.get('role', 'guest')
    )

# ----------------------------
# Quick Add Member (Admin)
# ----------------------------
@app.route("/movie/<title>/add_member_quick/<person_name>/<role>")
def add_member_quick(title, person_name, role):
    if session.get('role') != 'admin':
        return "Зөвшөөрөгдсөнгүй!"
    
    title_safe = title.replace("'", "\\'")
    person_safe = person_name.replace("'", "\\'")
    
    query = f"""
    MATCH (m:Movie {{title: '{title_safe}'}}), (p:Person {{name: '{person_safe}'}})
    MERGE (p)-[:{role}]->(m)
    """
    conn.query(query)
    return redirect(url_for('movie_detail', title=title))

# ----------------------------
# Add Review
# ----------------------------
@app.route("/movie/<title>/review", methods=['POST'])
def add_review(title):
    if 'username' not in session or session.get('role') == 'guest':
        return "Та нэвтэрсэн байх шаардлагатай!"
    summary = request.form.get('summary', '').replace("'", "\\'")
    try:
        rating = int(request.form.get('rating', '0'))
    except ValueError:
        rating = 0
    username = session['username'].replace("'", "\\'")
    title_safe = title.replace("'", "\\'")
    query = f"""
    MERGE (u:User {{username: '{username}'}})
    MERGE (m:Movie {{title: '{title_safe}'}})
    MERGE (u)-[r:REVIEWED]->(m)
    SET r.summary = '{summary}', r.rating = {rating}
    """
    conn.query(query)
    return redirect(url_for('movie_detail', title=title))

# ----------------------------
# Admin: Add Movie / Person / Movie Member
# ----------------------------
@app.route("/admin/movie/add", methods=['GET', 'POST'])
def add_movie():
    if session.get('role') != 'admin':
        return "Зөвшөөрөгдсөнгүй!"
    if request.method == 'POST':
        title = request.form.get('title', '').replace("'", "\\'")
        released = request.form.get('released', '0')
        img_file = request.files.get('image')
        img_name = img_file.filename if img_file else 'default.jpg'
        if img_file:
            img_file.save(os.path.join(app.config['MOVIE_UPLOAD'], img_name))
        query = f"CREATE (m:Movie {{title: '{title}', released: {released}, image: '{img_name}'}})"
        conn.query(query)
        return redirect(url_for('index'))
    return render_template("admin_add_movie.html")

@app.route("/admin/person/add", methods=['GET', 'POST'])
def add_person():
    if session.get('role') != 'admin':
        return "Зөвшөөрөгдсөнгүй!"

    if request.method == 'POST':
        name = request.form.get('name', '').replace("'", "\\'")
        born = request.form.get('born', '0')   # <-- ШИНЭ
        role = request.form.get('role', 'actor')

        img_file = request.files.get('image')
        img_name = img_file.filename if img_file else 'default.jpg'

        if img_file:
            img_file.save(os.path.join(app.config['PERSON_UPLOAD'], img_name))

        query = f"""
        CREATE (p:Person {{
            name: '{name}',
            born: {born},
            role: '{role}',
            image: '{img_name}'
        }})
        """
        conn.query(query)
        return redirect(url_for('index'))

    return render_template("admin_add_person.html")


@app.route("/admin/movie/<title>/add_member", methods=['GET', 'POST'])
def add_member(title):
    if session.get('role') != 'admin':
        return "Зөвшөөрөгдсөнгүй!"
    if request.method == 'POST':
        person_name = request.form.get('person')
        role = request.form.get('role')
        query = f"""
        MATCH (m:Movie {{title: '{title}'}}), (p:Person {{name: '{person_name}'}})
        MERGE (p)-[:{role.upper()}]->(m)
        """
        conn.query(query)
        return redirect(url_for('movie_detail', title=title))
    people = conn.query("MATCH (p:Person) RETURN p.name AS name, p.role AS role")
    return render_template("admin_add_member.html", title=title, people=people)

# ----------------------------
# Person detail
# ----------------------------
@app.route("/person/<name>")
def person_detail(name):
    name_safe = name.replace("'", "\\'")
    query = f"""
        MATCH (p:Person {{name: '{name_safe}'}})
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
    result = conn.query(query)

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

    query = f"""
    MATCH (p:Person)-[:{rel}]->(m:Movie)
    WHERE 1=1
    """

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

    people = conn.query(query)
    people = [dict(p) for p in people]

    return render_template("people_list.html", people=people, title=title, role=session.get("role", "guest"))








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
            old = conn.query(f"""
                MATCH (p:Person {{name:'{name_safe}'}})
                RETURN p.image AS image
            """)
            img_name = old[0]["image"] if old else "default.jpg"

        # Update Neo4j
        query = f"""
        MATCH (p:Person {{name:'{name_safe}'}})
        SET p.name='{new_name}', p.born={born}, p.role='{role}', p.image='{img_name}'
        """
        conn.query(query)

        return redirect(url_for("person_detail", name=new_name))

    # GET — load data
    result = conn.query(f"""
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
    conn.query(f"MATCH (p:Person {{name:'{name_safe}'}}) DETACH DELETE p")
    return redirect(url_for('index'))

# ----------------------------
# Reviewers
# ----------------------------
@app.route("/reviewers")
def reviewers():
    name_filter = request.args.get('name', '').strip()
    query = "MATCH (u:User)-[r:REVIEWED]->(m:Movie) RETURN u.username AS name, count(r) AS reviews ORDER BY u.username LIMIT 50"
    if name_filter:
        query = f"""
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
    if session.get('role') != 'admin':
        return "Зөвшөөрөгдсөнгүй!", 403

    title_safe = title.replace("'", "\\'")
    query = f"MATCH (m:Movie {{title: '{title_safe}'}}) DETACH DELETE m"
    conn.query(query)
    return redirect(url_for('index'))



    
@app.route('/admin/movie/<title>/edit', methods=['GET', 'POST'])
def edit_movie(title):
    if session.get("role") != "admin":
        return "Access Denied", 403

    title_safe = title.replace("'", "\\'")

    # POST: form-оос ирсэн шинэ мэдээллийг хадгалах
    if request.method == "POST":
        new_title = request.form.get("title").replace("'", "\\'")
        released = request.form.get("released")
        img_file = request.files.get("image")
        
        # Зураг хадгалах
        if img_file and img_file.filename:
            img_name = img_file.filename
            img_file.save(os.path.join(app.config['MOVIE_UPLOAD'], img_name))
        else:
            # Шинэ зураг ороогүй бол хуучин зураг хадгалах
            result = conn.query(f"MATCH (m:Movie {{title:'{title_safe}'}}) RETURN m.image AS image")
            img_name = result[0]['image'] if result else 'default.jpg'

        query = f"""
            MATCH (m:Movie {{title:'{title_safe}'}})
            SET m.title='{new_title}', m.released={released}, m.image='{img_name}'
        """
        conn.query(query)
        return redirect(url_for('movie_detail', title=new_title))

    # GET: form харуулах
    result = conn.query(f"""
        MATCH (m:Movie {{title:'{title_safe}'}})
        RETURN m.title AS title, m.released AS released, m.image AS image
    """)
    if not result:
        return "Movie not found"
    
    movie = result[0]
    return render_template("admin_edit_movie.html", movie=movie)



# ----------------------------
# Run Flask
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
