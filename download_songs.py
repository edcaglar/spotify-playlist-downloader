import parser
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from yt_dlp import YoutubeDL

def get_all_tracks(sp):

    results = sp.current_user_playlists()
    playlists = dict()
    while results:
        for i, playlist in enumerate(results['items']):
            playlists[playlist['name']] = playlist['uri']
        if results['next']:
            results = sp.next(results)
        else:
            results = None
    all_tracks = {}
    # for offset in range(0, 500, 100):
    for key, value in playlists.items():
        all_tracks[key] = []
        total_tracks = sp.playlist_tracks(value)['total']
        for offset in range(0, total_tracks, 100):
            all_tracks[key].extend(sp.playlist_tracks(value, limit=100, offset=offset)["items"])
    tracks_dict = {}
    for playlist_name, tracks in all_tracks.items():

        tracks_dict[playlist_name] = []
        for track in tracks:
            if type(track['track']) != type(None):
                song_name = track['track']['name']
                artists = ""

                for artist in track['track']['artists']:
                    artists += artist['name'] + " "
                tracks_dict[playlist_name].append(song_name + " " + artists)

    with open("tracks.json", "w") as file:
        json.dump(tracks_dict, file)

    return tracks_dict


def spotify_connection():
    SPOTIPY_CLIENT_ID = ""
    SPOTIPY_CLIENT_SECRET = ""
    SPOTIPY_REDIRECT_URI = "https://localhost:8888/callback/"

    scope = "user-library-read"
    connection_credentials = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                          client_secret=SPOTIPY_CLIENT_SECRET,
                                          redirect_uri=SPOTIPY_REDIRECT_URI,
                                          scope=scope)
    return spotipy.Spotify(auth_manager=connection_credentials)


def download_from_youtube(tracks_dict):

    for playlist_name in tracks_dict.keys():
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': f'{playlist_name}/%(title)s.%(ext)s'}
        with YoutubeDL(ydl_opts) as ydl:
            if not os.path.exists(playlist_name):
                os.mkdir(playlist_name)
            for track in tracks_dict[playlist_name]:
                url = ydl.extract_info(f"ytsearch:{track}", download=True)['entries'][0]['webpage_url']

if __name__ == "__main__":
    fetch_from_spotify = True
    if fetch_from_spotify == True:
        sp = spotify_connection()
        tracks_dict = get_all_tracks(sp)
    else:
        with open("tracks.json", "r") as file:
            tracks_dict = json.load(file)

    download_from_youtube(tracks_dict)
