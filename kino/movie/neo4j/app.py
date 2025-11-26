from flask import Flask, render_template, request, redirect, url_for, session
from myneo4j import Neo4jConnection
import os

# Flask app
app = Flask(__name__, template_folder='templates')
app.secret_key = 'super_secret_key_here'

# Static folders
MOVIE_IMG = os.path.join('static', 'movies')
PERSON_IMG = os.path.join('static', 'people')
os.makedirs(MOVIE_IMG, exist_ok=True)
os.makedirs(PERSON_IMG, exist_ok=True)
app.config['MOVIE_UPLOAD'] = MOVIE_IMG
app.config['PERSON_UPLOAD'] = PERSON_IMG

# Neo4j connection
conn = Neo4jConnection(uri="neo4j://127.0.0.1:7687", user="neo4j", pwd="12345678")

# Users
USERS = {
    'guest': {'password': '', 'role': 'guest'},
    'member': {'password': 'member123', 'role': 'member'},
    'admin': {'password': 'admin123', 'role': 'admin'}
}

# Index page
@app.route("/", methods=['GET'])
def index():
    query_text = request.args.get('txtMovieTitle', '')
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

# Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            error = "Нэвтрэхэд алдаа гарлаа!"
    return render_template("login.html", error=error)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

# Movie detail
@app.route("/movie/<title>")
def movie_detail(title):
    title_safe = title.replace("'", "\\'")
    query = f"""
    MATCH (m:Movie {{title: '{title_safe}'}})
    OPTIONAL MATCH (m)<-[r:ACTED_IN]-(p:Person)
    RETURN m.title AS title, m.released AS year, m.image AS image,
           collect(DISTINCT p) AS actors
    """
    result = conn.query(query)
    movie = result[0] if result else None
    return render_template("movie_detail.html", movie=movie, role=session.get('role', 'guest'))

# Add review
@app.route("/movie/<title>/review", methods=['POST'])
def add_review(title):
    if 'username' not in session or session.get('role') == 'guest':
        return "Та нэвтэрсэн байх шаардлагатай!"
    summary = request.form.get('summary', '').replace("'", "\\'")
    rating = int(request.form.get('rating', 0))
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

# Admin add movie
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

# Admin add person
@app.route("/admin/person/add", methods=['GET', 'POST'])
def add_person():
    if session.get('role') != 'admin':
        return "Зөвшөөрөгдсөнгүй!"
    if request.method == 'POST':
        name = request.form.get('name', '').replace("'", "\\'")
        birth = request.form.get('birthYear', '0')
        role = request.form.get('role', 'actor')  # admin хуудаснаас role дамжуулна
        img_file = request.files.get('image')
        img_name = img_file.filename if img_file else 'default.jpg'
        if img_file:
            img_file.save(os.path.join(app.config['PERSON_UPLOAD'], img_name))
        query = f"CREATE (p:Person {{name: '{name}', birthYear: {birth}, role: '{role}', image: '{img_name}'}})"
        conn.query(query)
        return redirect(url_for('index'))
    return render_template("admin_add_person.html")

# Generic function for people pages with filtering
def person_by_role(role, title):
    name_filter = request.args.get('name', '')
    year_from = request.args.get('year_from', '')
    year_to = request.args.get('year_to', '')

    query = f"MATCH (p:Person) WHERE p.role = '{role}' "

    if name_filter:
        query += f"AND toLower(p.name) CONTAINS toLower('{name_filter.replace('\'', '\\\'')}') "
    if year_from:
        query += f"AND p.birthYear >= {year_from} "
    if year_to:
        query += f"AND p.birthYear <= {year_to} "

    query += "RETURN p.name AS name, p.birthYear AS birthYear, p.image AS image ORDER BY p.name LIMIT 50"

    people = conn.query(query)
    return render_template("people_list.html", people=people, role=session.get('role', 'guest'), title=title)

# Actors page
@app.route("/actors")
def actors():
    return person_by_role('actor', "Жүжигчид")

# Directors page
@app.route("/directors")
def directors():
    return person_by_role('director', "Найруулагч")

# Writers page
@app.route("/writers")
def writers():
    return person_by_role('writer', "Зохиолч")

# Producers page
@app.route("/producers")
def producers():
    return person_by_role('producer', "Продюсер")

# Reviewers page (Шүүмжлэгчид)
@app.route("/reviewers")
def reviewers():
    name_filter = request.args.get('name', '')
    query = "MATCH (u:User)-[r:REVIEWED]->(m:Movie) RETURN u.username AS name, count(r) AS reviews ORDER BY u.username LIMIT 50"
    if name_filter:
        query = f"""
        MATCH (u:User)-[r:REVIEWED]->(m:Movie)
        WHERE toLower(u.username) CONTAINS toLower('{name_filter.replace('\'', '\\\'')}')
        RETURN u.username AS name, count(r) AS reviews ORDER BY u.username LIMIT 50
        """
    reviewers = conn.query(query)
    return render_template("reviewers_list.html", reviewers=reviewers, role=session.get('role', 'guest'), title="Кино шүүмжлэгчид")

if __name__ == "__main__":
    app.run(debug=True)
