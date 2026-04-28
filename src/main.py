import requests
import streamlit as st
from youtube_search import YoutubeSearch
import os
import json

st.markdown(
    """
    <style>
    .stApp, .stAppViewContainer, header[data-testid="stHeader"] {
        background-color: #000000 !important;
    }

    [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
        background-color: #000000 !important;
    }

    h1, h2, h3, p, span, div, label, .stMarkdown {
        color: #ffffff !important;
    }

    .stTextInput>div>div>input {
        color: #ffffff !important;
        background-color: #1e1e1e !important;
    }

    [data-testid="stDecoration"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

file_name = 'playlist_data.json'

def load_data():
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                return json.load(file)
        except: return []
    return []

def save_data(playlist):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(playlist, file, indent=4, ensure_ascii=False)

if 'playlist' not in st.session_state:
    st.session_state.playlist = load_data()

if 'search_results' not in st.session_state:
    st.session_state.search_results = None

def get_yt_link(artist, music):
    try:
        query = f'{artist} {music} official audio'
        results = YoutubeSearch(query, max_results=1).to_dict()
        if results:
            return 'https://www.youtube.com/watch?v=' + results[0]['id']
    except: return None
    return None

def search_lyric(artist, music):
    try:
        endpoint = f'https://api.lyrics.ovh/v1/{artist}/{music}'
        response = requests.get(endpoint)
        return response.json().get('lyrics', '') if response.status_code == 200 else ''
    except: return ''

# --- INTERFACE ---
st.image('https://i.pinimg.com/736x/e2/06/1e/e2061e114a9cf95c89e05d9f14c9a7f2.jpg')
st.title('Music Lyrics')

artist_input = st.text_input('Type the artist name: ', key='artist')
music_input = st.text_input('Type the music name: ', key='music')
search = st.button('Search')

with st.sidebar:
    st.header("🗂️ Saved Musics")
    if not st.session_state.playlist:
        st.info("Playlist is empty.")
    else:
        for idx, item in enumerate(st.session_state.playlist):
            col_t, col_b = st.columns([4, 1])

            if col_t.button(f"▶️ {item['music']}\n({item['artist']})", key=f"repro_{idx}"):
                saved_lyric = search_lyric(item['artist'], item['music'])
                st.session_state.search_results = {
                    "artist": item['artist'],
                    "music": item['music'],
                    "lyric": saved_lyric,
                    "url": item['url']
                }
                st.rerun()

            if col_b.button("🗑️", key=f"del_{idx}"):
                st.session_state.playlist.pop(idx)
                save_data(st.session_state.playlist)
                st.rerun()
            st.divider()

if search:
    if artist_input and music_input:
        lyric = search_lyric(artist_input, music_input)
        yt_link = get_yt_link(artist_input, music_input)

        if lyric:
            st.session_state.search_results = {
                "artist": artist_input,
                "music": music_input,
                "lyric": lyric,
                "url": yt_link
            }
        else:
            st.error('Error, music not found.')
            st.session_state.search_results = None

# --- EXIBIÇÃO ---
if st.session_state.search_results:
    st.divider()

    saved = any(i['music'] == st.session_state.search_results['music'] and
                i['artist'] == st.session_state.search_results['artist']
                for i in st.session_state.playlist)

    if not saved:
        if st.button("💾 Save on Playlist"):
            new_music = {
                "artist": st.session_state.search_results['artist'],
                "music": st.session_state.search_results['music'],
                "url": st.session_state.search_results['url']
            }
            st.session_state.playlist.append(new_music)
            save_data(st.session_state.playlist)
            st.toast("Saved!")
            st.rerun()
    else:
        st.write("✅ It's already in the playlist")

    if st.session_state.search_results['url']:
        st.video(st.session_state.search_results['url'])

    st.markdown("### Lyrics")
    # Usando st.text para manter a formatação original da letra
    st.text(st.session_state.search_results['lyric'])