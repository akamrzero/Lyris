from peewee import SqliteDatabase
from ..models import Artist
from ..models import Album
from ..models import Playlist
from ..models import PlaylistSong
from ..models import Song
from ..models import db

class DBManager:
    class _Artist:
        def add(self, name):
            return Artist.get_or_create(name=name)

        def get(self, album_id):
            return Artist.get_or_none(Artist.id == album_id)

        def get_by_name(self, name):
            return Artist.get_or_none(Artist.name == name)

        def get_ids(self):
            ids = []
            for artist in Artist.select().order_by(Artist.name):
                ids.append(artist.id)
            return ids

        def serach(self, query):
            return Artist.select().where(Artist.name.contains(query))

    class _Album:
        def add(self, name, artist):
            """Adds an album to the DB"""
            album, created = Album.get_or_create(
                name=name,
                artist=artist,
            )

            return album, created

        def get(self, album_id):
            return Album.get_or_none(Album.id == album_id)

        def get_ids(self):
            ids = []
            for album in Album.select().order_by(Album.name):
                ids.append(album.id)
            return ids

        def get_for_artist(self, artist):
            return Album.select().where(Album.artist == artist)

        def get_artist_for__id(self, album_id):
            """Gets an artist from an album id from the DB"""
            return Album.get_or_none(Album.id == album_id).artist

        def search(self, query):
            return Album.select().where(Album.name.contains(query))

    class _Songs:
        def add(self, song_id, name, artist, album, file_path, length, cover_base_filename):
            """Adds a song to the DB"""
            song, created = Song.get_or_create(
                file_path=file_path,
                defaults={
                    'id': song_id,
                    'name': name,
                    'artist': artist,
                    'album': album,
                    'length': length,
                    'cover_base_filename': cover_base_filename
                }
            )

            if not created:
                # Update fields if they changed (optional: check before saving)
                changed = False
                if song.name != name:
                    song.name = name
                    changed = True
                if song.artist != artist:
                    song.artist = artist
                    changed = True
                if song.album != album:
                    song.album = album
                    changed = True
                if song.length != length:
                    song.length = length
                    changed = True
                if song.cover_base_filename != cover_base_filename:
                    song.cover_base_filename = cover_base_filename
                    changed = True

                if changed:
                    song.save()
            return song, created

        def get_for_album(self, album):
            return Song.select().where(Song.album == album)

        def get_for_artist(self, artist):
            return Song.select().where(Song.artist == artist)

        def get_for_id(self, song_id):
            return Song.get_or_none(Song.id == song_id)

        def get_for_file_path(self, file_path):
            return Song.get_or_none(Song.file_path == file_path)

        def remove(self, song):
            Song.delete().where(Song == song).execute()

        def remove_by_filepath(self, filepath):
            Song.delete().where(Song.file_path == filepath).execute()

        def get_all(self):
            return Song.select().order_by(Song.id)

        def search(self, query):
            return Song.select().where(Song.name.contains(query))

    class _Playlist:
        def add(self, name, file_path):
            return Playlist.get_or_create(name=name, file_path=file_path)

        def get(self) -> list[str]:
            ids = []
            for playlist in Playlist.select().order_by(Playlist.name):
                ids.append(playlist.id)
            return ids

        def get_name(self, playlist_id) -> str:
            return Playlist.get_or_none(Playlist.id == playlist_id).name

        def get_for_id(self, playlist_id):
            return Playlist.get_or_none(Playlist.id == playlist_id)

        def search(self, query):
            return Playlist.select().where(Playlist.name.contains(query))

        def add_song(self, playlist, song, position):
            return PlaylistSong.get_or_create(playlist=playlist, song=song, position=position)

        def remove_song(self, playlist, song):
            PlaylistSong.delete().where(PlaylistSong.playlist == playlist and PlaylistSong.song == song).execute()

        def get_songs(self, playlist):
            query = (Song
                     .select()
                     .join(PlaylistSong)
                     .where(PlaylistSong.playlist == playlist)
                     .order_by(PlaylistSong.position))
            return list(query)


        def get_songs_for_id(self, playlist_id):
            return [ps.song for ps in PlaylistSong.select().where(PlaylistSong.playlist == playlist_id)]




    def __init__(self, database: SqliteDatabase):
        self.db = database
        if database.is_closed():
            database.connect()

    @property
    def artist(self):
        return self._Artist()

    @property
    def album(self):
        return self._Album()

    @property
    def song(self):
        return self._Songs()

    @property
    def playlist(self):
        return self._Playlist()




DBM = DBManager(database=db)

