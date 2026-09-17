"""
Compatibility module re-exporting from dedicated top-level database/ folder.
"""
from database.db import get_db, close_db, init_db, query_db, execute_db, DB_DIR, DEFAULT_DB_FILE

__all__ = ['get_db', 'close_db', 'init_db', 'query_db', 'execute_db', 'DB_DIR', 'DEFAULT_DB_FILE']
