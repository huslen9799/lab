import sqlite3

DB_FILE = "database2.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Branch хүснэгт
c.execute("""
CREATE TABLE IF NOT EXISTS Branch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bname TEXT NOT NULL
)
""")

# Worker хүснэгт
c.execute("""
CREATE TABLE IF NOT EXISTS Worker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wname TEXT NOT NULL,
    bid INTEGER,
    FOREIGN KEY(bid) REFERENCES Branch(id)
)
""")

# Жишээ өгөгдөл
branches = [('Дархан',), ('Салбар',), ('Баян-Өлгий',)]
workers = [('Бат', 1), ('Сүхээ', 2), ('Дулмаа', 3)]

# Өгөгдөл оруулах
c.executemany("INSERT INTO Branch (bname) VALUES (?)", branches)
c.executemany("INSERT INTO Worker (wname, bid) VALUES (?, ?)", workers)

conn.commit()
conn.close()

print("database2.db үүссэн, 3 салбар, 3 ажилтан өгөгдөлтэй.")
