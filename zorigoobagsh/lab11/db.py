import sqlite3
import os

db_path = "Employee.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Branch table
cur.execute("""
CREATE TABLE IF NOT EXISTS Branch(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bname TEXT
)
""")

# Worker table
cur.execute("""
CREATE TABLE IF NOT EXISTS Worker(
    wid INTEGER PRIMARY KEY AUTOINCREMENT,
    wname TEXT,
    bid INTEGER,
    FOREIGN KEY(bid) REFERENCES Branch(id)
)
""")

conn.commit()
conn.close()

print("Database created successfully!")
