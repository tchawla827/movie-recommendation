import os

movies_path = r"C:\Users\tavis\Desktop\Movie-Recommender-System-Using-Machine-Learning\data\tmdb_5000_movies.csv"
credits_path = r"C:\Users\tavis\Desktop\Movie-Recommender-System-Using-Machine-Learning\data\tmdb_5000_credits.csv"

print("Movies File Exists:", os.path.exists(movies_path))
print("Credits File Exists:", os.path.exists(credits_path))
