"""
visualization.py
-----------------
Builds every Plotly chart shown on the Dashboard page:
  - Top Rated Movies            (bar)
  - Highest Revenue Movies      (bar)
  - Genre Distribution          (pie)
  - Popularity Analysis         (scatter)
  - Average Rating by Genre     (bar)
  - Movies Released Per Year    (line)
  - Top 10 Popular Movies       (horizontal bar)
"""

import os
import sys

import pandas as pd
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.create_database import get_connection  # noqa: E402

DARK_TEMPLATE = "plotly_dark"
ACCENT_COLOR = "#E50914"


def load_movies_dataframe():
    """Load the full movies table into a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM movies;", conn)
    conn.close()

    if df.empty:
        return df

    # Clean up types
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["release_year"] = df["release_date"].dt.year
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
    df["runtime"] = pd.to_numeric(df["runtime"], errors="coerce").fillna(0)
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)
    df = df.drop_duplicates(subset="movie_id")
    return df


def top_rated_bar_chart(df, top_n=10):
    top = df.sort_values("rating", ascending=False).head(top_n)
    fig = px.bar(
        top, x="title", y="rating", color="rating",
        color_continuous_scale="Reds", template=DARK_TEMPLATE,
        title=f"Top {top_n} Rated Movies",
    )
    fig.update_layout(xaxis_title="Movie", yaxis_title="Rating", showlegend=False)
    return fig


def highest_revenue_bar_chart(df, top_n=10):
    top = df[df["revenue"] > 0].sort_values("revenue", ascending=False).head(top_n)
    fig = px.bar(
        top, x="title", y="revenue", color="revenue",
        color_continuous_scale="Blues", template=DARK_TEMPLATE,
        title=f"Top {top_n} Highest Revenue Movies",
    )
    fig.update_layout(xaxis_title="Movie", yaxis_title="Revenue (USD)", showlegend=False)
    return fig


def genre_distribution_pie(df):
    genre_series = df["genre"].dropna().str.split(", ").explode()
    genre_counts = genre_series.value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]
    fig = px.pie(
        genre_counts, names="genre", values="count",
        template=DARK_TEMPLATE, title="Genre Distribution", hole=0.35,
    )
    return fig


def popularity_scatter(df):
    fig = px.scatter(
        df, x="popularity", y="rating", size="vote_count", color="genre",
        hover_name="title", template=DARK_TEMPLATE,
        title="Popularity vs Rating",
    )
    fig.update_layout(xaxis_title="Popularity", yaxis_title="Rating")
    return fig


def average_rating_by_genre_bar(df):
    genre_df = df[["genre", "rating"]].dropna()
    genre_df = genre_df.assign(genre=genre_df["genre"].str.split(", ")).explode("genre")
    avg_by_genre = (
        genre_df.groupby("genre")["rating"].mean().reset_index().sort_values("rating", ascending=False)
    )
    fig = px.bar(
        avg_by_genre, x="genre", y="rating", color="rating",
        color_continuous_scale="Oranges", template=DARK_TEMPLATE,
        title="Average Rating by Genre",
    )
    fig.update_layout(xaxis_title="Genre", yaxis_title="Average Rating", showlegend=False)
    return fig


def movies_per_year_line(df):
    year_counts = df.dropna(subset=["release_year"]).groupby("release_year").size().reset_index(name="count")
    year_counts["release_year"] = year_counts["release_year"].astype(int)
    fig = px.line(
        year_counts, x="release_year", y="count", markers=True,
        template=DARK_TEMPLATE, title="Movies Released Per Year",
    )
    fig.update_layout(xaxis_title="Year", yaxis_title="Number of Movies")
    return fig


def top_10_popular_horizontal_bar(df):
    top = df.sort_values("popularity", ascending=False).head(10).sort_values("popularity")
    fig = px.bar(
        top, x="popularity", y="title", orientation="h",
        color="popularity", color_continuous_scale="Viridis",
        template=DARK_TEMPLATE, title="Top 10 Popular Movies",
    )
    fig.update_layout(xaxis_title="Popularity", yaxis_title="Movie", showlegend=False)
    return fig
