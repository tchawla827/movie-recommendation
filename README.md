# 🎬 Movie Recommender System Using Machine Learning!

<img src="demo/6.webp" alt="workflow" width="70%">

## 📌 About This Project
This is a **Streamlit web application** that recommends movies based on user interests using **Machine Learning and Cosine Similarity**. It provides an **interactive, user-friendly interface** with features like **movie search, IMDb ratings, genres, trailers, and clickable movie posters** for a **seamless recommendation experience**.

---

## 🚀 Key Features

### **🔍 1. Movie Search with Autocomplete**
- **Smart search bar** with **instant suggestions** as you type.
- **Prevents errors** by showing only available movies.
- **Fast, efficient, and user-friendly.**

### **🎥 2. Personalized Movie Recommendations**
- Uses **content-based filtering** to suggest **top 5 similar movies**.
- Generates recommendations based on **movie metadata (genres, cast, director, keywords)**.
- Powered by **cosine similarity** for accurate results.

### **⭐ 3. IMDb Ratings & Movie Details**
- Displays **IMDb rating** for each recommended movie.
- Shows **genres** (e.g., Action, Comedy, Drama) for better context.

### **🖼️ 4. Clickable Movie Posters**
- Each **movie poster is clickable** and redirects to its **IMDb page**.
- **High-resolution posters** for a clean UI.

### **▶ 5. Watch Trailer Button**
- **Dynamically fetches YouTube trailers** for each movie.
- **Perfectly aligned** across all recommendations.
- **Hover effects & animated buttons** for a modern look.

### **🎨 6. Responsive & Modern UI**
- **Dark mode theme** with a **sleek and polished interface**.
- **Hover effects** on movie cards for a smooth experience.
- **Optimized for both desktop & mobile viewing.**

---

## 📊 Dataset Used
We used the **TMDB 5000 Movie Dataset**, available on Kaggle:  
🔗 [Dataset Link](https://www.kaggle.com/tmdb/tmdb-movie-metadata?select=tmdb_5000_movies.csv)

---

## ⚙ **How the Recommendation Works?**
### **💡 Cosine Similarity (Concept Used)**
1. Measures the **similarity between two movie vectors**.
2. Computes the **angle between them** instead of distance.
3. Values range from **0 (completely different) to 1 (identical)**.
4. More details: [Cosine Similarity Explanation](https://www.learndatasci.com/glossary/cosine-similarity/)

---

## 🛠 How to Run?

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/tchawla827/movie-recommendation.git
cd movie-recommendation
```

### **2️⃣ Create a Virtual Environment**
```bash
conda create -n movie python=3.7.10 -y
conda activate movie
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Train the Model**
Run the following script to generate the model:
```bash
python Movie_Recommender_System_Data_Analysis.ipynb
```

### **5️⃣ Start the Streamlit App**
```bash
streamlit run app.py
```

---

## 📌 Author
📌 **Tavish Chawla**  
📌 **Email:** tchawla827@gmail.com  

---

🎬 **Your Movie Recommender System is now ready to use!** 🚀🔥 Let me know if you need any modifications.
