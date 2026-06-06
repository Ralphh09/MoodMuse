import random
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
import json
import os
import pandas as pd

st.set_page_config(page_title="MoodMuse", page_icon="🎶", layout="centered")

# ── Mood Themes ───────────────────────────────────────────────────────────────
MOOD_THEMES = {
    "Happy": {
        "emoji"  : "😄",
        "color"  : "#FFD700",
        "bg"     : "#FFF9E6",
        "accent" : "#FF8C00",
        "genre"  : "afrobeat"          # upbeat, energetic
    },
    "Sad": {
        "emoji"  : "😢",
        "color"  : "#5B9BD5",
        "bg"     : "#EEF4FB",
        "accent" : "#2E6DA4",
        "genre"  : "soul"     # emotional, raw
    },
    "Calm": {
        "emoji"  : "😌",
        "color"  : "#7EC8A4",
        "bg"     : "#F0FAF4",
        "accent" : "#3A9E6F",
        "genre"  : "ambient"      # soft, peaceful
    },
    "Stressed": {
        "emoji"  : "😰",
        "color"  : "#C084FC",
        "bg"     : "#F8F0FF",
        "accent" : "#8B5CF6",
        "genre"  : "piano"        # soothing, relaxing
    },
    "Angry": {
        "emoji"  : "😤",
        "color"  : "#FF6B6B",
        "bg"     : "#FFF0F0",
        "accent" : "#CC0000",
        "genre"  : "classical"    # calming, structured
    },
}

DEFAULT_MOODS = list(MOOD_THEMES.keys())

QUIZ_QUESTIONS = [
    {
        "question": "How's your energy level right now?",
        "options": {
            "High and buzzing ⚡": {"Happy": 2, "Angry": 1},
            "Low and drained 🪫": {"Sad": 2, "Calm": 1},
            "Steady and relaxed 🌿": {"Calm": 2},
            "Tense and wound up 🔩": {"Stressed": 2, "Angry": 1}
        }
    },
    {
        "question": "What do you most feel like doing right now?",
        "options": {
            "Dancing or singing 🕺": {"Happy": 2},
            "Curling up alone 🛋️": {"Sad": 2, "Calm": 1},
            "Going for a quiet walk 🚶": {"Calm": 2},
            "Screaming into a pillow 😤": {"Angry": 2, "Stressed": 1}
        }
    },
    {
        "question": "Pick a colour that matches your vibe:",
        "options": {
            "Bright yellow ☀️": {"Happy": 2},
            "Deep blue 🌊": {"Sad": 2, "Calm": 1},
            "Soft green 🌿": {"Calm": 2},
            "Dark red 🔴": {"Angry": 2, "Stressed": 1}
        }
    },
    {
        "question": "How did today treat you?",
        "options": {
            "Really well! 🎉": {"Happy": 2},
            "Not great 😔": {"Sad": 2},
            "It was fine, nothing special 😶": {"Calm": 2},
            "It was rough and overwhelming 😵": {"Stressed": 2, "Angry": 1}
        }
    },
    {
        "question": "What kind of music do you feel like hearing?",
        "options": {
            "Upbeat and fun 🎉": {"Happy": 2},
            "Emotional and raw 💔": {"Sad": 2},
            "Soft and mellow 🎵": {"Calm": 2},
            "Something to take the edge off 🎹": {"Stressed": 2, "Angry": 1}
        }
    }
]

# ── File paths ────────────────────────────────────────────────────────────────
HISTORY_FILE   = "mood_history.json"
FAVOURITES_FILE = "favourites.json"
JOURNAL_FILE   = "mood_journal.json"
RATINGS_FILE   = "song_ratings.json"
CUSTOM_MOODS_FILE = "custom_moods.json"

# ── File helpers ──────────────────────────────────────────────────────────────
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_history():     return load_json(HISTORY_FILE, [])
def load_favourites():  return load_json(FAVOURITES_FILE, [])
def load_journal():     return load_json(JOURNAL_FILE, [])
def load_ratings():     return load_json(RATINGS_FILE, {})
def load_custom_moods(): return load_json(CUSTOM_MOODS_FILE, {})

def save_history(mood, songs):
    history = load_history()
    history.insert(0, {
        "mood" : mood,
        "songs": songs,
        "time" : datetime.now().strftime("%d %b %Y, %H:%M")
    })
    save_json(HISTORY_FILE, history[:50])

def save_favourite(track):
    favourites = load_favourites()
    # avoid duplicates
    if not any(f["name"] == track["name"] and f["artist"] == track["artist"] for f in favourites):
        favourites.insert(0, {
            "name"        : track["name"],
            "artist"      : track["artist"],
            "album"       : track["album"],
            "external_url": track["external_url"],
            "time"        : datetime.now().strftime("%d %b %Y, %H:%M")
        })
        save_json(FAVOURITES_FILE, favourites)
        return True
    return False

def save_journal(mood, note):
    journal = load_journal()
    journal.insert(0, {
        "mood": mood,
        "note": note,
        "time": datetime.now().strftime("%d %b %Y, %H:%M")
    })
    save_json(JOURNAL_FILE, journal[:100])

def save_rating(track_name, rating):
    ratings = load_ratings()
    ratings[track_name] = rating
    save_json(RATINGS_FILE, ratings)

def load_all_moods():
    custom = load_custom_moods()
    all_themes = {**MOOD_THEMES}
    for mood, data in custom.items():
        all_themes[mood] = {
            "emoji" : data.get("emoji", "🎵"),
            "color" : data.get("color", "#888888"),
            "bg"    : "#F5F5F5",
            "accent": "#555555",
            "genre" : data.get("genre", "pop")
        }
    return all_themes

# ── Theme ─────────────────────────────────────────────────────────────────────
def apply_mood_theme(mood):
    all_themes = load_all_moods()
    theme = all_themes.get(mood, MOOD_THEMES["Happy"])
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {theme['bg']}; }}
        .stButton>button {{
            background-color: {theme['color']};
            color: #1a1a1a; border: none;
            border-radius: 12px; font-weight: bold;
        }}
        .stButton>button:hover {{ background-color: {theme['accent']}; color: white; }}
        .mood-header {{
            background: linear-gradient(135deg, {theme['color']}, {theme['accent']});
            padding: 20px; border-radius: 16px;
            text-align: center; color: white; margin-bottom: 20px;
        }}
        .track-card {{
            background: white;
            border-left: 5px solid {theme['color']};
            border-radius: 10px; padding: 12px 16px;
            margin-bottom: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .history-card {{
            background: white; border-radius: 10px;
            padding: 10px 14px; margin-bottom: 8px;
            border: 1px solid #eee; font-size: 0.9em;
        }}
    </style>
    """, unsafe_allow_html=True)

# ── Spotify ───────────────────────────────────────────────────────────────────
@st.cache_resource
def get_spotify():
    try:
        client_id = st.secrets["SPOTIFY_CLIENT_ID"]
        client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]
    except:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError("Spotify credentials not found. Please add them to Streamlit Secrets.")
    
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ), requests_timeout=30, retries=300)

def search_track(sp, query):
    try:
        results = sp.search(q=query, type="track", limit = 10)
        #tracks  = results["tracks"]
        items   = results["tracks"]["items"]
        tracks =[]
        if items:
            track = items[0]
            return {
                "name"        : track["name"],
                "artist"      : ", ".join(a["name"] for a in track["artists"]),
                "album"       : track["album"]["name"],
                "image"       : track["album"]["images"][1]["url"] if len(track["album"]["images"]) > 1 else None,
                "preview_url" : track.get("preview_url", None),
                "external_url": track["external_urls"]["spotify"],
            }
    except Exception as e:
        st.warning(f"Search failed for '{query}': {e}")
    return None

def get_spotify_recommendations(sp, mood, num_songs=5):
    """Search for songs by mood keywords instead of recommendations API"""

    # Mood to search keywords mapping
    mood_keywords = {
        "Happy"   : ["afrobeat", "feel good pop", "upbeat dance pop","tekno", "k-pop"],
        "Sad"     : ["sad acoustic", "emotional ballad","r-n-b", "heartbreak acoustic"],
        "Calm"    : ["calm ambient relaxing","jazz", "peaceful piano", "soft ambient"],
        "Stressed": ["relaxing piano stress relief","jazz", "calming music", "peaceful instrumental"],
        "Angry"   : ["calming classical", "peaceful orchestra","hip-hop" ,"gospel", "soothing classical"],
    }

    keywords = mood_keywords.get(mood, ["pop music"])
    tracks   = []

    try:
        for keyword in keywords[:2]:  # search 2 keywords
            results = sp.search(
                q     = keyword,
                type  = "track",
                limit = 3           # get 3 per keyword
            )
            items = results["tracks"]["items"]

            for track in items:
                if len(tracks) >= num_songs:
                    break
                tracks.append({
                    "name"        : track["name"],
                    "artist"      : ", ".join(a["name"] for a in track["artists"]),
                    "album"       : track["album"]["name"],
                    "image"       : track["album"]["images"][1]["url"] if len(track["album"]["images"]) > 1 else None,
                    "preview_url" : track.get("preview_url", None),
                    "external_url": track["external_urls"]["spotify"],
                })

            if len(tracks) >= num_songs:
                break

        # Shuffle so it feels fresh every time
        random.shuffle(tracks)
        return tracks[:num_songs]

    except Exception as e:
        st.warning(f"Spotify search failed: {e}")
        return []
# ── Track display ─────────────────────────────────────────────────────────────
def display_tracks(found_tracks, show_actions=True):
    ratings    = load_ratings()
    favourites = load_favourites()
    fav_names  = [f["name"] for f in favourites]

    for i, track in enumerate(found_tracks, 1):
        if track:
            st.markdown("<div class='track-card'>", unsafe_allow_html=True)
            cols = st.columns([1, 4, 2])

            with cols[0]:
                if track["image"]:
                    st.image(track["image"], width=60)

            with cols[1]:
                st.markdown(f"**{i}. {track['name']}**  \n{track['artist']} · *{track['album']}*")

                # Star rating
                rating = ratings.get(track["name"], 0)
                stars  = st.feedback("stars", key=f"rating_{i}_{track['name'][:10]}")
                if stars is not None and stars != rating:
                    save_rating(track["name"], stars + 1)
                    st.success("Rating saved!")

            with cols[2]:
                st.link_button("▶ Open", track["external_url"])

                if show_actions:
                    is_fav = track["name"] in fav_names
                    fav_label = "❤️ Saved" if is_fav else "🤍 Save"
                    if st.button(fav_label, key=f"fav_{i}_{track['name'][:10]}"):
                        if save_favourite(track):
                            st.success("Added to favourites!")
                        else:
                            st.info("Already in favourites!")

            if track["preview_url"]:
                st.audio(track["preview_url"], format="audio/mp3")

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.write(f"{i}. *(Not found on Spotify)*")

# ── Session State ─────────────────────────────────────────────────────────────
for key, default in [
    ("current_mood", "Happy"),
    ("playlist",     []),
    ("quiz_done",    False),
    ("page",         "home")
]:
    if key not in st.session_state:
        st.session_state[key] = default

apply_mood_theme(st.session_state.current_mood)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:10px 0 5px 0;'>
    <h1 style='font-size:2.5em; margin-bottom:0;'>🎶 Moodify</h1>
    <p style='color:gray; margin-top:4px;'>Your mood. Your playlist.</p>
</div>
""", unsafe_allow_html=True)

# ── Spotify init ──────────────────────────────────────────────────────────────
try:
    sp = get_spotify()
    sp.search(q="test", type="track", limit=1)
    st.success("Spotify connected ✅")
    spotify_connected = True
except Exception as e:
    st.warning(f"⚠️ Spotify not connected: {e}")
    spotify_connected = False

st.divider()

# ── Navigation ────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
with c1:
    if st.button("🏠", use_container_width=True):
        st.session_state.page = "home"
with c2:
    if st.button("🧠", use_container_width=True):
        st.session_state.page = "quiz"
        st.session_state.quiz_done = False
with c3:
    if st.button("📋", use_container_width=True):
        st.session_state.page = "history"
with c4:
    if st.button("❤️", use_container_width=True):
        st.session_state.page = "favourites"
with c5:
    if st.button("📝", use_container_width=True):
        st.session_state.page = "journal"
with c6:
    if st.button("🔍", use_container_width=True):
        st.session_state.page = "search"
with c7:
    if st.button("🎨", use_container_width=True):
        st.session_state.page = "custom"

st.divider()


# HOME

if st.session_state.page == "home":
    all_themes = load_all_moods()
    all_moods  = list(all_themes.keys())

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_mood = st.selectbox(
            "How are you feeling?",
            all_moods,
            index      = all_moods.index(st.session_state.current_mood) if st.session_state.current_mood in all_moods else 0,
            format_func= lambda m: f"{all_themes[m]['emoji']} {m}"
        )
        st.session_state.current_mood = selected_mood
        apply_mood_theme(selected_mood)

    with col2:
        num_songs = st.slider("Songs", 3, 10, 5)

    # Mood journal note
    with st.expander("📝 How are you feeling? Write a note"):
        journal_note = st.text_area("Write your thoughts...")
        if st.button("💾 Save Note"):
            if journal_note.strip():
                save_journal(selected_mood, journal_note)
                st.success("✅ Note saved!")

    b1, b2 = st.columns(2)
    with b1:
        generate = st.button("🎵 Generate Playlist", use_container_width=True, type="primary")
    with b2:
        shuffle = st.button("🔀 Shuffle Again", use_container_width=True)

    if generate or shuffle:
        st.session_state.current_mood = selected_mood
        if spotify_connected:
            with st.spinner("Spotify is picking songs for you..."):
                tracks = get_spotify_recommendations(sp, selected_mood, num_songs)
            if tracks:
                st.session_state.playlist = tracks
            else:
                st.warning("⚠️ Spotify couldn't find recommendations — try again!")
        else:
            st.error("❌ Spotify not connected!")

    if st.session_state.playlist:
        theme = all_themes.get(st.session_state.current_mood, MOOD_THEMES["Happy"])
        st.markdown(
            f"<div class='mood-header'><h2>{theme['emoji']} Your {st.session_state.current_mood} Playlist</h2></div>",
            unsafe_allow_html=True
        )
        display_tracks(st.session_state.playlist)
        names = [f"{t['name']} – {t['artist']}" for t in st.session_state.playlist]
        save_history(st.session_state.current_mood, names)

# QUIZ

elif st.session_state.page == "quiz":
    st.subheader("🧠 Mood Quiz")
    st.caption("Answer 5 questions and we'll detect your mood automatically!")

    if not st.session_state.quiz_done:
        with st.form("quiz_form"):
            answers = {}
            for i, q in enumerate(QUIZ_QUESTIONS):
                st.markdown(f"**{i+1}. {q['question']}**")
                answers[i] = st.radio("", list(q["options"].keys()), key=f"q{i}", label_visibility="collapsed")
            submitted = st.form_submit_button("🔍 Find My Mood", use_container_width=True)

        if submitted:
            scores = {m: 0 for m in DEFAULT_MOODS}
            for i, q in enumerate(QUIZ_QUESTIONS):
                for mood, delta in q["options"][answers[i]].items():
                    scores[mood] += delta
            st.session_state.current_mood = max(scores, key=scores.get)
            st.session_state.quiz_done    = True
            st.rerun()
    else:
        mood  = st.session_state.current_mood
        theme = MOOD_THEMES.get(mood, MOOD_THEMES["Happy"])
        apply_mood_theme(mood)
        st.markdown(
            f"<div class='mood-header'><h2>Your mood is: {theme['emoji']} {mood}</h2><p>Here's a playlist crafted just for you!</p></div>",
            unsafe_allow_html=True
        )

        if spotify_connected:
            with st.spinner("Building your playlist..."):
                tracks = get_spotify_recommendations(sp, mood, 5)
            if tracks:
                display_tracks(tracks)
                names = [f"{t['name']} – {t['artist']}" for t in tracks]
                save_history(mood, names)
            else:
                st.warning("⚠️ Spotify couldn't find recommendations!")
        else:
            st.error("❌ Spotify not connected!")

        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.quiz_done = False
            st.rerun()

# HISTORY

elif st.session_state.page == "history":
    st.subheader("📋 Your Mood History")
    history = load_history()

    if not history:
        st.info("No history yet — generate a playlist to get started!")
    else:
        from collections import Counter
        counts = Counter(h["mood"] for h in history)
        df     = pd.DataFrame(counts.items(), columns=["Mood", "Times"]).sort_values("Times", ascending=False)
        st.bar_chart(df.set_index("Mood"))
        st.divider()

        for entry in history:
            all_themes = load_all_moods()
            theme      = all_themes.get(entry["mood"], {"emoji": "🎵"})
            st.markdown(f"""
            <div class='history-card'>
                <strong>{theme['emoji']} {entry['mood']}</strong> &nbsp;
                <span style='color:gray; font-size:0.85em;'>{entry['time']}</span><br>
                <small>{' • '.join(entry['songs'][:3])}{'...' if len(entry['songs']) > 3 else ''}</small>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🗑️ Clear History", use_container_width=True):
            save_json(HISTORY_FILE, [])
            st.rerun()


# FAVOURITES

elif st.session_state.page == "favourites":
    st.subheader("❤️ Your Favourite Songs")
    favourites = load_favourites()

    if not favourites:
        st.info("No favourites yet — save songs from your playlist!")
    else:
        st.write(f"**{len(favourites)} saved songs**")
        for i, fav in enumerate(favourites, 1):
            st.markdown(f"""
            <div class='track-card'>
                <strong>{i}. {fav['name']}</strong><br>
                {fav['artist']}<br>
                <small style='color:gray;'>{fav['time']}</small>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("▶ Open on Spotify", fav["external_url"], key=f"fav_open_{i}")

        if st.button("🗑️ Clear Favourites", use_container_width=True):
            save_json(FAVOURITES_FILE, [])
            st.rerun()

# ════════════════════════════
# JOURNAL
# ════════════════════════════
elif st.session_state.page == "journal":
    st.subheader("📝 Mood Journal")
    journal = load_journal()

    # Add new entry
    with st.form("journal_form"):
        all_themes  = load_all_moods()
        all_moods   = list(all_themes.keys())
        mood_select = st.selectbox("Mood", all_moods, format_func=lambda m: f"{all_themes[m]['emoji']} {m}")
        note        = st.text_area("How are you feeling?", height=150)
        submitted   = st.form_submit_button("💾 Save Entry")

        if submitted:
            if note.strip():
                save_journal(mood_select, note)
                st.success("✅ Journal entry saved!")
            else:
                st.error("❌ Please write something!")

    st.divider()

    # Display journal entries
    if not journal:
        st.info("No journal entries yet!")
    else:
        for entry in journal:
            all_themes = load_all_moods()
            theme      = all_themes.get(entry["mood"], {"emoji": "🎵", "color": "#888"})
            st.markdown(f"""
            <div class='history-card' style='border-left: 4px solid {theme["color"]};'>
                <strong>{theme['emoji']} {entry['mood']}</strong> &nbsp;
                <span style='color:gray; font-size:0.85em;'>{entry['time']}</span><br>
                <p style='margin-top:8px;'>{entry['note']}</p>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🗑️ Clear Journal", use_container_width=True):
            save_json(JOURNAL_FILE, [])
            st.rerun()

# SEARCH

elif st.session_state.page == "search":
    st.subheader("🔍 Search for a Song")

    query = st.text_input("Search song or artist", placeholder="e.g. Blinding Lights The Weeknd")

    if st.button("🔍 Search", use_container_width=True):
        if query.strip():
            if spotify_connected:
                with st.spinner("Searching Spotify..."):
                    tracks = search_track(sp, query)
                if tracks:
                    display_tracks(tracks)
                else:
                    st.warning("⚠️ Song not found — try a different search!")
            else:
                st.error("❌ Spotify not connected!")
        else:
            st.error("❌ Please enter a search term!")

# CUSTOM MOOD

elif st.session_state.page == "custom":
    st.subheader("🎨 Custom Moods")

    custom_moods = load_custom_moods()

    # Add new mood
    with st.form("custom_mood_form"):
        st.markdown("### Add New Mood")
        mood_name  = st.text_input("Mood Name (e.g. Excited)")
        mood_emoji = st.text_input("Emoji (e.g. 🤩)")
        mood_color = st.color_picker("Color", "#888888")
        mood_genre = st.selectbox("Spotify Genre", [
            "pop", "rock", "hip-hop", "jazz", "classical",
            "electronic", "r-n-b", "country", "latin", "indie",
            "ambient", "chill", "sad", "happy", "party","grime","k-pop",
            "afrobeats", "gospel", "reggae","blues", "funk",  "metal",
            "punk", "folk","disco"
        ])
        submitted = st.form_submit_button("➕ Add Mood")

        if submitted:
            if mood_name.strip():
                custom_moods[mood_name] = {
                    "emoji": mood_emoji or "🎵",
                    "color": mood_color,
                    "genre": mood_genre
                }
                save_json(CUSTOM_MOODS_FILE, custom_moods)
                st.success(f"✅ {mood_name} mood added!")
                st.rerun()
            else:
                st.error("❌ Please enter a mood name!")

    st.divider()

    # Display custom moods
    if not custom_moods:
        st.info("No custom moods yet — add one above!")
    else:
        st.markdown("### Your Custom Moods")
        for mood, data in custom_moods.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div class='history-card' style='border-left: 4px solid {data["color"]};'>
                    <strong>{data['emoji']} {mood}</strong> — Genre: {data['genre']}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"del_{mood}"):
                    del custom_moods[mood]
                    save_json(CUSTOM_MOODS_FILE, custom_moods)
                    st.rerun()
