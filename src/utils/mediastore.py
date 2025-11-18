import os
import mimetypes
import uuid

from mutagen import File, FileType
import time
import json
from gi.repository import GLib
from PIL import Image
import io
from pathlib import Path

from mutagen.flac import FLAC
from mutagen.id3 import APIC
from mutagen.mp4 import MP4


def save_last_index_time():
    path = os.path.join(GLib.get_user_cache_dir(), 'last_index.json')
    with open(path, 'w') as f:
        json.dump({"last_indexed": int(time.time())}, f)


def get_last_indexed_time():
    path = os.path.join(GLib.get_user_cache_dir(), 'last_index.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            json_data = json.load(f)
        return json_data['last_indexed']
    return None

def is_m3u8(path: str) -> bool:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            return first_line == '#EXTM3U'
    except Exception:
        return False

def is_audio(path: str) -> bool:
    return mimetypes.guess_type(path)[0].startswith('audio/')

def extract_cover(file_path):
    audio = File(file_path)
    if audio is None:
        return None

    # MP3
    if hasattr(audio, 'tags') and 'APIC:' in audio.tags:
        return audio.tags['APIC:'].data
    elif hasattr(audio, 'tags'):  # mehrere APIC Frames prüfen
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                return tag.data

    # FLAC
    if isinstance(audio, FLAC) and audio.pictures:
        return audio.pictures[0].data

    # M4A/MP4
    if isinstance(audio, MP4) and 'covr' in audio.tags and audio.tags['covr']:
        return audio.tags['covr'][0]

    return None



def save_cover_variants(cover_bytes, cache_path, base_name, sizes=(56, 146, 250)):
    if not cover_bytes or not cache_path:
        return
    print('caching cover')
    try:
        image = Image.open(io.BytesIO(cover_bytes))
    except Exception as e:
        print("Failed to load cover image with Pillow:", e)
        return

    for size in sizes:
        dest_folder = os.path.join(cache_path, str(size))
        os.makedirs(dest_folder, exist_ok=True)
        output_path = os.path.join(dest_folder, f'{base_name}.jpg')

        w, h = image.size
        scale = size / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)

        img_resized = image.resize((new_w, new_h), Image.LANCZOS)

        if image.mode == 'RGBA':
            image.convert('RGB').save(output_path, format='JPEG', quality=90)
        else:
            img_resized.save(output_path, format='JPEG', quality=90)

def get_title(audio: FileType):
    return audio.get('title')


class MediaStore:
    def __init__(self):
        self._folders = []
        self._audio_files = {}
        self._playlist_files = {}

    @property
    def audio_files(self):
        return self._audio_files
    @property
    def playlist_files(self):
        return self._playlist_files

    @property
    def folders(self):
        return self._folders

    def add_folder(self, folder):
        if os.path.isdir(folder):
            self._folders.append(folder)

    def index(self):
        print('indexing media files')
        last_indexed_time = get_last_indexed_time()
        for folder in self.folders:
            files = []

            for root, dirs, sub_files in os.walk(folder):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in sub_files:
                    if not file.startswith('.'):
                        files.append(os.path.join(root, file))

            for file in files:
                if os.path.getmtime(file) <= last_indexed_time:
                    continue
                audio = File(file, easy=True)
                if audio:
                    tags = audio.tags
                    info = audio.info

                    artist_name = audio.get('artist', [None])[0]
                    album_name = audio.get('album', [None])[0]

                    prov_artist_name, prov_album_name = artist_name, album_name

                    if not artist_name:
                        prov_artist_name = str(uuid.uuid4())
                    if not album_name:
                        prov_album_name = str(uuid.uuid4())

                    album_art_name = str(uuid.uuid3(uuid.NAMESPACE_DNS, f'{prov_artist_name}_{prov_album_name}'))
                    cover_data = extract_cover(file)
                    save_cover_variants(cover_data, os.path.join(GLib.get_user_cache_dir(), 'covers'), album_art_name)

                    print(Path(file).stem)
                    self._audio_files[file] = {
                        'title': audio.get('title', [Path(file).stem])[0],
                        'artist': artist_name,
                        'album': album_name,
                        'length': int(info.length) if info else None,
                        'cover_base_filename': album_art_name
                    }


                else:
                    if not is_m3u8(file):
                        continue
                    try:
                        playlist_folder = os.path.dirname(file)
                        playlist_name = ''
                        songs = []
                        with open(file, 'r') as f:
                            for line in f:
                                if line.startswith('#PLAYLIST:'):
                                    playlist_name = line.removeprefix("#PLAYLIST:").strip()
                                elif line.startswith('#'):
                                    continue
                                else:
                                    song_path = os.path.join(playlist_folder, line.strip())
                                    song_path = os.path.abspath(song_path)
                                    if os.path.exists(song_path) and song_path in files:
                                        songs.append(song_path)

                            if playlist_name and songs:
                                self._playlist_files[file] = {
                                    'name': playlist_name,
                                    'songs': songs,
                                }
                    except Exception:
                        pass
        save_last_index_time()


media_store = MediaStore()

