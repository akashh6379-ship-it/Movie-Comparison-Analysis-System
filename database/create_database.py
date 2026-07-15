"""
create_database.py
-------------------
Creates the SQLite database and the `movies` table if they do not
already exist. Safe to run multiple times (idempotent).
"""

import os
import sqlite3
import sys

# Allow running this file directly or importing it as a module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.config import DATABASE_PATH  # noqa: E402


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS movies (
    movie_id      INTEGER PRIMARY KEY,
    title         TEXT NOT NULL,
    overview      TEXT,
    genre         TEXT,
    language      TEXT,
    release_date  TEXT,
    runtime       INTEGER,
    rating        REAL,
    vote_count    INTEGER,
    popularity    REAL,
    budget        INTEGER,
    revenue       INTEGER,
    status        TEXT,
    poster_url    TEXT,
    backdrop_url  TEXT,
    category      TEXT,       -- current / upcoming / popular / top_rated
    last_updated  TEXT        -- timestamp of the last time this row was refreshed
);
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);",
    "CREATE INDEX IF NOT EXISTS idx_movies_genre ON movies(genre);",
    "CREATE INDEX IF NOT EXISTS idx_movies_release_date ON movies(release_date);",
    "CREATE INDEX IF NOT EXISTS idx_movies_category ON movies(category);",
]


def get_connection():
    """Return a SQLite connection to the project's database file."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")  # better concurrent read/write
    return conn


def create_database():
    """Create the movies table and helpful indexes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    for stmt in CREATE_INDEXES_SQL:
        cursor.execute(stmt)
    conn.commit()
    conn.close()
    print(f"Database ready at: {DATABASE_PATH}")


if __name__ == "__main__":
    create_database()
