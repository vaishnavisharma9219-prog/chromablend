#!/usr/bin/env python3
"""
Standalone Database Initializer for Chroma Blend.
Creates all SQLite tables and indexes defined in schema.sql.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.db import init_db, DEFAULT_DB_FILE

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB_FILE
    print(f"Initializing database at: {target}")
    init_db(custom_path=target)
    print("Database initialization complete.")
