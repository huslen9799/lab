from db import get_db

class ZeregDAO:
    def getRecords(self):
        db = get_db()
        return db.execute("SELECT * FROM zereg ORDER BY id DESC").fetchall()

    def getRecord(self, id: int):
        db = get_db()
        return db.execute("SELECT * FROM zereg WHERE id=?", (id,)).fetchone()

    def Add(self, name: str):
        db = get_db()
        db.execute("INSERT INTO zereg(name) VALUES(?)", (name.strip(),))
        db.commit()

    def Edit(self, id: int, name: str):
        db = get_db()
        db.execute("UPDATE zereg SET name=? WHERE id=?", (name.strip(), id))
        db.commit()

    def Delete(self, id: int):
        db = get_db()
        db.execute("DELETE FROM zereg WHERE id=?", (id,))
        db.commit()
