import sqlite3
import os
from pathlib import Path
from flask import g, current_app

DB_DIR = Path(__file__).resolve().parent
DEFAULT_DB_FILE = str(DB_DIR / 'chroma_blend.db')

def get_db(custom_path=None):
    """Open a new database connection if there is none yet for the current app context."""
    if custom_path:
        db_path = custom_path
    elif current_app:
        db_path = current_app.config.get('DATABASE_PATH', DEFAULT_DB_FILE)
    else:
        db_path = DEFAULT_DB_FILE

    # Ensure parent directory exists
    db_parent = Path(db_path).parent
    db_parent.mkdir(parents=True, exist_ok=True)

    # If within Flask application context, use flask.g
    try:
        if 'db' not in g:
            g.db = sqlite3.connect(db_path)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON;")
        return g.db
    except RuntimeError:
        # Outside application context (e.g. standalone scripts or migrations)
        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON;")
        return con

def close_db(e=None):
    """Close the database at the end of the request."""
    try:
        db = g.pop('db', None)
        if db is not None:
            db.close()
    except RuntimeError:
        pass

def init_db(app=None, custom_path=None):
    """Initialize the database from schema.sql."""
    schema_path = DB_DIR / 'schema.sql'
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    if app:
        with app.app_context():
            db = get_db(custom_path)
            db.executescript(schema_sql)
            db.commit()
    else:
        db = get_db(custom_path)
        db.executescript(schema_sql)
        db.commit()
        db.close()

def query_db(query, args=(), one=False):
    """Helper to query the database and return dictionaries."""
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if one:
        return dict(rv[0]) if rv else None
    return [dict(row) for row in rv]

def execute_db(query, args=()):
    """Helper to execute an insert, update, or delete."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    row_count = cur.rowcount
    cur.close()
    return {'last_id': last_id, 'row_count': row_count}
