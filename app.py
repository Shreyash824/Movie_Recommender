import streamlit as st

from recommender import MovieRecommender

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
)

@st.cache_resource
def load_recommender():
    return MovieRecommender()


rec = load_recommender()

st.title("🎬 Movie Recommendation System")
st.markdown("Find movies similar to your favorite ones using **cosine similarity** on genres.")

with st.sidebar:
    st.header("⚙️ Settings")
    top_n = st.slider("Number of recommendations", min_value=3, max_value=15, value=10, step=1)

    st.markdown("---")
    st.subheader("📊 Dataset Stats")
    st.write(f"- **Total movies:** {len(rec.titles)}")
    genres_set = set()
    for g in rec.df["genres"]:
        genres_set.update(g.split())
    st.write(f"- **Unique genres:** {len(genres_set)}")
    st.write(", ".join(sorted(genres_set)))
    st.markdown("---")
    st.caption("Built with Streamlit + scikit-learn")

tab_rec, tab_add = st.tabs(["🎬 Recommendations", "➕ Add Movie"])

with tab_rec:
    st.header("🔍 Pick a Movie")
    query = st.text_input("Type a movie name to search:", placeholder="e.g. Inception, The Dark Knight...")

    selected_movie = None
    if query:
        results = rec.search(query)
        if results:
            selected_movie = st.selectbox("Select from matches:", results)
        else:
            st.warning("No matching movie found. Try a different name.")

    st.markdown("### ➡️ or select directly from the catalog")
    catalog = st.selectbox("Browse all movies:", ["-- Choose a movie --"] + rec.titles)

    if selected_movie:
        movie = selected_movie
    elif catalog != "-- Choose a movie --":
        movie = catalog
    else:
        movie = None

    if movie:
        st.subheader(f"Movies similar to **{movie}**")

        genres = rec.genres_for(movie)
        if genres:
            st.markdown(f"*Genres of {movie}:* `{genres}`")

        recommendations, error = rec.get_similar(movie, top_n=top_n)

        if error:
            st.error(error)
        elif recommendations:
            cols = st.columns(3)
            for i, r in enumerate(recommendations):
                col = cols[i % 3]
                with col:
                    st.markdown(
                        f"""
                        <div style="border:1px solid #444; border-radius:10px; padding:12px; margin:8px 0; background:#1a1a1a;">
                            <h4 style="margin:0 0 4px 0;">{r['title']}</h4>
                            <p style="margin:0; color:#aaa; font-size:13px;">{r['genres']}</p>
                            <p style="margin:6px 0 0 0; color:#4caf50; font-weight:bold;">Similarity: {r['similarity']}%</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

with tab_add:
    st.header("➕ Add a New Movie")
    st.markdown(
        "Expand the dataset by adding a movie with its genres. "
        "It becomes available for recommendations immediately and is saved permanently."
    )

    with st.form("add_movie_form"):
        new_title = st.text_input("Movie Title", placeholder="e.g. Oppenheimer")
        available_genres = sorted(genres_set)
        selected_genres = st.multiselect(
            "Select genres (or type custom ones below)",
            available_genres,
            help="Pick from existing genres to keep the dataset consistent.",
        )
        custom_genres = st.text_input(
            "Extra genres (space-separated, optional)",
            placeholder="e.g. Noir Cyberpunk",
        )
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
    st.subheader("📚 Recently added movies")
    custom = rec.custom_movies()
    if custom:
        for m in custom:
            st.markdown(f"- **{m['title']}** — `{m['genres']}`")
    else:
        st.caption("No custom movies added yet.")
