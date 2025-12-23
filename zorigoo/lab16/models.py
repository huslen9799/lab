import sqlite3
from typing import Any, Dict, List, Optional, Tuple

DB_NAME = "MU.db"

def get_conn():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    return con

class Hicheel:
    ALLOWED_SORT = {"id", "code", "ner", "credit", "turul"}

    @staticmethod
    def getRecords(
        page: int = 1,
        per_page: int = 10,
        q: str = "",
        turul: str = "",
        sort: str = "ner",
        order: str = "asc",
    ) -> Tuple[List[Dict[str, Any]], int]:

        page = max(1, int(page))
        per_page = min(50, max(1, int(per_page)))

        sort = sort if sort in Hicheel.ALLOWED_SORT else "ner"
        order = "desc" if str(order).lower() == "desc" else "asc"

        where = []
        params: List[Any] = []

        if q:
            where.append("ner LIKE ?")
            params.append(f"%{q}%")

        if turul:
            where.append("turul = ?")
            params.append(turul)

        where_sql = ("WHERE " + " AND ".join(where)) if where else ""

        con = get_conn()

        total = con.execute(
            f"SELECT COUNT(*) AS c FROM hicheel {where_sql}", params
        ).fetchone()["c"]

        offset = (page - 1) * per_page

        rows = con.execute(
            f"""
            SELECT * FROM hicheel
            {where_sql}
            ORDER BY {sort} {order}
            LIMIT ? OFFSET ?
            """,
            params + [per_page, offset]
        ).fetchall()

        con.close()
        return [dict(r) for r in rows], int(total)

    @staticmethod
    def getRecord(id: int) -> Optional[Dict[str, Any]]:
        con = get_conn()
        row = con.execute("SELECT * FROM hicheel WHERE id=?", (id,)).fetchone()
        con.close()
        return dict(row) if row else None

    @staticmethod
    def Add(data: Dict[str, Any]) -> None:
        con = get_conn()
        con.execute("""
            INSERT INTO hicheel(code, ner, credit, umnuh_holboo, turul)
            VALUES(?,?,?,?,?)
        """, (
            data["code"], data["ner"], int(data["credit"]),
            data.get("umnuh_holboo", ""), data["turul"]
        ))
        con.commit()
        con.close()

    @staticmethod
    def Edit(id: int, data: Dict[str, Any]) -> None:
        con = get_conn()
        con.execute("""
            UPDATE hicheel
            SET code=?, ner=?, credit=?, umnuh_holboo=?, turul=?
            WHERE id=?
        """, (
            data["code"], data["ner"], int(data["credit"]),
            data.get("umnuh_holboo", ""), data["turul"], id
        ))
        con.commit()
        con.close()

    @staticmethod
    def Delete(id: int) -> None:
        con = get_conn()
        con.execute("DELETE FROM hicheel WHERE id=?", (id,))
        con.commit()
        con.close()
