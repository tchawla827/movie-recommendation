"""
Author: Tavish Chawla
Contact: tchawla827@gmail.com
Description: A modern movie recommender system
"""

import pickle
from pathlib import Path
from typing import Optional

import streamlit as st
import requests
import numpy as np
import pandas as pd

# Try to import gdown (required for Drive downloads)
try:
    import gdown
except Exception:
    gdown = None

# ==============================
# Page configuration & Styling
# ==============================
st.set_page_config(
    page_title="Movie Recommender",
    layout="wide",
    initial_sidebar_state="collapsed"
)

custom_css = """
<style>
    .main { background-color: #121212; color: #ffffff; }
    h1 { text-align: center; color: #ffffff; padding: 1rem; }
    .movie-container {
        text-align: center; transition: transform 0.2s ease-in-out;
        display: flex; flex-direction: column; align-items: center;
        justify-content: space-between; height: 460px; padding-bottom: 20px;
    }
    .movie-container:hover { transform: scale(1.05); }
    .movie-title { font-size: 18px; font-weight: bold; color: #ffffff; margin-top: 0.5rem; }
    .movie-rating { font-size: 14px; color: #ffcc00; margin-bottom: 0.5rem; }
    .movie-genre { font-size: 14px; color: #dddddd; margin-bottom: 0.5rem; }
    .button-container { margin-top: auto; padding-top: 10px; display: flex; justify-content: center; width: 100%; }
    .trailer-button {
        background: linear-gradient(to right, #007BFF, #0056D2);
        color: white; padding: 10px 18px; border-radius: 20px; font-weight: bold; text-decoration: none;
        font-size: 14px; display: inline-block; transition: transform 0.2s ease-in-out, background 0.3s ease-in-out;
        box-shadow: 0px 4px 10px rgba(0, 123, 255, 0.5); text-align: center;
    }
    .trailer-button:hover { background: linear-gradient(to right, #0056D2, #003E99); transform: scale(1.1);
        box-shadow: 0px 6px 12px rgba(0, 123, 255, 0.7); }
    img { border-radius: 10px; max-width: 100%; height: auto; }
    .footer {
        position: fixed; bottom: 0; width: 100%; background-color: #1a1a1a; color: white;
        text-align: center; padding: 10px; font-size: 14px;
    }
    .footer a { color: #1DB954; text-decoration: none; font-weight: bold; }
    .footer a:hover { text-decoration: underline; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================
# Secrets (REQUIRED)
# ==============================
def require_secret(name: str) -> str:
    try:
        return st.secrets[name]
    except Exception:
        st.error(
            f"Missing secret `{name}`. Create `.streamlit/secrets.toml` locally "
            f"or set Secrets in Streamlit Cloud. "
            f"Example:\n\nTMDB_API_KEY=\"...\"\nGDRIVE_FILE_ID=\"...\""
        )
        st.stop()

TMDB_API_KEY: str = require_secret("TMDB_API_KEY")
GDRIVE_SIMILARITY_FILE_ID: str = require_secret("GDRIVE_FILE_ID")
GDRIVE_MOVIE_LIST_FILE_ID: Optional[str] = st.secrets.get("MOVIE_LIST_FILE_ID", None)

# ==============================
# Artifact paths
# ==============================
ARTIFACTS_DIR = Path("artifacts")
SIMILARITY_PATH = ARTIFACTS_DIR / "similarity.pkl"
MOVIE_LIST_PATH = ARTIFACTS_DIR / "movie_list.pkl"

# ==============================
# Helpers
# ==============================
def _drive_download(file_id: str, dest: Path) -> None:
    """Download a file from Google Drive by file ID to dest using gdown."""
    if not file_id:
        raise ValueError("Google Drive file_id is empty.")
    if gdown is None:
        raise ImportError("gdown is not installed. Add 'gdown' to requirements.txt.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, str(dest), quiet=False)

def ensure_local_file(path: Path, file_id: Optional[str], label: str = "") -> Path:
    """Ensure local file exists; if missing and file_id given, download from Drive."""
    if path.exists():
        return path
    if file_id:
        with st.spinner(f"Downloading {label or path.name}..."):
            _drive_download(file_id, path)
        return path
    raise FileNotFoundError(
        f"Missing required artifact: {path}. Provide it locally or set a Drive file ID in secrets."
    )

# ==============================
# TMDB / Recommendation logic
# ==============================
def fetch_movie_details(movie_id: int):
    """Fetch poster, rating, imdb url, genres, and trailer from TMDb."""
    try:
        api_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": TMDB_API_KEY, "language": "en-US"}
        resp = requests.get(api_url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        poster_path = data.get("poster_path") or ""
        imdb_id = data.get("imdb_id") or ""
        rating = data.get("vote_average", "N/A")
        genres = ", ".join([g.get("name", "") for g in data.get("genres", []) if g.get("name")])

        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        imdb_url = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"

        # Trailer
        trailer_url = "#"
        vids = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/videos",
                            params=params, timeout=15)
        if vids.ok:
            v = vids.json()
            for video in v.get("results", []):
                if video.get("type") == "Trailer" and video.get("site") == "YouTube" and video.get("key"):
                    trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                    break

        return poster_url, rating, imdb_url, genres, trailer_url

    except Exception:
        # Fail silently with safe defaults
        return "", "N/A", "#", "", "#"

def generate_recommendations(selected_movie: str, movie_data, similarity_matrix):
    """Return list of dicts for top-5 similar movies to `selected_movie`."""
    idx = movie_data[movie_data['title'] == selected_movie].index[0]
    similarity_scores = list(enumerate(similarity_matrix[idx]))
    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    out = []
    for i in similarity_scores[1:6]:  # top-5
        movie_id = int(movie_data.iloc[i[0]].movie_id)
        title = str(movie_data.iloc[i[0]].title)
        poster_url, rating, imdb_url, genres, trailer_url = fetch_movie_details(movie_id)
        out.append({
            "title": title,
            "poster_url": poster_url,
            "rating": rating,
            "imdb_url": imdb_url,
            "genres": genres,
            "trailer_url": trailer_url
        })
    return out

# ==============================
# Load assets (pickles)
# ==============================
@st.cache_resource(show_spinner="Loading similarity matrix…")
def load_similarity():
    ensure_local_file(SIMILARITY_PATH, GDRIVE_SIMILARITY_FILE_ID, label="similarity.pkl")
    with open(SIMILARITY_PATH, "rb") as f:
        return pickle.load(f)

@st.cache_data(show_spinner="Loading movie list…")
def load_movies_df():
    if MOVIE_LIST_PATH.exists():
        with open(MOVIE_LIST_PATH, "rb") as f:
            return pickle.load(f)
    if GDRIVE_MOVIE_LIST_FILE_ID:
        ensure_local_file(MOVIE_LIST_PATH, GDRIVE_MOVIE_LIST_FILE_ID, label="movie_list.pkl")
        with open(MOVIE_LIST_PATH, "rb") as f:
            return pickle.load(f)
    raise FileNotFoundError(
        "Could not find 'artifacts/movie_list.pkl'. "
        "Add it locally or set MOVIE_LIST_FILE_ID in Streamlit secrets."
    )

# Instantiate cached assets
try:
    similarity_matrix = load_similarity()
except Exception as e:
    st.error(f"Failed to load similarity matrix: {e}")
    st.stop()

try:
    movie_data = load_movies_df()
except Exception as e:
    st.error(f"Failed to load movie list: {e}")
    st.stop()

# ==============================
# UI
# ==============================
st.title("🎬 Movie Recommender")

# Genre and year filters

genre_col = next((c for c in ["genres", "genre"] if c in movie_data.columns), None)
if genre_col:
    genre_series = movie_data[genre_col].fillna("").astype(str)
    all_genres = sorted(
        {
            g.strip()
            for cell in genre_series
            for g in cell.replace("|", ",").split(",")
            if g.strip()
        }
    )
else:
    genre_series = pd.Series([], dtype=str)
    all_genres = []


if "release_date" in movie_data.columns:
    year_series = pd.to_datetime(movie_data["release_date"], errors="coerce").dt.year
elif "year" in movie_data.columns:
    year_series = pd.to_numeric(movie_data["year"], errors="coerce")
else:
    year_series = pd.Series([], dtype="Int64")

year_min = int(year_series.min()) if not year_series.dropna().empty else 0
year_max = int(year_series.max()) if not year_series.dropna().empty else 0

selected_genres = st.multiselect("🎞️ Filter by genre:", all_genres)
year_range = (
    st.slider("📅 Release year:", year_min, year_max, (year_min, year_max))
    if year_min != year_max
    else (year_min, year_max)
)

mask = pd.Series(True, index=movie_data.index)

if selected_genres and not genre_series.empty:
    mask &= genre_series.apply(lambda x: any(g in x for g in selected_genres))
if year_min != year_max:
    mask &= year_series.between(year_range[0], year_range[1])

filtered_idx = np.flatnonzero(mask.to_numpy())
filtered_movies = movie_data.iloc[filtered_idx].reset_index(drop=True)

filtered_similarity = similarity_matrix[np.ix_(filtered_idx, filtered_idx)]

titles = (
    filtered_movies["title"].values
    if "title" in getattr(filtered_movies, "columns", [])
    else []
)
if len(titles) == 0:
    st.warning("No movies match selected filters.")
    st.stop()

user_choice = st.selectbox("🔍 Search for a movie:", titles)

if st.button("🎥 Recommend"):
    if user_choice not in titles:
        st.error("⚠️ Movie not found. Please check spelling.")
    else:
        recs = generate_recommendations(user_choice, filtered_movies, filtered_similarity)
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            if idx < len(recs):
                m = recs[idx]
                with col:
                    if m["poster_url"]:
                        st.markdown(
                            f'<a href="{m["imdb_url"]}" target="_blank">'
                            f'<img src="{m["poster_url"]}" alt="{m["title"]}"></a>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<a href="{m["imdb_url"]}" target="_blank">'
                            f'<div class="movie-container">No poster available</div></a>',
                            unsafe_allow_html=True
                        )
                    st.markdown(f"<div class='movie-title'>{m['title']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='movie-rating'>⭐ IMDb: {m['rating']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='movie-genre'>{m['genres']}</div>", unsafe_allow_html=True)
                    st.markdown(
                        "<div class='button-container'>"
                        f"<a class='trailer-button' href='{m['trailer_url']}' target='_blank'>▶ Watch Trailer</a>"
                        "</div>",
                        unsafe_allow_html=True
                    )

# Footer
st.markdown(
    "<div class='footer'>Made by <b>Tavish Chawla</b> | 📧 "
    "<a href='mailto:tchawla827@gmail.com'>tchawla827@gmail.com</a></div>",
    unsafe_allow_html=True
)
