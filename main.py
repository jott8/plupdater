import spotipy, time, sys
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2        import SpotifyOAuth
from datetime              import datetime

class User:
    username: str
    copy_playlist_id: str

    def __init__(self, username, copy_playlist_id) -> None:
        self.username         = username
        self.copy_playlist_id = copy_playlist_id


class Track:
    tid: str
    title: str
    artist: str

    def __init__(self, track_id: str, title: str, artist: str) -> None:
        self.tid    = track_id
        self.title  = title
        self.artist = artist

    def __eq__(self, other):
        if not isinstance(other, Track):
            return NotImplementedError
        
        return self.tid == other.tid


class Playlist:
    pid: str
    tracks: list[Track]
    length: int
    is_liked_songs: bool

    def __init__(self, tracks: list[Track], playlist_id: str = None) -> None:
        if playlist_id: self.pid = playlist_id; self.is_liked_songs = False
        else: self.playlist_id = None; self.is_liked_songs = True

        self.tracks = tracks
        self.length = len(tracks)


def get_playlist(id=None) -> Playlist:
    if id: results = sp.playlist_tracks(id)
    else: results  = sp.current_user_saved_tracks() 

    tracks_raw = results['items']

    while results['next']:
        results = sp.next(results)
        tracks_raw.extend(results['items'])

    tracks = [Track(raw_track['track']['id'], raw_track['track']['name'], raw_track['track']['artists'][0]['name']) for raw_track in tracks_raw]

    return Playlist(tracks, playlist_id=id)


def get_playlist_diff(playlist1: Playlist, playlist2: Playlist):
    new_tracks     = [Track(track.tid, track.title, track.artist) for track in playlist1.tracks if track not in playlist2.tracks]
    deleted_tracks = [Track(track.tid, track.title, track.artist) for track in playlist2.tracks if track not in playlist1.tracks]

    return new_tracks, deleted_tracks


def remove_tracks(user: User, tracks: list[str]) -> None:
    track_ids = [track.tid for track in tracks]
    while track_ids:
        if(len(track_ids) > 100): 
            temp = track_ids[:100]

            sp.user_playlist_remove_all_occurrences_of_tracks(user.username, user.copy_playlist_id, temp)

            track_ids = track_ids[100:]
        else: 
            sp.user_playlist_remove_all_occurrences_of_tracks(user.username, user.copy_playlist_id, track_ids)
            track_ids = []
    return
        

def fill_playlist(user: User, tracks: list[str]) -> None:
    track_ids = [track.tid for track in tracks]
    while track_ids:
        if(len(track_ids) > 100): 
            temp = track_ids[:100]

            sp.user_playlist_add_tracks(user.username, user.copy_playlist_id, temp, position=0)

            track_ids = track_ids[100:]
        else: 
            sp.user_playlist_add_tracks(user.username, user.copy_playlist_id, track_ids, position=0)
            track_ids = []
    return


def update_description(id: str, amount_tracks_new: int, amount_tracks_deleted: int, execution_time: float, date: str) -> None:
    sp.playlist_change_details(id, description=f'Automatically updated on {date}. Changes: {amount_tracks_new} new, {amount_tracks_deleted} deleted track(s).') 

    return


def write_log(filename: str, new_tracks: list[Track], deleted_tracks: list[Track], date: str) -> None:
    with open(filename, 'a') as file:
        new_str = ''
        del_str = ''

        for track in new_tracks:
            new_str += f'{track.title.replace(",", "")} - {track.artist}'

        for track in deleted_tracks:
            del_str += f'{track.title.replace(",", "")} - {track.artist}'

        file.write(f'{date},{new_str},{del_str},{len(new_str)},{len(del_str)},\n')


def get_spotify_user():
    scope = 'user-library-read,playlist-modify-public,playlist-modify-public'
    user = User(sys.argv[2], sys.argv[3])
    cache_handler = CacheFileHandler(username=user.username)
    sp_oath = SpotifyOAuth(client_id=sys.argv[4],
                                               client_secret=sys.argv[5],
                                               redirect_uri=sys.argv[6],
                                               scope=scope,
                                               cache_handler=cache_handler) 

    spotify = spotipy.Spotify(auth_manager=sp_oath)
    return spotify, user


if __name__ == '__main__':
    DEBUG = sys.argv[1] == 'TRUE'

    sp, user = get_spotify_user()

    if DEBUG: log_file_name = f'logs/{user.username}_debug.csv'
    else: log_file_name = f'logs/{user.username}.csv'

    date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    start_time = time.time()

    ls_playlist                = get_playlist()
    copy_playlist              = get_playlist(user.copy_playlist_id)
    new_tracks, deleted_tracks = get_playlist_diff(ls_playlist, copy_playlist)

    print(f'New: {new_tracks}\n\nDeleted: {deleted_tracks}\n')

    total_time = time.time() - start_time

    if not DEBUG and (new_tracks or deleted_tracks): 
        if new_tracks: fill_playlist(user, new_tracks)
        if deleted_tracks: remove_tracks(user, deleted_tracks)

        update_description(user.copy_playlist_id, len(new_tracks), len(deleted_tracks), total_time, date)

    print(f'Execution time: {total_time}')
    write_log(log_file_name, new_tracks, deleted_tracks, date)
