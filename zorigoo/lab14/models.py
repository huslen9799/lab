import sqlite3
from typing import Any, Dict, List, Optional

DB_NAME = "MU.db"

def get_conn():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    return con

class Bagsh:
    @staticmethod
    def getRecords() -> List[Dict[str, Any]]:
        con = get_conn()
        rows = con.execute("SELECT * FROM bagsh ORDER BY id DESC").fetchall()
        con.close()
        return [dict(r) for r in rows]

    @staticmethod
    def getRecord(id: int) -> Optional[Dict[str, Any]]:
        con = get_conn()
        row = con.execute("SELECT * FROM bagsh WHERE id = ?", (id,)).fetchone()
        con.close()
        return dict(row) if row else None

    @staticmethod
    def Add(data: Dict[str, Any]) -> None:
        con = get_conn()
        con.execute("""
            INSERT INTO bagsh(code, ovog, ner, huis, ajild_orson, tenhim)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data["code"], data["ovog"], data["ner"], data["huis"],
              data["ajild_orson"], data["tenhim"]))
        con.commit()
        con.close()

    @staticmethod
    def Edit(id: int, data: Dict[str, Any]) -> None:
        con = get_conn()
        con.execute("""
            UPDATE bagsh
            SET code=?, ovog=?, ner=?, huis=?, ajild_orson=?, tenhim=?
            WHERE id=?
        """, (data["code"], data["ovog"], data["ner"], data["huis"],
              data["ajild_orson"], data["tenhim"], id))
        con.commit()
        con.close()

    @staticmethod
    def Delete(id: int) -> None:
        con = get_conn()
        con.execute("DELETE FROM bagsh WHERE id = ?", (id,))
        con.commit()
        con.close()


class Oyutan:
    @staticmethod
    def getRecords() -> List[Dict[str, Any]]:
        con = get_conn()
        rows = con.execute("SELECT * FROM oyutan ORDER BY id DESC").fetchall()
        con.close()
        return [dict(r) for r in rows]

    @staticmethod
    def getRecord(id: int) -> Optional[Dict[str, Any]]:
        con = get_conn()
        row = con.execute("SELECT * FROM oyutan WHERE id = ?", (id,)).fetchone()
        con.close()
        return dict(row) if row else None

    @staticmethod
    def Add(data: Dict[str, Any]) -> None:
        con = get_conn()
        con.execute("""
            INSERT INTO oyutan(code, ovog, ner, huis, elselt_ognoo, mergejil)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data["code"], data["ovog"], data["ner"], data["huis"],
              data["elselt_ognoo"], data["mergejil"]))
        con.commit()
        con.close()

    @staticmethod
    def Edit(id: int, data: Dict[str, Any]) -> None:
        con = get_conn()
        con.execute("""
            UPDATE oyutan
            SET code=?, ovog=?, ner=?, huis=?, elselt_ognoo=?, mergejil=?
            WHERE id=?
        """, (data["code"], data["ovog"], data["ner"], data["huis"],
              data["elselt_ognoo"], data["mergejil"], id))
        con.commit()
        con.close()

    @staticmethod
    def Delete(id: int) -> None:
        con = get_conn()
        con.execute("DELETE FROM oyutan WHERE id = ?", (id,))
        con.commit()
        con.close()
