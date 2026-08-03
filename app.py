import random

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from recommender import MovieRecommender

st.set_page_config(page_title="Movie Recommendation System", page_icon="🎬", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

:root {
  --neon: #00f5ff;
  --neon2: #ff6ec7;
  --gold: #ffd166;
  --bg1: #0f0c29;
  --bg2: #1b1b3a;
  --bg3: #24243e;
}

[data-testid="stAppViewContainer"] {
  font-family: 'Outfit', 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, var(--bg1), var(--bg2), var(--bg3));
  background-size: 400% 400%;
  animation: gradShift 16s ease infinite;
}
@keyframes gradShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

[data-testid="stHeader"] { background: transparent; }

h1, h2, h3, h4 {
  background: linear-gradient(90deg, var(--neon), var(--neon2), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
  letter-spacing: 0.5px;
}

[data-testid="stSidebar"] {
  background: rgba(20, 18, 48, 0.65);
  backdrop-filter: blur(14px);
  border-right: 1px solid rgba(0, 245, 255, 0.15);
}
[data-testid="stSidebar"] * { color: #e6e6fa !important; }

.stButton > button, .stDownloadButton > button {
  border: 1px solid var(--neon);
  border-radius: 30px;
  color: var(--neon);
  background: rgba(0, 245, 255, 0.06);
  transition: all 0.25s ease;
  font-weight: 600;
}
.stButton > button:hover {
  background: linear-gradient(90deg, var(--neon), var(--neon2));
  color: #0f0c29 !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 245, 255, 0.35);
}

.stTextInput input, .stSelectbox > div > div, [data-baseweb="select"] > div {
  border-radius: 14px !important;
  border: 1px solid rgba(0, 245, 255, 0.35) !important;
  background: rgba(255, 255, 255, 0.06) !important;
  color: #fff !important;
}

.movie-card {
  border: 1px solid rgba(0, 245, 255, 0.25);
  border-radius: 16px;
  padding: 16px 18px;
  margin: 10px 0;
  background: linear-gradient(145deg, rgba(26, 26, 58, 0.92), rgba(15, 12, 41, 0.92));
  backdrop-filter: blur(8px);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  animation: fadeUp 0.5s ease both;
}
.movie-card:hover {
  transform: translateY(-6px) scale(1.02);
  border-color: var(--neon2);
  box-shadow: 0 14px 34px rgba(255, 110, 199, 0.28), 0 0 24px rgba(0, 245, 255, 0.18);
}
.movie-card-hot {
  border-color: var(--gold);
  box-shadow: 0 0 28px rgba(255, 209, 102, 0.35);
}
.mc-title {
  font-size: 17px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 6px;
}
.mc-genres { margin-bottom: 8px; }
.chip {
  display: inline-block;
  margin: 2px 4px 2px 0;
  padding: 3px 10px;
  font-size: 12px;
  border-radius: 20px;
  background: rgba(0, 245, 255, 0.12);
  border: 1px solid rgba(0, 245, 255, 0.4);
  color: #aef6ff;
}
.sim-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #cdd6ff;
}
.sim-row strong { color: var(--gold); }
.sim-bar {
  flex: 1;
  height: 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  overflow: hidden;
}
.sim-fill {
  height: 100%;
  border-radius: 8px;
  background: linear-gradient(90deg, var(--neon), var(--neon2), var(--gold));
  animation: growBar 0.8s ease both;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes growBar {
  from { width: 0; }
}

.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
  border-radius: 20px;
  padding: 8px 22px;
  background: rgba(255,255,255,0.05);
  font-weight: 600;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(90deg, var(--neon), var(--neon2)) !important;
  color: #0f0c29 !important;
}

.hero {
  font-size: 42px;
  font-weight: 800;
  text-align: center;
  padding: 14px 0 4px;
}
.hero-sub {
  text-align: center;
  color: #b9c0ff;
  margin-bottom: 18px;
  font-size: 16px;
}
.glow-text {
  background: linear-gradient(90deg, var(--neon), var(--neon2), var(--gold), var(--neon));
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: glowSlide 6s linear infinite;
}
@keyframes glowSlide {
  0% { background-position: 0% 50%; }
  100% { background-position: 300% 50%; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource
def load_recommender():
    return MovieRecommender()


rec = load_recommender()

GENRES = sorted(set(g for genres in rec.df["genres"] for g in genres.split()))
GENRE_COLORS = {g: c for g, c in zip(sorted(set(rec.primary_genre)),
                                     px.colors.qualitative.Light24)}

st.markdown('<div class="hero glow-text">🎬 MOVIE LENS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Genre-based recommendations powered by <b>cosine similarity</b> &nbsp;·&nbsp; explore the 3D genre map</div>',
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


def build_3d(title=None, rec_titles=None):
    highlight_set = set(rec_titles or [])
    others_opacity = 0.18 if (title or highlight_set) else 0.85
    figs = []

    for genre in GENRE_COLORS:
        indices = [
            i for i, pg in enumerate(rec.primary_genre)
            if pg == genre and rec.titles[i] not in highlight_set and rec.titles[i] != title
        ]
        if not indices:
            continue
        figs.append(go.Scatter3d(
            x=[rec.x[i] for i in indices],
            y=[rec.y[i] for i in indices],
            z=[rec.z[i] for i in indices],
            mode="markers",
            name=genre,
            text=[f"{rec.titles[i]}<br>{rec.df.iloc[i]['genres']}" for i in indices],
            hovertemplate="<b>%{text}</b><extra></extra>",
            marker=dict(
                size=3,
                color=GENRE_COLORS[genre],
                opacity=others_opacity,
                line=dict(width=0.4, color="rgba(255,255,255,0.4)"),
            ),
            showlegend=True,
        ))

    if title and rec_titles:
        rec_indices = [rec.index_map[t] for t in rec_titles if t in rec.index_map]
        figs.append(go.Scatter3d(
            x=[rec.x[i] for i in rec_indices],
            y=[rec.y[i] for i in rec_indices],
            z=[rec.z[i] for i in rec_indices],
            mode="markers",
            name="Recommended",
            text=[f"{rec.titles[i]}<br>{rec.df.iloc[i]['genres']}" for i in rec_indices],
            hovertemplate="<b>%{text}</b><extra></extra>",
            marker=dict(size=8, color="#ffd166", opacity=1,
                        line=dict(width=1, color="#fff")),
            showlegend=True,
        ))

    if title:
        idx = rec.index_map.get(title)
        if idx is not None:
            figs.append(go.Scatter3d(
                x=[rec.x[idx]],
                y=[rec.y[idx]],
                z=[rec.z[idx]],
                mode="markers",
                name="Selected",
                text=[f"{title}<br>{rec.df.iloc[idx]['genres']}"],
                hovertemplate="<b>%{text}</b><extra></extra>",
                marker=dict(size=12, color="#ff2e63", opacity=1,
                            line=dict(width=2, color="#fff"),
                            symbol="diamond"),
                showlegend=True,
            ))

    fig = go.Figure(data=figs)
    fig.update_layout(
        height=680,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cdd6ff", family="Outfit"),
        legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0.2)"),
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showbackground=False, showgrid=False, zeroline=False,
                       showticklabels=False, title=""),
            yaxis=dict(showbackground=False, showgrid=False, zeroline=False,
                       showticklabels=False, title=""),
            zaxis=dict(showbackground=False, showgrid=False, zeroline=False,
                       showticklabels=False, title=""),
        ),
    )
    return fig


with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    top_n = st.slider("Number of recommendations", 3, 15, 10)

    st.markdown("---")
    st.markdown("### 🎯 Genre Filter")
    genre_filter = st.multiselect("Highlight genres in the 3D map", GENRES,
                                  help="Optional: narrow the catalog and spotlight genres.")
    st.markdown("---")
    st.markdown("### 📊 Dataset")
    st.metric("Total movies", len(rec.titles))
    st.metric("Unique genres", len(GENRES))
    custom_count = len(rec.custom_movies())
    st.metric("Added by you", custom_count)
    st.markdown("---")
    st.caption("Built with Streamlit · scikit-learn · Plotly")

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

            st.markdown("### 🌌 3D Genre Map")
            st.caption("Each point is a movie projected into genre space (PCA). "
                       "Hover to inspect · click & drag to rotate · scroll to zoom.")
            fig = build_3d(title=movie, rec_titles=rec_titles)
            st.plotly_chart(fig, use_container_width=True, key="map")

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
        st.markdown("### 🌌 3D Genre Map — all movies")
        st.caption("Pick a movie above to spotlight it and its recommendations in 3D.")
        st.plotly_chart(build_3d(), use_container_width=True, key="map_all")

with tab_add:
    st.markdown("## ➕ Add a New Movie")
    st.markdown("Expand the dataset — it becomes available for recommendations instantly "
                "and is saved permanently to `custom_movies.json`.")

    with st.form("add_movie_form"):
        new_title = st.text_input("Movie Title", placeholder="e.g. Oppenheimer")
        selected_genres = st.multiselect("Select genres", GENRES)
        custom_genres = st.text_input("Extra genres (space-separated, optional)",
                                      placeholder="e.g. Noir Cyberpunk")
        submitted = st.form_submit_button("✨ Add Movie")

    if submitted:
        genres_input = " ".join(selected_genres)
        if custom_genres.strip():
            genres_input = (genres_input + " " + custom_genres.strip()).strip()
        ok, msg = rec.add_movie(new_title, genres_input)
        if ok:
            st.success(msg)
            st.balloons()
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
