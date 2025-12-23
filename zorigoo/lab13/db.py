import sqlite3
from flask import g

DB_NAME = "MU.db"

def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db

def close_db(e=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()
