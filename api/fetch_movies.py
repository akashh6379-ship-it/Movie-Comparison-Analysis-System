"""
fetch_movies.py
----------------
Handles all communication with the TMDb API:
  - now_playing   -> "Current Movies"
  - upcoming      -> "Upcoming Movies"
  - popular       -> "Popular Movies"
  - top_rated     -> "Top Rated Movies"

Each function returns a list of cleaned movie dictionaries ready to be
inserted into the SQLite database.
"""

import requests

from api.config import (
    TMDB_API_KEY,
    TMDB_BASE_URL,
    TMDB_IMAGE_BASE_URL,
    TMDB_BACKDROP_BASE_URL,
    DEFAULT_LANGUAGE,
    DEFAULT_REGION,
    MAX_PAGES_PER_CATEGORY,
)

# Simple in-memory cache so we don't hit the /genre endpoint repeatedly
_GENRE_MAP_CACHE = None


def _get_genre_map():
    """Fetch and cache the TMDb genre_id -> genre_name mapping."""
    global _GENRE_MAP_CACHE
    if _GENRE_MAP_CACHE is not None:
        return _GENRE_MAP_CACHE

    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/genre/movie/list",
            params={"api_key": TMDB_API_KEY, "language": DEFAULT_LANGUAGE},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json().get("genres", [])
        _GENRE_MAP_CACHE = {g["id"]: g["name"] for g in data}
    except requests.RequestException as error:
        print(f"[fetch_movies] Could not load genre list: {error}")
        _GENRE_MAP_CACHE = {}

    return _GENRE_MAP_CACHE


def _genre_ids_to_names(genre_ids):
    genre_map = _get_genre_map()
    names = [genre_map.get(gid, "") for gid in genre_ids]
    return ", ".join([n for n in names if n])


def _fetch_movie_details(movie_id):
    """Fetch extra fields (runtime, budget, revenue, status) for one movie."""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}",
            params={"api_key": TMDB_API_KEY, "language": DEFAULT_LANGUAGE},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print(f"[fetch_movies] Could not load details for movie {movie_id}: {error}")
        return {}


def _clean_movie(raw, category, fetch_details=True):
    """Convert a raw TMDb movie JSON object into our database row format."""
    movie_id = raw.get("id")
    details = _fetch_movie_details(movie_id) if fetch_details else {}

    poster_path = raw.get("poster_path")
    backdrop_path = raw.get("backdrop_path")

    return {
        "movie_id": movie_id,
        "title": raw.get("title") or raw.get("original_title") or "Untitled",
        "overview": raw.get("overview", ""),
        "genre": _genre_ids_to_names(raw.get("genre_ids", [])),
        "language": raw.get("original_language", ""),
        "release_date": raw.get("release_date", ""),
        "runtime": details.get("runtime"),
        "rating": raw.get("vote_average", 0.0),
        "vote_count": raw.get("vote_count", 0),
        "popularity": raw.get("popularity", 0.0),
        "budget": details.get("budget", 0),
        "revenue": details.get("revenue", 0),
        "status": details.get("status", ""),
        "poster_url": f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else "",
        "backdrop_url": f"{TMDB_BACKDROP_BASE_URL}{backdrop_path}" if backdrop_path else "",
        "category": category,
    }


def _fetch_category(endpoint, category, extra_params=None, max_pages=MAX_PAGES_PER_CATEGORY):
    """Generic helper to page through a TMDb list endpoint."""
    movies = []
    params = {
        "api_key": TMDB_API_KEY,
        "language": DEFAULT_LANGUAGE,
        "region": DEFAULT_REGION,
    }
    if extra_params:
        params.update(extra_params)

    for page in range(1, max_pages + 1):
        params["page"] = page
        try:
            response = requests.get(f"{TMDB_BASE_URL}{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            print(f"[fetch_movies] Error fetching {category} page {page}: {error}")
            break

        results = payload.get("results", [])
        if not results:
            break

        for raw_movie in results:
            movies.append(_clean_movie(raw_movie, category))

        if page >= payload.get("total_pages", 1):
            break

    return movies


def fetch_current_movies():
    """Movies currently in theaters ('Now Playing')."""
    return _fetch_category("/movie/now_playing", "current")


def fetch_upcoming_movies():
    """Movies scheduled for future release."""
    return _fetch_category("/movie/upcoming", "upcoming")


def fetch_popular_movies():
    """Trending / most popular movies right now."""
    return _fetch_category("/movie/popular", "popular")


def fetch_top_rated_movies():
    """All-time top rated movies on TMDb."""
    return _fetch_category("/movie/top_rated", "top_rated")


def fetch_all_categories():
    """Fetch all four categories in one call. Returns a combined list."""
    all_movies = []
    all_movies.extend(fetch_current_movies())
    all_movies.extend(fetch_upcoming_movies())
    all_movies.extend(fetch_popular_movies())
    all_movies.extend(fetch_top_rated_movies())
    return all_movies


def search_movies_online(query):
    """Search TMDb directly for a movie name (used as a fallback to local search)."""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/search/movie",
            params={"api_key": TMDB_API_KEY, "language": DEFAULT_LANGUAGE, "query": query},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return [_clean_movie(r, "search", fetch_details=False) for r in results]
    except requests.RequestException as error:
        print(f"[fetch_movies] Search error: {error}")
        return []
