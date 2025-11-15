from peewee import (
    SqliteDatabase, Model, AutoField, CharField, IntegerField,
    ForeignKeyField, DateTimeField, TextField, BooleanField, UUIDField
)
import uuid
from .base_model import BaseModel
from .artist import Artist

class Album(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=200)
    artist = ForeignKeyField(Artist, backref='albums')
    dominant_cover_color =CharField(max_length=20, null=True)

    class Meta:
        indexes = (
            (('name', 'artist'), True),
        )