import os

from gi.repository import Gdk, GLib, GdkPixbuf
from .db_manager import DBM

def get_small_pixbuf_cover(filename):
    try:
        folder = os.path.join(GLib.get_user_cache_dir(), 'covers', 'covers_small')
        filepath = os.path.join(folder, filename)
        return GdkPixbuf.Pixbuf.new_from_file(filepath)
    except Exception:
        return None


def get_medium_pixbuf_cover(filename):
    try:
        folder = os.path.join(GLib.get_user_cache_dir(), 'covers', 'covers_medium')
        filepath = os.path.join(folder, filename)
        return GdkPixbuf.Pixbuf.new_from_file(filepath)
    except Exception:
        return None


def get_large_pixbuf_cover(filename):
    try:
        folder = os.path.join(GLib.get_user_cache_dir(), 'covers', 'covers_large')
        filepath = os.path.join(folder, filename)
        return GdkPixbuf.Pixbuf.new_from_file(filepath)
    except Exception:
        return None

