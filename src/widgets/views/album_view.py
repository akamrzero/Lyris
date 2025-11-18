import gi


gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from typing import Callable

from src.queue import Queue
from src.utils.db_manager import DBM
from src.utils.get_cached_cover import get_cached_cover, CoverSize
from src.widgets.album_art import AlbumArt
from src.widgets.entitys.entity_item_row import EntityItemRow
from src.utils.event_bus import GEB
from src.widgets.album_detail_page import AlbumDetailPage
from src.widgets.entitys.entity_item_view import EntityItemView


class AlbumView(EntityItemView):
    def set_albums(self, albums):
        self._set_items(albums)

    def _load_items(self, arg):
        for album_id in arg:
            new_song_view_item = AlbumViewItem(
                album_id,
                lambda a=album_id: GEB.emit_viewstack_push_page(AlbumDetailPage(a))
            )

            self._add_item(new_song_view_item)

class AlbumViewItem(EntityItemRow):
    def __init__(self, album_id, callback: Callable):
        super().__init__()
        self.album_id = album_id
        self.album = DBM.album.get(self.album_id)
        self.callback = callback

        self.set_title()
        self.set_subtitle()
        self.set_start_widget()

    def set_title(self):
        self.title = self.album.name

    def set_subtitle(self):
        songs = DBM.song.get_for_album(self.album)
        self.subtitle = f'{len(songs)} Song{"s" if len(songs) > 1 else ""}'

    def set_start_widget(self):
        def get_filepath():
            song = DBM.song.get_for_album(self.album)[0]
            return song.cover_base_filename

        start_widget = AlbumArt(56, 'person-symbolic', [get_cached_cover(get_filepath(), CoverSize.small)])
        start_widget.add_css_class('lyris-all-rounded-corners')
        start_widget.set_overflow(Gtk.Overflow.HIDDEN)
        self.start_widget = start_widget


