import sqlite3

DB_NAME = "MU.db"

def main():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alban_tushaal(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ner TEXT NOT NULL UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS erdmiin_zereg(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ner TEXT NOT NULL UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tenhim(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ner TEXT NOT NULL UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bagsh(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        ovog TEXT NOT NULL,
        ner  TEXT NOT NULL,
        huis TEXT NOT NULL CHECK(huis IN ('Эр','Эм')),
        ajild_orson TEXT NOT NULL, -- YYYY-MM-DD
        tenhim_id INTEGER NOT NULL,
        alban_tushaal_id INTEGER NOT NULL,
        erdmiin_zereg_id INTEGER NOT NULL,
        FOREIGN KEY(tenhim_id) REFERENCES tenhim(id),
        FOREIGN KEY(alban_tushaal_id) REFERENCES alban_tushaal(id),
        FOREIGN KEY(erdmiin_zereg_id) REFERENCES erdmiin_zereg(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS oyutan(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        ovog TEXT NOT NULL,
        ner  TEXT NOT NULL,
        huis TEXT NOT NULL CHECK(huis IN ('Эр','Эм')),
        elselt_ognoo TEXT NOT NULL, -- YYYY-MM-DD
        tenhim_id INTEGER NOT NULL,
        zurag TEXT, -- uploads/ доторх filename
        FOREIGN KEY(tenhim_id) REFERENCES tenhim(id)
    )
    """)

    con.commit()
    con.close()
    print("✅ MU.db created (all tables).")

if __name__ == "__main__":
    main()
