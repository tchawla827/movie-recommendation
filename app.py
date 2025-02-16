"""
Author: Tavish Chawla
Contact: tchawla827@gmail.com
Description: A movie recommender system with IMDb ratings and links.
"""

import streamlit as st
import pickle
import requests

# Set up page configuration
st.set_page_config(
    page_title="Movie Recommender",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Dark Theme CSS ---
custom_css = """
<style>
    /* Set dark background */
    .main {
        background-color: #121212;
        color: #ffffff;
    }
    /* Style the header */
    h1 {
        color: #ffffff;
        text-align: center;
        padding: 1rem;
        margin-bottom: 0;
    }
    /* Movie details styling */
    .movie-container {
        text-align: center;
    }
    .movie-title {
        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
    }
    .movie-rating {
        font-size: 16px;
        color: #ffcc00;
        margin-bottom: 0.5rem;
    }
    .imdb-link {
        font-size: 14px;
        text-align: center;
        display: block;
        color: #1DB954;
        text-decoration: none;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    img {
        border-radius: 8px;
        max-width: 100%;
        height: auto;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- API Key ---
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# --- Functions ---

def fetch_movie_details(movie_id: int):
    """
    Fetch movie details including poster, IMDb rating, and IMDb ID from TMDb API.
    """
    api_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    response = requests.get(api_url, params=params).json()
    
    # Extract required details
    poster_path = response.get("poster_path", "")
    imdb_id = response.get("imdb_id", "")
    rating = response.get("vote_average", "N/A")  # IMDb rating (from TMDb)
    
    # Generate full URLs
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    imdb_url = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"

    return poster_url, rating, imdb_url

def generate_recommendations(selected_movie: str, movie_data, similarity_matrix):
    """
    Generates movie recommendations based on a selected movie title.
    Returns lists of recommended movie details: title, poster, rating, and IMDb link.
    """
    idx = movie_data[movie_data['title'] == selected_movie].index[0]

    # Sort by similarity scores
    similarity_scores = list(enumerate(similarity_matrix[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    recommended_movies = []
    
    for i in similarity_scores[1:6]:  # Skip the first one because it's the same movie
        movie_id = movie_data.iloc[i[0]].movie_id
        title = movie_data.iloc[i[0]].title
        poster_url, rating, imdb_url = fetch_movie_details(movie_id)
        
        recommended_movies.append({
            "title": title,
            "poster_url": poster_url,
            "rating": rating,
            "imdb_url": imdb_url
        })

    return recommended_movies


# --- Load data from pickles ---
@st.cache_data
def load_assets():
    with open("artifacts/movie_list.pkl", "rb") as f:
        movies_df = pickle.load(f)
    with open("artifacts/similarity.pkl", "rb") as f:
        similarity_df = pickle.load(f)
    return movies_df, similarity_df

movie_data, similarity_matrix = load_assets()

# --- UI Components ---

st.title("🎬 Movie Recommender System")

# Dropdown for movie selection
user_choice = st.selectbox(
    "🔍 Search or select a movie:",
    movie_data["title"].values
)

# Button to trigger recommendations
if st.button("🎥 Recommend"):
    recommended_movies = generate_recommendations(user_choice, movie_data, similarity_matrix)

    # Display recommendations in columns
    col_count = 5
    cols = st.columns(col_count)

    for index, col in enumerate(cols):
        if index < len(recommended_movies):
            movie = recommended_movies[index]
            with col:
                st.image(movie["poster_url"])  # Display poster
                st.markdown(f"<div class='movie-title'>{movie['title']}</div>", unsafe_allow_html=True)  # Name below poster
                st.markdown(f"<div class='movie-rating'>⭐ IMDb: {movie['rating']}</div>", unsafe_allow_html=True)  # Rating below name
                st.markdown(f"<a class='imdb-link' href='{movie['imdb_url']}' target='_blank'>🔗 IMDb Page</a>", unsafe_allow_html=True)  # IMDb link
