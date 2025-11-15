from peewee import (
    SqliteDatabase, Model, AutoField, CharField, IntegerField,
    ForeignKeyField, DateTimeField, TextField, BooleanField, UUIDField
)
from .base_model import BaseModel
import uuid

class Artist(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=200, unique=True)