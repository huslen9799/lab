import sqlite3

DB_NAME = "Employee.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

class Branch:
    @staticmethod
    def getRecords():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Branch")
        data = cur.fetchall()
        conn.close()
        return data

class Worker:
    @staticmethod
    def getRecords():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT w.wid, w.wname, b.bname
            FROM Worker w LEFT JOIN Branch b ON w.bid = b.id
        """)
        data = cur.fetchall()
        conn.close()
        return data

    @staticmethod
    def Add(wname, bid):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Worker (wname, bid) VALUES (?, ?)", (wname, bid))
        conn.commit()
        conn.close()
