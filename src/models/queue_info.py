from peewee import (
    SqliteDatabase, Model, AutoField, CharField, IntegerField,
    ForeignKeyField, DateTimeField, TextField, BooleanField, UUIDField
)
from .base_model import BaseModel
from .song import Song

class QueueSongs(BaseModel):
    index = IntegerField(primary_key=True)
    play_index = IntegerField(unique=True)
    song = ForeignKeyField(Song)

class QueueInfo(BaseModel):
    current_index = IntegerField(default=0)