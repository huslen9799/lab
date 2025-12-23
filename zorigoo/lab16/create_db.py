import sqlite3
import random

DB_NAME = "MU.db"

TURULS = ["Суурь", "Мэргэжлийн", "Сонгон", "Ерөнхий", "Заавал"]

NAMES = [
    "Программчлалын үндэс", "Өгөгдлийн сан", "Веб хөгжүүлэлт",
    "Сүлжээний үндэс", "Алгоритм", "Объект хандлагат програмчлал",
    "Операцийн систем", "Кибер аюулгүй байдал", "Хиймэл оюун",
    "Машин сургалт", "Компьютерийн архитектур", "Статистик"
]

def main():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS hicheel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        ner TEXT NOT NULL,
        credit INTEGER NOT NULL,
        umnuh_holboo TEXT,
        turul TEXT NOT NULL
    )
    """)

    # Demo өгөгдөл (хоосон үед нэг удаа)
    count = cur.execute("SELECT COUNT(*) FROM hicheel").fetchone()[0]
    if count == 0:
        for i in range(1, 61):  # 60 мөр
            code = f"SW{1000+i}"
            ner = f"{random.choice(NAMES)} {i}"
            credit = random.choice([2, 3, 4])
            umnuh = random.choice(["", "SW1001", "SW1005", "MATH1001"])
            turul = random.choice(TURULS)
            cur.execute("""
                INSERT INTO hicheel(code, ner, credit, umnuh_holboo, turul)
                VALUES(?,?,?,?,?)
            """, (code, ner, credit, umnuh, turul))

    con.commit()
    con.close()
    print("✅ MU.db created and seeded (hicheel).")

if __name__ == "__main__":
    main()
