from flask import Flask, render_template, request, redirect, url_for, session
from myneo4j import Neo4jConnection
import os

# ----------------------------
# Flask setup
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = 'super_secret_unique_key_here'

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
    'admin': {'password': 'admin123', 'role': 'admin'}
}

# ----------------------------
# Index page
# ----------------------------
@app.route("/", methods=['GET'])
def index():
    query_text = request.args.get('txtMovieTitle', '').strip()
    if query_text:
        query = f"""
        MATCH (m:Movie)
        WHERE toLower(m.title) CONTAINS toLower('{query_text.replace("'", "\\'")}')
        RETURN m.title AS title, m.released AS year, m.image AS image
        LIMIT 20
        """
    else:
        query = "MATCH (m:Movie) RETURN m.title AS title, m.released AS year, m.image AS image LIMIT 10"
    movies = conn.query(query)
    return render_template("index.html", movies=movies, query=query_text, role=session.get('role', 'guest'))

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
        if username in USERS:
            error = "Энэ хэрэглэгчийн нэр аль хэдийн ашиглагдсан байна!"
        elif password != confirm:
            error = "Нууц үг таарахгүй байна!"
        else:
            USERS[username] = {'password': password, 'role': 'member'}
            session['username'] = username
            session['role'] = 'member'
            return redirect(url_for('index'))
    return render_template("register.html", error=error)

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
           collect(DISTINCT {{name: p.name, role: type(a)}}) AS team
    """
    result = conn.query(query)
    movie = dict(result[0]) if result else None

    # Дундаж үнэлгээ
    if movie and movie['reviews']:
        ratings = [rev['rating'] for rev in movie['reviews'] if rev['rating'] is not None]
        movie['avg_rating'] = round(sum(ratings)/len(ratings), 2) if ratings else None
    else:
        movie['avg_rating'] = None

    # Админд зориулсан бүх хүн
    people = conn.query("MATCH (p:Person) RETURN p.name AS name ORDER BY p.name") if session.get('role') == 'admin' else []

    return render_template("movie_detail.html", movie=movie, people=people, role=session.get('role', 'guest'))

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
        birth = request.form.get('birthYear', '0')
        role = request.form.get('role', 'actor')
        img_file = request.files.get('image')
        img_name = img_file.filename if img_file else 'default.jpg'
        if img_file:
            img_file.save(os.path.join(app.config['PERSON_UPLOAD'], img_name))
        query = f"CREATE (p:Person {{name: '{name}', birthYear: {birth}, role: '{role}', image: '{img_name}'}})"
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
    MATCH (p:Person {{name: '{name_safe}'}})-[r:ACTED_IN|DIRECTED|WROTE|PRODUCED]->(m:Movie)
    RETURN p.name AS name, p.role AS role, collect({{title: m.title, year: m.released, image: m.image}}) AS movies
    """
    result = conn.query(query)
    person = dict(result[0]) if result else None
    return render_template("person_detail.html", person=person, role=session.get('role', 'guest'))

# ----------------------------
# People pages with filter (function нэг удаа тодорхойлсон)
# ----------------------------
def person_by_role(role, title):
    name_filter = request.args.get('name', '').strip()
    year_from = request.args.get('year_from', '').strip()
    year_to = request.args.get('year_to', '').strip()

    query = f"MATCH (p:Person) WHERE p.role = '{role}'"
    filters = []
    if name_filter:
        filters.append(f"toLower(p.name) CONTAINS toLower('{name_filter.replace('\'', '\\\'')}')")
    if year_from.isdigit():
        filters.append(f"p.birthYear >= {year_from}")
    if year_to.isdigit():
        filters.append(f"p.birthYear <= {year_to}")
    if filters:
        query += " AND " + " AND ".join(filters)
    query += " RETURN p.name AS name, p.birthYear AS birthYear, p.image AS image ORDER BY p.name LIMIT 50"

    people = conn.query(query)
    people = [dict(p) if not isinstance(p, dict) else p for p in people]
    return render_template("people_list.html", people=people, role=session.get('role', 'guest'), title=title)

@app.route("/actors")
def actors():
    return person_by_role('actor', "Жүжигчид")

@app.route("/directors")
def directors():
    return person_by_role('director', "Найруулагч")

@app.route("/writers")
def writers():
    return person_by_role('writer', "Зохиолч")

@app.route("/producers")
def producers():
    return person_by_role('producer', "Продюсер")

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
    return render_template("actors.html", actors=actors)
    return render_template("directors.html", directors=directors)
    return render_template("writers.html", writers=writers)
    return render_template("producers.html", producers=producers)

# ----------------------------
# Run Flask
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
