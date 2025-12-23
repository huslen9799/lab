import sqlite3

DB_NAME = "MU.db"

def main():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bagsh (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        ovog TEXT NOT NULL,
        ner  TEXT NOT NULL,
        huis TEXT NOT NULL CHECK(huis IN ('Эр','Эм')),
        ajild_orson TEXT NOT NULL,          -- YYYY-MM-DD
        tenhim TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS oyutan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        ovog TEXT NOT NULL,
        ner  TEXT NOT NULL,
        huis TEXT NOT NULL CHECK(huis IN ('Эр','Эм')),
        elselt_ognoo TEXT NOT NULL,         -- YYYY-MM-DD
        mergejil TEXT NOT NULL
    )
    """)

    con.commit()
    con.close()
    print("✅ MU.db and tables created.")

if __name__ == "__main__":
    main()
