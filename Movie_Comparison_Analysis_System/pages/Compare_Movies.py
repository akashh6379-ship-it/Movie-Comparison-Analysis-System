"""
Compare_Movies.py
------------------
Lets the user pick two movies and compares them across rating,
revenue, popularity, runtime, vote count, and release date.
"""

import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.visualization import load_movies_dataframe  # noqa: E402
from analysis.comparison import compare_movies, build_comparison_chart, build_release_date_note  # noqa: E402

st.set_page_config(page_title="Compare Movies", page_icon="⚖️", layout="wide")
st.title("⚖️ Movie Comparison")
st.caption("Compare any two movies side by side")

df = load_movies_dataframe()

if df.empty:
    st.info("No movie data available yet. Refresh data from the Home page first.")
else:
    titles = sorted(df["title"].dropna().unique().tolist())

    col1, col2 = st.columns(2)
    with col1:
        movie_a_title = st.selectbox("Select first movie", titles, index=0, key="movie_a")
    with col2:
        default_b_index = 1 if len(titles) > 1 else 0
        movie_b_title = st.selectbox("Select second movie", titles, index=default_b_index, key="movie_b")

    if movie_a_title == movie_b_title:
        st.warning("Please select two different movies to compare.")
    else:
        comparison_df, movie_a, movie_b = compare_movies(movie_a_title, movie_b_title)

        if comparison_df is None:
            st.error("Could not find one of the selected movies in the database.")
        else:
            poster_col1, vs_col, poster_col2 = st.columns([2, 1, 2])
            with poster_col1:
                if movie_a["poster_url"]:
                    st.image(movie_a["poster_url"], use_container_width=True)
                st.markdown(f"### {movie_a['title']}")
            with vs_col:
                st.markdown("<h2 style='text-align:center; margin-top:80px;'>VS</h2>", unsafe_allow_html=True)
            with poster_col2:
                if movie_b["poster_url"]:
                    st.image(movie_b["poster_url"], use_container_width=True)
                st.markdown(f"### {movie_b['title']}")

            st.markdown(build_release_date_note(movie_a, movie_b))

            fig = build_comparison_chart(comparison_df, movie_a["title"], movie_b["title"])
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📊 View raw comparison data"):
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)
