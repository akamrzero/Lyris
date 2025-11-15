from typing import Tuple

from .music_loader import load_playlist_files, load_music_files
from .audio_metadata import get_album_name, get_song_title, get_song_length, get_cover_image, get_artist_name
from .get_playlist_data import get_playlist_name, get_playlist_content
# from time_converter import ms_to_seconds, seconds_to_readable
from .db_manager import DBManager, DBM
from .get_dominant_color import get_dominant_color_from_pixbuf
import time
import os
import uuid
import json
from datetime import datetime

from gi.repository import GLib, GdkPixbuf, Gio

def cache_covers(cover: GdkPixbuf.Pixbuf, song_id: str):
    start_time = time.time()
    covers_folder = os.path.join(GLib.get_user_cache_dir(), 'covers')
    covers_small_folder = os.path.join(covers_folder, 'covers_small')
    covers_medium_folder = os.path.join(covers_folder, 'covers_medium')
    covers_large_folder = os.path.join(covers_folder, 'covers_large')
    if not os.path.exists(covers_folder):
        os.makedirs(covers_folder)
    if not os.path.exists(covers_small_folder):
        os.makedirs(covers_small_folder)
    if not os.path.exists(covers_medium_folder):
        os.makedirs(covers_medium_folder)
    if not os.path.exists(covers_large_folder):
        os.makedirs(covers_large_folder)

    small_pixbuf = cover.scale_simple(
         56,
         56,
         GdkPixbuf.InterpType.BILINEAR,
    )
    small_cover_filename = f'{song_id}_cover_small.png'
    small_pixbuf.savev(os.path.join(covers_small_folder, small_cover_filename), 'png', [], [])

    medium_pixbuf = cover.scale_simple(
        146,
        146,
        GdkPixbuf.InterpType.BILINEAR,
    )
    medium_cover_filename = f'{song_id}_cover_medium.png'
    medium_pixbuf.savev(os.path.join(covers_medium_folder, medium_cover_filename), 'png', [], [])

    large_pixbuf = cover.scale_simple(
         250,
         250,
         GdkPixbuf.InterpType.BILINEAR,
    )
    large_cover_filename = f'{song_id}_cover_large.png'
    large_pixbuf.savev(os.path.join(covers_large_folder, large_cover_filename), 'png', [], [])

    return small_cover_filename, medium_cover_filename, large_cover_filename

def save_last_index_time():
    path = os.path.join(GLib.get_user_cache_dir(), 'last_index.json')
    with open(path, 'w') as f:
        json.dump({"last_indexed": int(time.time())}, f)


def get_last_indexed_time():
    path = os.path.join(GLib.get_user_cache_dir(), 'last_index.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            json_data = json.load(f)
        return json_data['last_indexed']
    return None

def get_file_last_edited(file):
    file = Gio.File.new_for_path(file)
    info = file.query_info('time::modified', Gio.FileQueryInfoFlags.NONE, None)
    modified_time = info.get_attribute_uint64('time::modified')
    return modified_time


def index_folder(dbm: DBManager, folder):
    start_time = time.time()
    song_files = load_music_files(folder)
    playlist_files = load_playlist_files(folder)

    last_indexed_time = get_last_indexed_time()

    for song in dbm.song.get_all():
        if not os.path.exists(song.file_path):
            dbm.song.remove(song)

    if song_files:
        for file in song_files:
            existing_song = dbm.song.get_for_file_path(file)
            if existing_song:
                file_modified = get_file_last_edited(file)
                if last_indexed_time is not None and file_modified <= last_indexed_time:
                    continue
                else:
                    print('removing Song by filepath')
                    dbm.song.remove(existing_song)
                    song_id = uuid.uuid4()
            else:
                song_id = uuid.uuid4()

            song_title = get_song_title(file)
            artist_name = get_artist_name(file)
            album_name = get_album_name(file)
            filepath = file
            song_length = get_song_length(file)

            artist = None
            album = None

            cover = get_cover_image(file)

            if cover:
                small_cover_filename, medium_cover_filename, large_cover_filename = cache_covers(cover, str(song_id))
                color = get_dominant_color_from_pixbuf(cover)
                color_str = ','.join(map(str, color))
            else:
                color_str, small_cover_filename, medium_cover_filename, large_cover_filename = None, None, None, None

            if artist_name:
                artist, _ = dbm.artist.add(artist_name)
                if album_name:
                    album, _ = dbm.album.add(album_name, artist, color_str)


            song, _ = dbm.song.add(
                song_id=song_id,
                name = song_title,
                artist=artist,
                album=album,
                file_path=filepath,
                length=song_length,
                small_cover_file=small_cover_filename,
                medium_cover_file=medium_cover_filename,
                large_cover_file=large_cover_filename,
            )

        for file in playlist_files:
            try:
                playlist_name = get_playlist_name(file)
                filepath = file

                playlist, _ = dbm.playlist.add(playlist_name, filepath)

                for i, song_filepath in enumerate(get_playlist_content(filepath)):
                    song = dbm.song.get_for_file_path(song_filepath)
                    if song:
                        dbm.playlist.add_song(
                            playlist,
                            song,
                            i
                        )
                for song in dbm.playlist.get_songs(playlist):
                    if not os.path.exists(song.file_path):
                        dbm.song.remove(song)
                        dbm.playlist.remove_song(playlist, song)
                        print('Song removed')
            except Exception as e:
                print(e)

    save_last_index_time()




    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Indexing done in {elapsed_time} seconds.')
