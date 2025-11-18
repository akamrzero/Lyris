import peewee

from .db_manager import DBM
from .mediastore import media_store
import time
import uuid


class MediaIndexer:
    def index(self):
        start_time = time.time()
        media_store.index()

        audio_files = media_store.audio_files
        # print(audio_files)
        for filename, data  in audio_files.items():
            try:
                artist, album = None, None
                if data['artist']:
                    artist, _ = DBM.artist.add(data['artist'])
                    if data['album']:
                        album, _ = DBM.album.add(data['album'], artist)

                DBM.song.add(
                    song_id = uuid.uuid3(uuid.NAMESPACE_DNS, filename),
                    name = data['title'],
                    artist = artist,
                    album = album,
                    file_path = filename,
                    length = data['length'],
                    cover_base_filename = data['cover_base_filename'],
                )


            except peewee.IntegrityError as e:
                print(e)

        playlist_files = media_store.playlist_files
        print(playlist_files)
        for filename, data in playlist_files.items():
            playlist, _ = DBM.playlist.add(
                name=data['name'],
                file_path=filename,
            )
            for i, song_filepath in enumerate(data['songs']):
                song = DBM.song.get_for_file_path(song_filepath)
                if song:
                    DBM.playlist.add_song(
                        playlist,
                        song,
                        i
                    )

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'Indexing done in {elapsed_time} seconds.')

media_indexer = MediaIndexer()