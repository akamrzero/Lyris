from typing import Callable
from src.utils.get_cached_cover import get_small_pixbuf_cover
from src.utils.time_converter import ms_to_readable
from src.widgets.album_art import AlbumArt
from src.widgets.entitys.entity_item_row import EntityItemRow
from src.widgets.entitys.entity_item_view import EntityItemView
from src.utils.db_manager import DBM
from src.utils.event_bus import GEB
from src.widgets.playlist_detail_page import PlaylistDetailPage

import time


class PlaylistView(EntityItemView):
        def set_playlists(self, playists):
            self._set_items(playists)

        def _load_items(self, arg):
            start = time.time()
            for playlist_id in arg:
                new_song_view_item = PlaylistViewItem(playlist_id, lambda p=playlist_id: GEB.emit_viewstack_push_page(PlaylistDetailPage(p)))

                self._add_item(new_song_view_item)
            end = time.time()

            print(f'creating playlist items in {end-start} seconds')

class PlaylistViewItem(EntityItemRow):
    def __init__(self, playlist_id: str, callback: Callable):
        super().__init__()
        start = time.time()
        self.playlist_id = playlist_id
        self.playlist = DBM.playlist.get_for_id(playlist_id)
        self.callback = callback

        self.set_title()
        self.set_subtitle()
        self.set_start_widget()
        end = time.time()
        print(f'creating playlist item in {end-start} seconds')


    def set_title(self):
        self.title = DBM.playlist.get_name(self.playlist_id)

    def set_subtitle(self):
        songs = DBM.playlist.get_songs(self.playlist)
        time = 0
        for song in songs:
            time += song.length
        self.subtitle = f'{len(songs)} Songs • {ms_to_readable(time)}'

    def set_start_widget(self):
        covers = []
        i = 0
        songs = DBM.playlist.get_songs(self.playlist)
        while len(covers) < 4:
            cover = get_small_pixbuf_cover(songs[i].small_cover_file)
            if cover:
                covers.append(cover)

            i += 1

        start_widget = AlbumArt(56, covers=covers)

        self.start_widget = start_widget

