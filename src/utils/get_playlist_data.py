import gi
import os
from gi.repository import Gio

def get_playlist_content(path: str) -> list[str]:
    song_paths = []
    parent_folder = os.path.dirname(path)
    file = Gio.File.new_for_path(path)
    success, contents, etag_out = file.load_contents(None)
    if success:
        text = contents.decode('utf-8')
    else:
        raise IOError

    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        song_paths.append(os.path.join(parent_folder, line))
        # try:
        #     songs.append(Song.from_file(os.path.join(parent_folder, line)))
        # except IOError:
        #     raise print(f'Could not load song from {path}, skipping...')

    return song_paths

def get_playlist_name(path: str) -> str:
    file = Gio.File.new_for_path(path)
    success, contents, etag_out = file.load_contents(None)
    if success:
        text = contents.decode('utf-8')
    else:
        raise IOError

    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('#PLAYLIST'):
            line = line.replace('#PLAYLIST:', '', 1)
            name = line
            return name
    return 'Unknown Playlist'