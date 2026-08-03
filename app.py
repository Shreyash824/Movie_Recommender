import random

import streamlit as st

from recommender import MovieRecommender

st.set_page_config(page_title="Movie Recommendation System", page_icon="🎬", layout="wide")

CSS = """
<style>
:root {
  --accent: #00a8cc;
  --accent2: #d81b60;
  --gold: #ffb300;
  --bg: #10132b;
  --card: #171b38;
}

[data-testid="stAppViewContainer"] {
  font-family: 'Segoe UI', sans-serif;
  background: linear-gradient(160deg, #0d1025, #10132b, #1b1f3d);
}

[data-testid="stHeader"] { background: transparent; }

h1, h2, h3, h4 {
  color: #e8eaf6 !important;
  font-weight: 700;
}

[data-testid="stSidebar"] {
  background: rgba(20, 23, 50, 0.9);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}
[data-testid="stSidebar"] * { color: #e8eaf6 !important; }

.stButton > button {
  border: 1px solid var(--accent);
  border-radius: 10px;
  color: var(--accent);
  background: rgba(0, 168, 204, 0.08);
  font-weight: 600;
}
.stButton > button:hover {
  background: var(--accent);
  color: #0d1025 !important;
}

.stTextInput input, .stSelectbox > div > div {
  border-radius: 10px !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  background: rgba(255, 255, 255, 0.07) !important;
  color: #fff !important;
}

.movie-card {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 14px 16px;
  margin: 8px 0;
  background: var(--card);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
}
.movie-card-hot {
  border-color: var(--gold);
}
.mc-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 6px;
}
.mc-genres { margin-bottom: 8px; }
.chip {
  display: inline-block;
  margin: 2px 4px 2px 0;
  padding: 2px 10px;
  font-size: 12px;
  border-radius: 14px;
  background: rgba(0, 168, 204, 0.15);
  border: 1px solid rgba(0, 168, 204, 0.45);
  color: #9be8ff;
}
.sim-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #b8bcd6;
}
.sim-row strong { color: var(--gold); }
.sim-bar {
  flex: 1;
  height: 7px;
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.12);
  overflow: hidden;
}
.sim-fill {
  height: 100%;
  border-radius: 7px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
}

.stTabs [data-baseweb="tab"] {
  border-radius: 10px;
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.05);
  font-weight: 600;
}
.stTabs [aria-selected="true"] {
  background: var(--accent) !important;
  color: #0d1025 !important;
}

.hero {
  font-size: 40px;
  font-weight: 800;
  text-align: center;
  padding: 14px 0 4px;
  color: #e8eaf6;
}
.hero-sub {
  text-align: center;
  color: #9aa0c9;
  margin-bottom: 18px;
  font-size: 16px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource
def load_recommender():
    return MovieRecommender()


rec = load_recommender()

GENRES = sorted(set(g for genres in rec.df["genres"] for g in genres.split()))

st.markdown('<div class="hero">🎬 Movie Lens</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Genre-based recommendations powered by <b>cosine similarity</b></div>',
    unsafe_allow_html=True,
)


def movie_card_html(title, genres, sim=None, hot=False):
    chips = "".join(f'<span class="chip">{g}</span>' for g in genres.split())
    sim_html = ""
    if sim is not None:
        bar = max(0, min(100, sim))
        sim_html = (
            f'<div class="sim-row">'
            f'<span>Similarity</span>'
            f'<div class="sim-bar"><div class="sim-fill" style="width:{bar}%"></div></div>'
            f"<strong>{sim:.1f}%</strong></div>"
        )
    return (
        f'<div class="movie-card{" movie-card-hot" if hot else ""}">'
        f'<div class="mc-title">🎬 {title}</div>'
        f'<div class="mc-genres">{chips}</div>'
        f"{sim_html}</div>"
    )


with st.sidebar:
    st.markdown("## ⚙️ Settings")
    top_n = st.slider("Number of recommendations", 3, 15, 10)

    st.markdown("---")
    st.markdown("### 🎯 Genre Filter")
    genre_filter = st.multiselect("Filter recommendations by genre", GENRES)
    st.markdown("---")
    st.markdown("### 📊 Dataset")
    st.metric("Total movies", len(rec.titles))
    st.metric("Unique genres", len(GENRES))
    custom_count = len(rec.custom_movies())
    st.metric("Added by you", custom_count)
    st.markdown("---")
    st.caption("Built with Streamlit + scikit-learn")

tab_rec, tab_add = st.tabs(["🎬 Recommendations", "➕ Add Movie"])

with tab_rec:
    c1, c2 = st.columns([2, 1])
    with c1:
        query = st.text_input("🔎 Type a movie name to search:",
                              placeholder="e.g. Inception, The Dark Knight...")
    with c2:
        surprise = st.button("🎲 Surprise Me")
        if surprise:
            st.session_state["random_pick"] = random.choice(rec.titles)

    selected_movie = None
    if query:
        results = rec.search(query)
        if results:
            selected_movie = st.selectbox("Select from matches:", results)
        else:
            st.warning("No matching movie found. Try a different name.")

    random_pick = st.session_state.get("random_pick")
    st.markdown("#### 📚 or browse the catalog")
    catalog = st.selectbox("All movies:", ["-- Choose a movie --"] + rec.titles,
                           label_visibility="collapsed")

    movie = None
    if selected_movie:
        movie = selected_movie
    elif catalog != "-- Choose a movie --":
        movie = catalog
    elif random_pick:
        movie = random_pick
        st.info(f"🎲 Random pick: **{movie}**")

    if movie:
        recommendations, error = rec.get_similar(movie, top_n=top_n)
        rec_titles = [r["title"] for r in recommendations] if not error else []

        st.markdown("---")
        if error:
            st.error(error)
        else:
            genres = rec.genres_for(movie)
            st.markdown(f"#### 🎯 Movies similar to **{movie}**")
            if genres:
                st.markdown("".join(f'<span class="chip">{g}</span>' for g in genres.split()),
                            unsafe_allow_html=True)

            if genre_filter:
                rec_titles = [t for t in rec_titles if any(
                    g in rec.genres_for(t) for g in genre_filter)]

            if rec_titles:
                st.markdown(f"### 🍿 Recommendations ({len(rec_titles)})")
                cols = st.columns(3)
                for i, r in enumerate(recommendations):
                    if r["title"] not in rec_titles:
                        continue
                    with cols[i % 3]:
                        st.markdown(movie_card_html(r["title"], r["genres"], r["similarity"]),
                                    unsafe_allow_html=True)
            else:
                st.warning("No recommendations match the current genre filter.")
    else:
        st.info("Select a movie above to see recommendations.")

with tab_add:
    st.markdown("## ➕ Add a New Movie")
    st.markdown("Expand the dataset — it becomes available for recommendations instantly "
                "and is saved permanently to `custom_movies.json`.")

    with st.form("add_movie_form"):
        new_title = st.text_input("Movie Title", placeholder="e.g. Oppenheimer")
        selected_genres = st.multiselect("Select genres", GENRES)
        custom_genres = st.text_input("Extra genres (space-separated, optional)",
                                      placeholder="e.g. Noir Cyberpunk")
        submitted = st.form_submit_button("Add Movie")

    if submitted:
        genres_input = " ".join(selected_genres)
        if custom_genres.strip():
            genres_input = (genres_input + " " + custom_genres.strip()).strip()
        ok, msg = rec.add_movie(new_title, genres_input)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

    st.markdown("---")
    st.markdown("### 🗂️ Recently added")
    custom = rec.custom_movies()
    if custom:
        for m in reversed(custom[-10:]):
            st.markdown(movie_card_html(m["title"], m["genres"]), unsafe_allow_html=True)
    else:
        st.caption("No custom movies added yet.")
