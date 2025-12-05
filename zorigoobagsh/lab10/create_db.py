import os, sqlite3

if os.path.exists("Employee.db"):
    os.remove("Employee.db")

conn = sqlite3.connect("Employee.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE Branch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bname TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE Worker (
    wid INTEGER PRIMARY KEY AUTOINCREMENT,
    wname TEXT NOT NULL,
    bid INTEGER,
    FOREIGN KEY (bid) REFERENCES Branch(id)
)
""")

# Жишээ салбарууд
cur.executemany("INSERT INTO Branch (bname) VALUES (?)", [
    ("Төв салбар",),
    ("Дархан салбар",)
])

conn.commit()
conn.close()
print("✅ Employee.db үүссэн!")
