import os
from enum import Enum

from gi.repository import GLib, GdkPixbuf

class CoverSize(Enum):
    small = 56
    medium = 146
    large = 250

def get_cached_cover(base_filename, size: CoverSize):
    try:
        folder = os.path.join(GLib.get_user_cache_dir(), 'covers', str(size.value))
        filepath = os.path.join(folder, f'{base_filename}.jpg')
        return GdkPixbuf.Pixbuf.new_from_file(filepath)
    except Exception as e:
        print(e)
        return None