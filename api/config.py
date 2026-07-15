"""
config.py
----------
Central configuration for the TMDb API connection.

Get a free API key here: https://www.themoviedb.org/settings/api
Then either:
  1) Set it as an environment variable named TMDB_API_KEY, OR
  2) Paste it directly into TMDB_API_KEY below (not recommended for shared code).
"""

import os

# ---------------------------------------------------------------------------
# TMDb credentials
# ---------------------------------------------------------------------------
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "PASTE_YOUR_TMDB_API_KEY_")

# TMDb base API URL
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Base URL used to build full poster/backdrop image links.
# "w500" = 500px wide image. Other sizes: w92, w154, w185, w342, w780, original
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w1280"

# Default language / region for results
DEFAULT_LANGUAGE = "en-US"
DEFAULT_REGION = "US"

# How many result pages to pull per category (20 movies per TMDb page).
# Keep this small to avoid hitting API rate limits during development.
MAX_PAGES_PER_CATEGORY = 30

# How often (in hours) the app should automatically refresh data from TMDb.
AUTO_REFRESH_HOURS = 24

# Path to the SQLite database file (relative to project root).
DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "movie_database.db",
)
