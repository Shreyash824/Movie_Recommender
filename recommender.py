import json
import os

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from data import MOVIES

CUSTOM_FILE = os.path.join(os.path.dirname(__file__), "custom_movies.json")


class MovieRecommender:
    def __init__(self):
        movies = list(MOVIES)
        movies.extend(self._load_custom())
        self.df = pd.DataFrame(movies)
        self._rebuild()

    def _load_custom(self):
        if os.path.exists(CUSTOM_FILE):
            with open(CUSTOM_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        return []

    def _rebuild(self):
        self.titles = self.df["title"].tolist()
        vectorizer = CountVectorizer()
        genre_matrix = vectorizer.fit_transform(self.df["genres"])
        self.similarity = cosine_similarity(genre_matrix, genre_matrix)
        self.index_map = {title: i for i, title in enumerate(self.titles)}

    def add_movie(self, title, genres):
        title = title.strip()
        genres = " ".join(genres.strip().split())
        if not title:
            return False, "Movie title is required."
        if not genres:
            return False, "At least one genre is required."
        if any(t.lower() == title.lower() for t in self.titles):
            return False, f"'{title}' already exists in the dataset."

        new_row = {"title": title, "genres": genres}
        custom = self._load_custom()
        custom.append(new_row)
        with open(CUSTOM_FILE, "w", encoding="utf-8") as f:
            json.dump(custom, f, indent=4)

        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self._rebuild()
        return True, f"'{title}' added successfully!"

    def custom_movies(self):
        return self._load_custom()

    def get_similar(self, movie_title, top_n=10):
        movie_title = movie_title.strip().lower()
        matches = [t for t in self.titles if t.lower() == movie_title]

        if not matches:
            return None, "Movie not found in the database."

        idx = self.index_map[matches[0]]
        scores = list(enumerate(self.similarity[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        similar = []
        for movie_idx, score in scores:
            if movie_idx == idx:
                continue
            similar.append({
                "title": self.titles[movie_idx],
                "genres": self.df.iloc[movie_idx]["genres"],
                "similarity": round(float(score) * 100, 1),
            })
            if len(similar) >= top_n:
                break

        return similar, None

    def search(self, query):
        query = query.strip().lower()
        return [t for t in self.titles if query in t.lower()]

    def genres_for(self, movie_title):
        movie_title = movie_title.strip().lower()
        for row in self.df.itertuples():
            if row.title.lower() == movie_title:
                return row.genres
        return None


if __name__ == "__main__":
    rec = MovieRecommender()
    print(f"Total movies: {len(rec.titles)}")
    test = "Inception"
    results, err = rec.get_similar(test)
    if err:
        print(err)
    else:
        print(f"\nMovies similar to '{test}':")
        for r in results:
            print(f"  {r['similarity']:>5.1f}%  {r['title']}  [{r['genres']}]")
