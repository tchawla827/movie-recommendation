"""
Author: Tavish Chawla
Contact: tchawla827@gmail.com
Description: A modern movie recommender system 
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

# --- Dark Theme and Enhanced UI ---
custom_css = """
<style>
    .main {
        background-color: #121212;
        color: #ffffff;
    }
    h1 {
        text-align: center;
        color: #ffffff;
        padding: 1rem;
    }
    .movie-container {
        text-align: center;
        transition: transform 0.2s ease-in-out;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        height: 460px; /* Ensures uniform height for all movie cards */
        padding-bottom: 20px;
    }
    .movie-container:hover {
        transform: scale(1.05);
    }
    .movie-title {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
        margin-top: 0.5rem;
    }
    .movie-rating {
        font-size: 14px;
        color: #ffcc00;
        margin-bottom: 0.5rem;
    }
    .movie-genre {
        font-size: 14px;
        color: #dddddd;
        margin-bottom: 0.5rem;
    }
    .button-container {
        margin-top: auto;
        padding-top: 10px;
        display: flex;
        justify-content: center;
        width: 100%;
    }
    /* 🔹 Bright "Watch Trailer" Button */
    .trailer-button {
        background: linear-gradient(to right, #007BFF, #0056D2);
        color: white;
        padding: 10px 18px;
        border-radius: 20px;
        font-weight: bold;
        text-decoration: none;
        font-size: 14px;
        display: inline-block;
        transition: transform 0.2s ease-in-out, background 0.3s ease-in-out;
        box-shadow: 0px 4px 10px rgba(0, 123, 255, 0.5);
        text-align: center;
    }
    .trailer-button:hover {
        background: linear-gradient(to right, #0056D2, #003E99);
        transform: scale(1.1);
        box-shadow: 0px 6px 12px rgba(0, 123, 255, 0.7);
    }
    img {
        border-radius: 10px;
        max-width: 100%;
        height: auto;
    }
    /* 🔹 Footer Section */
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #1a1a1a;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 14px;
    }
    .footer a {
        color: #1DB954;
        text-decoration: none;
        font-weight: bold;
    }
    .footer a:hover {
        text-decoration: underline;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- API Key ---
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# --- Functions ---

def fetch_movie_details(movie_id: int):
    """
    Fetch movie details including poster, IMDb rating, IMDb ID, genres, and trailer from TMDb API.
    """
    api_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    response = requests.get(api_url, params=params).json()
    
    poster_path = response.get("poster_path", "")
    imdb_id = response.get("imdb_id", "")
    rating = response.get("vote_average", "N/A")
    genres = ", ".join([genre["name"] for genre in response.get("genres", [])])  # Extract genres
    
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    imdb_url = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "#"
    
    # Fetch trailer
    trailer_url = "#"
    videos = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/videos", params=params).json()
    for video in videos.get("results", []):
        if video["type"] == "Trailer" and video["site"] == "YouTube":
            trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
            break
    
    return poster_url, rating, imdb_url, genres, trailer_url

def generate_recommendations(selected_movie: str, movie_data, similarity_matrix):
    """
    Generates movie recommendations based on a selected movie title.
    Returns movie details: title, poster, rating, IMDb link, genres, and trailer.
    """
    idx = movie_data[movie_data['title'] == selected_movie].index[0]

    similarity_scores = list(enumerate(similarity_matrix[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    recommended_movies = []
    
    for i in similarity_scores[1:6]:  # Fetch top 5 movies
        movie_id = movie_data.iloc[i[0]].movie_id
        title = movie_data.iloc[i[0]].title
        poster_url, rating, imdb_url, genres, trailer_url = fetch_movie_details(movie_id)
        
        recommended_movies.append({
            "title": title,
            "poster_url": poster_url,
            "rating": rating,
            "imdb_url": imdb_url,
            "genres": genres,
            "trailer_url": trailer_url
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
st.title("🎬 Movie Recommender")

# --- 🔥 Improved Search Bar (Now Shows Available Movies) ---
user_choice = st.selectbox("🔍 Search for a movie:", movie_data["title"].values)

# Button to trigger recommendations
if st.button("🎥 Recommend"):
    if user_choice not in movie_data["title"].values:
        st.error("⚠️ Movie not found. Please check spelling.")
    else:
        recommended_movies = generate_recommendations(user_choice, movie_data, similarity_matrix)

        # Display recommendations in a 5-column grid
        cols = st.columns(5)

        for index, col in enumerate(cols):
            if index < len(recommended_movies):
                movie = recommended_movies[index]
                with col:
                    # Clickable Poster
                    st.markdown(f'<a href="{movie["imdb_url"]}" target="_blank">'
                                f'<img src="{movie["poster_url"]}" alt="{movie["title"]}"></a>',
                                unsafe_allow_html=True)
                    
                    # Title, Rating, Genres
                    st.markdown(f"<div class='movie-title'>{movie['title']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='movie-rating'>⭐ IMDb: {movie['rating']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='movie-genre'>{movie['genres']}</div>", unsafe_allow_html=True)
                    
                    # Fixed-position button inside a container
                    st.markdown("<div class='button-container'>"
                                f"<a class='trailer-button' href='{movie['trailer_url']}' target='_blank'>▶ Watch Trailer</a>"
                                "</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("<div class='footer'>Made by <b>Tavish Chawla</b> | 📧 <a href='mailto:tchawla827@gmail.com'>tchawla827@gmail.com</a></div>", unsafe_allow_html=True)
