# 🎬 Movie Comparison and Analysis System

A professional web application that automatically collects **live movie
data from the TMDb API**, stores it in a **SQLite database**, analyzes it
with **Pandas**, and displays **interactive dashboards** built with
**Streamlit** and **Plotly** — no manual CSV uploads, ever.

---

## ✨ Features

- **Automatic data collection** — pulls Current, Upcoming, Popular, and
  Top Rated movies from TMDb on first launch and every 24 hours after.
- **Home Page** — total movies, average rating, total revenue, highest
  rated movie, live search, and latest posters.
- **Current Movies** — poster, name, genre, release date, rating, popularity.
- **Upcoming Movies** — poster, release date, genre, overview.
- **Movie Comparison** — compare any two movies on rating, revenue,
  popularity, runtime, release date, and vote count with a bar chart.
- **Dashboard** — 7 interactive charts: Top Rated, Highest Revenue,
  Genre Distribution, Popularity Analysis, Average Rating by Genre,
  Movies per Year, Top 10 Popular Movies.
- **Search** — by movie name, genre, release year, or language.
- **Dark, Netflix/IMDb-inspired UI.**

---

## 📁 Project Structure

```
Movie_Comparison_Analysis_System/
│
├── app.py                     # Main entry point (Home page + init)
├── requirements.txt
├── README.md
│
├── api/
│   ├── config.py              # TMDb API key & settings
│   ├── fetch_movies.py        # All TMDb API calls
│   ├── update_database.py     # Insert/update logic + 24hr scheduler
│
├── database/
│   ├── create_database.py     # Creates SQLite schema
│   ├── movie_database.db      # Created automatically on first run
│
├── analysis/
│   ├── comparison.py          # Two-movie comparison logic
│   ├── visualization.py       # All Plotly chart builders
│
├── pages/                     # Streamlit auto-detects these as extra pages
│   ├── Current_Movies.py
│   ├── Upcoming_Movies.py
│   ├── Compare_Movies.py
│   ├── Dashboard.py
│
├── images/
└── assets/
```

> **Note:** Streamlit automatically turns every file inside `pages/`
> into a sidebar page, with `app.py` itself serving as the **Home** page.
> That's why there's no separate `pages/Home.py` — its content lives in
> `app.py` to avoid a duplicate "Home" entry in the sidebar.

---

## 🗄️ Database Schema (`movies` table)

| Column        | Type    | Description                          |
|---------------|---------|---------------------------------------|
| movie_id      | INTEGER | TMDb movie ID (primary key)          |
| title         | TEXT    | Movie title                          |
| overview      | TEXT    | Plot summary                         |
| genre         | TEXT    | Comma-separated genre names          |
| language      | TEXT    | Original language code               |
| release_date  | TEXT    | YYYY-MM-DD                           |
| runtime       | INTEGER | Minutes                              |
| rating        | REAL    | TMDb average vote                    |
| vote_count    | INTEGER | Number of votes                      |
| popularity    | REAL    | TMDb popularity score                |
| budget        | INTEGER | Production budget (USD)              |
| revenue       | INTEGER | Box office revenue (USD)             |
| status        | TEXT    | Released / Upcoming / etc.           |
| poster_url    | TEXT    | Full poster image URL                |
| backdrop_url  | TEXT    | Full backdrop image URL              |
| category      | TEXT    | current / upcoming / popular / top_rated |
| last_updated  | TEXT    | Timestamp of last refresh            |

---

## ⚙️ Setup Instructions

### 1. Get a free TMDb API key
Sign up at https://www.themoviedb.org/signup, then generate a key at
https://www.themoviedb.org/settings/api

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
Open `api/config.py` and either:
- paste your key into `TMDB_API_KEY`, **or**
- set an environment variable before running:
```bash
export TMDB_API_KEY="your_key_here"      # macOS/Linux
setx TMDB_API_KEY "your_key_here"        # Windows
```

### 4. Run the app
```bash
streamlit run app.py
```

The first launch will automatically create `database/movie_database.db`
and download live movie data — no manual steps needed. After that, the
app refreshes itself every 24 hours in the background, and you can also
click **"🔄 Refresh Data Now"** in the sidebar any time.

---

## 🧠 How It Works

1. **`app.py`** creates the database (if missing) and, if it's empty,
   calls `refresh_all_data()` to do the first TMDb pull. It then starts
   a background thread (`start_background_scheduler`) using the
   `schedule` library to repeat that pull every `AUTO_REFRESH_HOURS`
   (default: 24).
2. **`api/fetch_movies.py`** calls TMDb's `now_playing`, `upcoming`,
   `popular`, and `top_rated` endpoints, then enriches each movie with
   budget/revenue/runtime from the `/movie/{id}` details endpoint.
3. **`api/update_database.py`** performs an `INSERT ... ON CONFLICT
   DO UPDATE` (UPSERT) for every movie, so re-running never creates
   duplicates — it just refreshes existing rows.
4. **`analysis/visualization.py`** loads the whole table into a Pandas
   DataFrame and builds all 7 Plotly Dashboard charts.
5. **`analysis/comparison.py`** looks up two chosen movies and builds a
   grouped bar chart across five key metrics.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| "No movie data available yet" | Confirm your TMDb API key in `api/config.py`, then click **Refresh Data Now**. |
| `requests.exceptions.HTTPError: 401` | Your API key is missing or invalid. |
| Slow first load | The app fetches details for every movie individually; reduce `MAX_PAGES_PER_CATEGORY` in `api/config.py` for faster (smaller) pulls. |
| Charts look empty | Genre/rating charts need at least a few dozen movies — run **Refresh Data Now** if the DB was just created. |

---

## 📚 Tech Stack

Python • Streamlit • SQLite • TMDb API • Pandas • Plotly • Matplotlib • Schedule

---

## 🎓 Academic Note

This project structure is designed to be viva-ready: clean separation
of concerns (`api/`, `database/`, `analysis/`, `pages/`), commented
code, and a database-first (not CSV-first) architecture that
demonstrates live API integration, ETL (extract-transform-load) into
SQLite, and interactive data visualization.
