import sqlite3

DB_NAME = "MU.db"

def main():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alban(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS zereg(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tenhim(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS mergejil(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    conn.commit()
    conn.close()
    print("MU.db бэлэн боллоо ✅")

if __name__ == "__main__":
    main()
