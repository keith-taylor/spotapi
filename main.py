import spotipy
from spotipy.oauth2 import SpotifyOAuth
import argparse
import os

# Set up Spotify credentials
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

scope = "user-read-playback-state,user-modify-playback-state"


def authenticate_spotify():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=scope,
        )
    )
    return sp


def search_spotify(sp, query):
    results = sp.search(q=query, limit=3, type="album,artist,track")
    items = []

    if results["albums"]["items"]:
        items.append(("Album", results["albums"]["items"]))
    if results["artists"]["items"]:
        items.append(("Artist", results["artists"]["items"]))
    if results["tracks"]["items"]:
        items.append(("Track", results["tracks"]["items"]))

    return items


def play_item(sp, item_type, item_id):
    if item_type == "Album":
        sp.start_playback(context_uri=f"spotify:album:{item_id}")
    elif item_type == "Artist":
        sp.start_playback(context_uri=f"spotify:artist:{item_id}")
    elif item_type == "Track":
        sp.start_playback(uris=[f"spotify:track:{item_id}"])


def main():
    parser = argparse.ArgumentParser(description="Control Spotify from the CLI.")
    parser.add_argument(
        "-s", "--search", type=str, help="Search for the specified text."
    )
    args = parser.parse_args()

    if args.search:
        sp = authenticate_spotify()
        items = search_spotify(sp, args.search)

        if not items:
            print("No results found.")
            return

        print("Select an item to play (0 to cancel):")
        index = 1
        for item_type, item_list in items:
            for item in item_list:
                print(f"{index}. {item_type}: {item['name']}")
                index += 1

        choice = int(input("Enter your choice: "))
        if choice == 0:
            print("Cancelled.")
            return

        selected_item = None
        index = 1
        for item_type, item_list in items:
            for item in item_list:
                if index == choice:
                    selected_item = (item_type, item["id"])
                    break
                index += 1
            if selected_item:
                break

        if selected_item:
            play_item(sp, selected_item[0], selected_item[1])
            print(f"Playing {selected_item[0]}: {selected_item[1]}")
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
