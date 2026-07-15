"""
Upcoming_Movies.py
-------------------
Displays movies with future release dates, pulled live from TMDb.
"""

import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.visualization import load_movies_dataframe  # noqa: E402

st.set_page_config(page_title="Upcoming Movies", page_icon="🍿", layout="wide")
st.title("🍿 Upcoming Movies")
st.caption("Movies scheduled for future release")

df = load_movies_dataframe()
upcoming_df = df[df["category"] == "upcoming"] if not df.empty else df

if upcoming_df.empty:
    st.info("No upcoming movies found. Try refreshing data from the Home page.")
else:
    upcoming_df = upcoming_df.sort_values("release_date", ascending=True)

    for _, movie in upcoming_df.iterrows():
        col1, col2 = st.columns([1, 3])
        with col1:
            if movie["poster_url"]:
                st.image(movie["poster_url"], use_container_width=True)
        with col2:
            st.subheader(movie["title"])
            st.caption(f"📅 Release Date: {movie['release_date'] or 'TBA'}")
            st.caption(f"🎭 Genre: {movie['genre'] or 'N/A'}")
            st.write(movie["overview"] or "No overview available.")
        st.markdown("---")
