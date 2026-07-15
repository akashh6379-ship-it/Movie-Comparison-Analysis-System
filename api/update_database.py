"""
update_database.py
-------------------
Takes movie dictionaries fetched from TMDb and inserts/updates them in
SQLite (UPSERT). Also provides a background scheduler that refreshes
the database automatically every N hours (see AUTO_REFRESH_HOURS in
api/config.py) without blocking the Streamlit UI.
"""

import os
import sys
import threading
import time
from datetime import datetime

import schedule

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.create_database import get_connection, create_database  # noqa: E402
from api.fetch_movies import fetch_all_categories  # noqa: E402
from api.config import AUTO_REFRESH_HOURS  # noqa: E402

UPSERT_SQL = """
INSERT INTO movies (
    movie_id, title, overview, genre, language, release_date, runtime,
    rating, vote_count, popularity, budget, revenue, status,
    poster_url, backdrop_url, category, last_updated
) VALUES (
    :movie_id, :title, :overview, :genre, :language, :release_date, :runtime,
    :rating, :vote_count, :popularity, :budget, :revenue, :status,
    :poster_url, :backdrop_url, :category, :last_updated
)
ON CONFLICT(movie_id) DO UPDATE SET
    title=excluded.title,
    overview=excluded.overview,
    genre=excluded.genre,
    language=excluded.language,
    release_date=excluded.release_date,
    runtime=excluded.runtime,
    rating=excluded.rating,
    vote_count=excluded.vote_count,
    popularity=excluded.popularity,
    budget=excluded.budget,
    revenue=excluded.revenue,
    status=excluded.status,
    poster_url=excluded.poster_url,
    backdrop_url=excluded.backdrop_url,
    category=excluded.category,
    last_updated=excluded.last_updated;
"""


def upsert_movies(movies):
    """Insert new movies or update existing ones (matched by movie_id)."""
    if not movies:
        return 0

    now = datetime.now().isoformat(timespec="seconds")
    for movie in movies:
        movie["last_updated"] = now

    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(UPSERT_SQL, movies)
    conn.commit()
    conn.close()
    return len(movies)


def refresh_all_data(verbose=True):
    """Fetch every category from TMDb and upsert into SQLite."""
    create_database()
    movies = fetch_all_categories()
    count = upsert_movies(movies)
    if verbose:
        print(f"[update_database] Refreshed {count} movie records at "
              f"{datetime.now().isoformat(timespec='seconds')}")
    return count


def database_is_empty():
    """Check whether the movies table currently has zero rows."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM movies;")
    (count,) = cursor.fetchone()
    conn.close()
    return count == 0


def _safe_refresh_job():
    """Wrapper so a failed refresh never kills the scheduler thread."""
    try:
        refresh_all_data()
    except Exception as error:
        print(f"[update_database] Scheduled refresh failed: {error}")


def _scheduler_loop():
    """Runs forever in a background thread, checking the `schedule` queue."""
    schedule.every(AUTO_REFRESH_HOURS).hours.do(_safe_refresh_job)
    while True:
        schedule.run_pending()
        time.sleep(60)  # check once a minute


def start_background_scheduler():
    """
    Launch a daemon thread that refreshes the database every
    AUTO_REFRESH_HOURS hours (via the `schedule` library).
    Safe to call once per app session.
    """
    thread = threading.Thread(target=_scheduler_loop, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    refresh_all_data()
