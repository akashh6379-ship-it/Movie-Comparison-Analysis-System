"""
comparison.py
-------------
Functions for pulling two movies from the database and comparing
them across rating, revenue, popularity, runtime, and vote count.
"""

import os
import sys

import pandas as pd
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.create_database import get_connection  # noqa: E402


def get_movie_by_title(title):
    """Return a single movie row (as a dict) matching the given title exactly."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM movies WHERE title = ? LIMIT 1;", conn, params=(title,)
    )
    conn.close()
    if df.empty:
        return None
    return df.iloc[0].to_dict()


def compare_movies(title_a, title_b):
    """
    Fetch two movies and return a tidy comparison DataFrame with columns:
    metric, movie A value, movie B value.
    """
    movie_a = get_movie_by_title(title_a)
    movie_b = get_movie_by_title(title_b)

    if not movie_a or not movie_b:
        return None, movie_a, movie_b

    metrics = ["rating", "revenue", "popularity", "runtime", "vote_count"]
    comparison_df = pd.DataFrame(
        {
            "metric": metrics,
            movie_a["title"]: [movie_a.get(m) or 0 for m in metrics],
            movie_b["title"]: [movie_b.get(m) or 0 for m in metrics],
        }
    )
    return comparison_df, movie_a, movie_b


def build_comparison_chart(comparison_df, title_a, title_b):
    """Build a grouped bar chart comparing two movies across all metrics."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name=title_a,
            x=comparison_df["metric"],
            y=comparison_df[title_a],
            marker_color="#E50914",  # Netflix red
        )
    )
    fig.add_trace(
        go.Bar(
            name=title_b,
            x=comparison_df["metric"],
            y=comparison_df[title_b],
            marker_color="#00A8E1",  # contrasting blue
        )
    )
    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        title=f"{title_a} vs {title_b}",
        xaxis_title="Metric",
        yaxis_title="Value",
        legend_title="Movie",
        height=500,
    )
    return fig


def build_release_date_note(movie_a, movie_b):
    """Return a plain-text sentence comparing release dates (not chartable)."""
    date_a = movie_a.get("release_date") or "Unknown"
    date_b = movie_b.get("release_date") or "Unknown"
    return f"**{movie_a['title']}** released on `{date_a}`  •  **{movie_b['title']}** released on `{date_b}`"
