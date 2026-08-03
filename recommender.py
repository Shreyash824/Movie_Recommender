import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from data import MOVIES


class MovieRecommender:
    def __init__(self):
        self.df = pd.DataFrame(MOVIES)
        self.titles = self.df["title"].tolist()

        vectorizer = CountVectorizer()
        genre_matrix = vectorizer.fit_transform(self.df["genres"])
        self.similarity = cosine_similarity(genre_matrix, genre_matrix)

        self.index_map = {title: i for i, title in enumerate(self.titles)}

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
