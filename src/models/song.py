from peewee import (
    SqliteDatabase, Model, AutoField, CharField, IntegerField,
    ForeignKeyField, DateTimeField, TextField, BooleanField, UUIDField
)
from .base_model import BaseModel
from .artist import Artist
from .album import Album
import uuid

class Song(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=200)
    artist = ForeignKeyField(Artist, backref='songs', null=True)
    album = ForeignKeyField(Album, backref='songs', null=True)
    file_path = CharField(unique=True)
    length = IntegerField()
    small_cover_file = CharField(max_length=200, null=True)
    medium_cover_file = CharField(max_length=200, null=True)
    large_cover_file = CharField(max_length=200, null=True)
