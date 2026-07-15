"""
Current_Movies.py
------------------
Displays movies currently playing in theaters, pulled live from TMDb
via the local SQLite cache.
"""

import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.visualization import load_movies_dataframe  # noqa: E402

st.set_page_config(page_title="Current Movies", page_icon="🎥", layout="wide")
st.title("🎥 Current Movies")
st.caption("Now playing in theaters")

df = load_movies_dataframe()
current_df = df[df["category"] == "current"] if not df.empty else df

if current_df.empty:
    st.info("No current movies found. Try refreshing data from the Home page.")
else:
    sort_option = st.selectbox(
        "Sort by", ["Rating (High to Low)", "Popularity (High to Low)", "Release Date (Newest)"]
    )
    if sort_option == "Rating (High to Low)":
        current_df = current_df.sort_values("rating", ascending=False)
    elif sort_option == "Popularity (High to Low)":
        current_df = current_df.sort_values("popularity", ascending=False)
    else:
        current_df = current_df.sort_values("release_date", ascending=False)

    cols = st.columns(4)
    for idx, (_, movie) in enumerate(current_df.iterrows()):
        col = cols[idx % 4]
        with col:
            if movie["poster_url"]:
                st.image(movie["poster_url"], use_container_width=True)
            st.markdown(f"**{movie['title']}**")
            st.caption(f"🎭 {movie['genre'] or 'N/A'}")
            st.caption(f"📅 {movie['release_date'] or 'N/A'}")
            st.caption(f"⭐ {movie['rating']:.1f} • 🔥 {movie['popularity']:.0f}")
            st.markdown("---")
