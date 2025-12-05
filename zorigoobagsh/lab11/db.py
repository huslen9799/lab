import sqlite3
import os

DB_FILE = "database.db"

# Хуучин database-г устгах
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# Шинэ database үүсгэх
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Branch хүснэгт
cursor.execute("""
CREATE TABLE Branch(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bname TEXT NOT NULL
)
""")

# Worker хүснэгт
cursor.execute("""
CREATE TABLE Worker(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wname TEXT NOT NULL,
    bid INTEGER,
    FOREIGN KEY(bid) REFERENCES Branch(id)
)
""")

# Жишээ өгөгдөл оруулах
cursor.execute("INSERT INTO Branch(bname) VALUES (?)", ("IT",))
cursor.execute("INSERT INTO Branch(bname) VALUES (?)", ("HR",))
cursor.execute("INSERT INTO Branch(bname) VALUES (?)", ("Finance",))

cursor.execute("INSERT INTO Worker(wname, bid) VALUES (?, ?)", ("Bat", 1))
cursor.execute("INSERT INTO Worker(wname, bid) VALUES (?, ?)", ("Bold", 2))

conn.commit()
conn.close()

print("✅ database.db амжилттай үүслээ, хүснэгтүүд болон жишээ өгөгдөл орлоо.")
