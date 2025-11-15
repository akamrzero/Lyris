import gi

from gi.repository import Gio


def load_music_files(folder):
    folder = Gio.File.new_for_path(folder)

    enumerator = folder.enumerate_children(
        'standard::*',
        Gio.FileQueryInfoFlags.NONE,
        None
    )

    files = []
    info = enumerator.next_file(None)
    while info:
        name = info.get_name()
        if is_music_file(info.get_content_type()):
            path = folder.get_child(name).get_path()
            files.append(path)
        info = enumerator.next_file(None)

    return files

def load_playlist_files(folder):
    folder = Gio.File.new_for_path(folder)

    enumerator = folder.enumerate_children(
        'standard::*',
        Gio.FileQueryInfoFlags.NONE,
        None
    )

    files = []
    info = enumerator.next_file(None)
    while info:
        name = info.get_name()
        if is_playlist_file(info.get_content_type()):
            path = folder.get_child(name).get_path()
            files.append(path)
        info = enumerator.next_file(None)

    return files

def is_music_file(content_type):
    return content_type.startswith('audio/') and not content_type.endswith('pls') and not content_type.endswith('url')

def is_playlist_file(content_type):
    return content_type in (
        'audio/x-mpegurl',
        'application/x-mpegurl',
        'application/vnd.apple.mpegurl',
        'audio/mpegurl'
    )

