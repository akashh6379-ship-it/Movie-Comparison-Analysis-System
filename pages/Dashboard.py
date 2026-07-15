"""
Dashboard.py
------------
Full analytics dashboard with 7 interactive Plotly charts summarizing
the entire movie dataset.
"""

import os
import sys

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.visualization import (  # noqa: E402
    load_movies_dataframe,
    top_rated_bar_chart,
    highest_revenue_bar_chart,
    genre_distribution_pie,
    popularity_scatter,
    average_rating_by_genre_bar,
    movies_per_year_line,
    top_10_popular_horizontal_bar,
)

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Analytics Dashboard")
st.caption("Interactive insights across the entire movie dataset")

df = load_movies_dataframe()

if df.empty:
    st.info("No movie data available yet. Refresh data from the Home page first.")
else:
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.plotly_chart(top_rated_bar_chart(df), use_container_width=True)
    with row1_col2:
        st.plotly_chart(highest_revenue_bar_chart(df), use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.plotly_chart(genre_distribution_pie(df), use_container_width=True)
    with row2_col2:
        st.plotly_chart(popularity_scatter(df), use_container_width=True)

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        st.plotly_chart(average_rating_by_genre_bar(df), use_container_width=True)
    with row3_col2:
        st.plotly_chart(movies_per_year_line(df), use_container_width=True)

    st.plotly_chart(top_10_popular_horizontal_bar(df), use_container_width=True)
