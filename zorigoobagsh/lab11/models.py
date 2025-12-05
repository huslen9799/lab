import sqlite3

DB_FILE = "database2.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

class Branch:
    def __init__(self, id=None, bname=None):
        self.id = id
        self.bname = bname

    @staticmethod
    def all():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM Branch").fetchall()
        conn.close()
        return [Branch(row['id'], row['bname']) for row in rows]

    @staticmethod
    def get(branch_id):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM Branch WHERE id=?", (branch_id,)).fetchone()
        conn.close()
        if row:
            return Branch(row['id'], row['bname'])
        return None

    def save(self):
        conn = get_db_connection()
        if self.id:  # Update
            conn.execute("UPDATE Branch SET bname=? WHERE id=?", (self.bname, self.id))
        else:  # Insert
            cursor = conn.execute("INSERT INTO Branch (bname) VALUES (?)", (self.bname,))
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def delete(self):
        conn = get_db_connection()
        conn.execute("DELETE FROM Branch WHERE id=?", (self.id,))
        conn.commit()
        conn.close()

class Worker:
    def __init__(self, id=None, wname=None, bid=None):
        self.id = id
        self.wname = wname
        self.bid = bid

    @staticmethod
    def all():
        conn = get_db_connection()
        rows = conn.execute("""
            SELECT Worker.id, Worker.wname, Branch.bname, Worker.bid 
            FROM Worker LEFT JOIN Branch ON Worker.bid = Branch.id
        """).fetchall()
        conn.close()
        return [Worker(row['id'], row['wname'], row['bid']) for row in rows]

    @staticmethod
    def get(worker_id):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM Worker WHERE id=?", (worker_id,)).fetchone()
        conn.close()
        if row:
            return Worker(row['id'], row['wname'], row['bid'])
        return None

    def save(self):
        conn = get_db_connection()
        if self.id:  # Update
            conn.execute("UPDATE Worker SET wname=?, bid=? WHERE id=?", (self.wname, self.bid, self.id))
        else:  # Insert
            cursor = conn.execute("INSERT INTO Worker (wname, bid) VALUES (?, ?)", (self.wname, self.bid))
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def delete(self):
        conn = get_db_connection()
        conn.execute("DELETE FROM Worker WHERE id=?", (self.id,))
        conn.commit()
        conn.close()
