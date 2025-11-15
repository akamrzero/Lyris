from gi.repository import Gio, GLib
from peewee import (
    SqliteDatabase, Model, AutoField, CharField, IntegerField,
    ForeignKeyField, DateTimeField, TextField, BooleanField, UUIDField
)
from pathlib import Path
from datetime import datetime


DB_PATH = Path(GLib.get_user_data_dir()) / 'library.db'

db = SqliteDatabase(DB_PATH)

def init_db(*models):
    if db.is_closed():
        db.connect()
    db.create_tables(list(models))


