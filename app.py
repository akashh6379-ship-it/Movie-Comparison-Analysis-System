"""
app.py
------
Main entry point for the Movie Comparison and Analysis System.
This file:
  1. Sets global Streamlit page config + dark theme styling.
  2. Creates the SQLite database on first run.
  3. Fetches live data from TMDb automatically if the database is empty.
  4. Starts a background scheduler that refreshes data every 24 hours.
  5. Renders the Home page (Streamlit automatically adds every file
     inside pages/ as extra sidebar pages).
"""

import streamlit as st
import pandas as pd

from database.create_database import create_database
from api.update_database import (
    database_is_empty,
    refresh_all_data,
    start_background_scheduler,
)
from analysis.visualization import load_movies_dataframe

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Movie Comparison & Analysis System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Netflix/IMDb-style dark theme tweaks
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; color: #f5f5f5; }
    .metric-card {
        background-color: #181818;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2a2a2a;
    }
    h1, h2, h3 { color: #E50914; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# One-time app initialization (cached across reruns within a session)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def initialize_app():
    """Create DB, do the first data pull if needed, and start the scheduler."""
    create_database()
    if database_is_empty():
        with st.spinner("Connecting to TMDb and downloading movie data for the first time..."):
            refresh_all_data()
    start_background_scheduler()
    return True


initialize_app()

# ---------------------------------------------------------------------------
# Sidebar manual refresh control
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎬 Movie Analysis System")
    st.caption("Live data from TMDb • Auto-refreshes every 24 hours")
    if st.button("🔄 Refresh Data Now"):
        with st.spinner("Fetching latest movies from TMDb..."):
            count = refresh_all_data()
        st.success(f"Updated {count} movie records!")
        st.cache_data.clear()

# ---------------------------------------------------------------------------
# Home page content
# ---------------------------------------------------------------------------
st.title("🎬 Movie Comparison and Analysis System")
st.caption("Live movie intelligence powered by TMDb, SQLite, and Plotly")

df = load_movies_dataframe()

if df.empty:
    st.warning(
        "No movie data available yet. Check your TMDb API key in `api/config.py` "
        "and click **Refresh Data Now** in the sidebar."
    )
else:
    total_movies = df["movie_id"].nunique()
    avg_rating = round(df["rating"].mean(), 2)
    total_revenue = int(df["revenue"].sum())
    highest_rated = df.sort_values("rating", ascending=False).iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🎞️ Total Movies", f"{total_movies:,}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("⭐ Average Rating", f"{avg_rating} / 10")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💰 Total Revenue", f"${total_revenue:,}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🏆 Highest Rated", highest_rated["title"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Search box
    st.subheader("🔍 Search Movies")
    search_query = st.text_input(
        "Search by movie name, genre, release year, or language", ""
    )

    if search_query:
        query_lower = search_query.lower()
        results = df[
            df["title"].str.lower().str.contains(query_lower, na=False)
            | df["genre"].str.lower().str.contains(query_lower, na=False)
            | df["language"].str.lower().str.contains(query_lower, na=False)
            | df["release_year"].astype(str).str.contains(query_lower, na=False)
        ]
        st.write(f"Found **{len(results)}** matching movies")
        display_cols = ["title", "genre", "release_date", "rating", "popularity", "language"]
        st.dataframe(results[display_cols], use_container_width=True, hide_index=True)

    st.markdown("---")

    # Latest movie posters
    st.subheader("🆕 Latest Movie Posters")
    latest = df.sort_values("release_date", ascending=False).head(10)
    poster_cols = st.columns(5)
    for idx, (_, movie) in enumerate(latest.iterrows()):
        col = poster_cols[idx % 5]
        with col:
            if movie["poster_url"]:
                st.image(movie["poster_url"], use_container_width=True)
            st.caption(f"**{movie['title']}**")
