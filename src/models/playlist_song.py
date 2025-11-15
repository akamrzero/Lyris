from peewee import (
    SqliteDatabase, Model, AutoField, CharField, IntegerField,
    ForeignKeyField, DateTimeField, TextField, BooleanField, UUIDField
)
from .base_model import BaseModel
from .playlist import Playlist
from .song import Song

class PlaylistSong(BaseModel):
    playlist = ForeignKeyField(Playlist, backref='playlist_songs')
    song = ForeignKeyField(Song, backref='song_playlists')
    position = IntegerField()

    class Meta:
        indexes = (
            (('playlist', 'song'), True),
        )