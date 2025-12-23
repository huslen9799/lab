import sqlite3
from typing import Any, Dict, List, Optional

DB_NAME = "MU.db"

def get_conn():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con

class AlbanTushaal:
    @staticmethod
    def getRecords() -> List[Dict[str, Any]]:
        con = get_conn()
        rows = con.execute("SELECT * FROM alban_tushaal ORDER BY id DESC").fetchall()
        con.close()
        return [dict(r) for r in rows]

    @staticmethod
    def getRecord(id: int) -> Optional[Dict[str, Any]]:
        con = get_conn()
        row = con.execute("SELECT * FROM alban_tushaal WHERE id=?", (id,)).fetchone()
        con.close()
        return dict(row) if row else None

    @staticmethod
    def Add(data: Dict[str, Any]) -> None:
        con = get_conn()
        con.execute("INSERT INTO alban_tushaal(ner) VALUES(?)", (data["ner"],))
        con.commit(); con.close()

    @staticmethod
    def Edit(id: int, data: Dict[str, Any]) -> None:
        con = get_conn()
        con.execute("UPDATE alban_tushaal SET ner=? WHERE id=?", (data["ner"], id))
        con.commit(); con.close()

    @staticmethod
    def Delete(id: int) -> None:
        con = get_conn()
        con.execute("DELETE FROM alban_tushaal WHERE id=?", (id,))
        con.commit(); con.close()


class ErdmiinZereg:
    @staticmethod
    def getRecords():
        con = get_conn()
        rows = con.execute("SELECT * FROM erdmiin_zereg ORDER BY id DESC").fetchall()
        con.close()
        return [dict(r) for r in rows]

    @staticmethod
    def getRecord(id: int):
        con = get_conn()
        row = con.execute("SELECT * FROM erdmiin_zereg WHERE id=?", (id,)).fetchone()
        con.close()
        return dict(row) if row else None

    @staticmethod
    def Add(data):
        con = get_conn()
        con.execute("INSERT INTO erdmiin_zereg(ner) VALUES(?)", (data["ner"],))
        con.commit(); con.close()

    @staticmethod
    def Edit(id: int, data):
        con = get_conn()
        con.execute("UPDATE erdmiin_zereg SET ner=? WHERE id=?", (data["ner"], id))
        con.commit(); con.close()

    @staticmethod
    def Delete(id: int):
        con = get_conn()
        con.execute("DELETE FROM erdmiin_zereg WHERE id=?", (id,))
        con.commit(); con.close()


class Tenhim:
    @staticmethod
    def getRecords():
        con = get_conn()
        rows = con.execute("SELECT * FROM tenhim ORDER BY id DESC").fetchall()
        con.close()
        return [dict(r) for r in rows]

    @staticmethod
    def getRecord(id: int):
        con = get_conn()
        row = con.execute("SELECT * FROM tenhim WHERE id=?", (id,)).fetchone()
        con.close()
        return dict(row) if row else None

    @staticmethod
    def Add(data):
        con = get_conn()
        con.execute("INSERT INTO tenhim(ner) VALUES(?)", (data["ner"],))
        con.commit(); con.close()

    @staticmethod
    def Edit(id: int, data):
        con = get_conn()
        con.execute("UPDATE tenhim SET ner=? WHERE id=?", (data["ner"], id))
        con.commit(); con.close()

    @staticmethod
    def Delete(id: int):
        con = get_conn()
        con.execute("DELETE FROM tenhim WHERE id=?", (id,))
        con.commit(); con.close()


class Bagsh:
    @staticmethod
    def getRecords():
        con = get_conn()
        rows = con.execute("""
            SELECT b.*,
                   t.ner AS tenhim_ner,
                   a.ner AS alban_ner,
                   z.ner AS zereg_ner
            FROM bagsh b
            JOIN tenhim t ON t.id=b.tenhim_id
            JOIN alban_tushaal a ON a.id=b.alban_tushaal_id
            JOIN erdmiin_zereg z ON z.id=b.erdmiin_zereg_id
            ORDER BY b.id DESC
        """).fetchall()
        con.close()
        return [dict(r) for r in rows]

    @staticmethod
    def getRecord(id: int):
        con = get_conn()
        row = con.execute("SELECT * FROM bagsh WHERE id=?", (id,)).fetchone()
        con.close()
        return dict(row) if row else None

    @staticmethod
    def Add(data):
        con = get_conn()
        con.execute("""
            INSERT INTO bagsh(code, ovog, ner, huis, ajild_orson, tenhim_id, alban_tushaal_id, erdmiin_zereg_id)
            VALUES(?,?,?,?,?,?,?,?)
        """, (
            data["code"], data["ovog"], data["ner"], data["huis"], data["ajild_orson"],
            data["tenhim_id"], data["alban_tushaal_id"], data["erdmiin_zereg_id"]
        ))
        con.commit(); con.close()

    @staticmethod
    def Edit(id: int, data):
        con = get_conn()
        con.execute("""
            UPDATE bagsh
            SET code=?, ovog=?, ner=?, huis=?, ajild_orson=?, tenhim_id=?, alban_tushaal_id=?, erdmiin_zereg_id=?
            WHERE id=?
        """, (
            data["code"], data["ovog"], data["ner"], data["huis"], data["ajild_orson"],
            data["tenhim_id"], data["alban_tushaal_id"], data["erdmiin_zereg_id"], id
        ))
        con.commit(); con.close()

    @staticmethod
    def Delete(id: int):
        con = get_conn()
        con.execute("DELETE FROM bagsh WHERE id=?", (id,))
        con.commit(); con.close()


class Oyutan:
    @staticmethod
    def getRecords():
        con = get_conn()
        rows = con.execute("""
            SELECT o.*,
                   t.ner AS tenhim_ner
            FROM oyutan o
            JOIN tenhim t ON t.id=o.tenhim_id
            ORDER BY o.id DESC
        """).fetchall()
        con.close()
        return [dict(r) for r in rows]

    @staticmethod
    def getRecord(id: int):
        con = get_conn()
        row = con.execute("SELECT * FROM oyutan WHERE id=?", (id,)).fetchone()
        con.close()
        return dict(row) if row else None

    @staticmethod
    def Add(data):
        con = get_conn()
        con.execute("""
            INSERT INTO oyutan(code, ovog, ner, huis, elselt_ognoo, tenhim_id, zurag)
            VALUES(?,?,?,?,?,?,?)
        """, (
            data["code"], data["ovog"], data["ner"], data["huis"], data["elselt_ognoo"],
            data["tenhim_id"], data.get("zurag")
        ))
        con.commit(); con.close()

    @staticmethod
    def Edit(id: int, data):
        con = get_conn()
        con.execute("""
            UPDATE oyutan
            SET code=?, ovog=?, ner=?, huis=?, elselt_ognoo=?, tenhim_id=?, zurag=?
            WHERE id=?
        """, (
            data["code"], data["ovog"], data["ner"], data["huis"], data["elselt_ognoo"],
            data["tenhim_id"], data.get("zurag"), id
        ))
        con.commit(); con.close()

    @staticmethod
    def Delete(id: int):
        con = get_conn()
        con.execute("DELETE FROM oyutan WHERE id=?", (id,))
        con.commit(); con.close()
