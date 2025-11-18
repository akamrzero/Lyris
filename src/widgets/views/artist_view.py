import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from typing import Callable

from src.utils.db_manager import DBM
from src.utils.event_bus import GEB
from src.widgets.album_art import AlbumArt
from src.widgets.entitys.entity_item_row import EntityItemRow
from src.widgets.entitys.entity_item_view import EntityItemView
from src.widgets.view_stack import ViewStackPage
from src.widgets.artist_detail_page import ArtistDetailPage




class ArtistView(EntityItemView):
    def set_artists(self, artists):
        self._set_items(artists)

    def _load_items(self, arg):
        for album_id in arg:
            new_song_view_item = ArtistViewItem(
                album_id,
                lambda a=album_id: GEB.emit_viewstack_push_page(ViewStackPage(ArtistDetailPage(a)))
            )

            self._add_item(new_song_view_item)


class ArtistViewItem(EntityItemRow):
    def __init__(self, artist_id: str, callback: Callable):
        super().__init__()
        self.artist_id = artist_id
        self.artist = DBM.artist.get(artist_id)
        self.callback = callback

        self.set_title()
        self.set_subtitle()
        self.set_start_widget()


    def set_title(self):
        self.title = self.artist.name

    def set_subtitle(self):
        songs = DBM.song.get_for_artist(self.artist)
        self.subtitle = f'{len(songs)} Song{"s" if len(songs) > 1 else ""}'

    def set_start_widget(self):
        start_widget = AlbumArt(size=56, placeholder_icon='person-symbolic')
        start_widget.add_css_class('lyris-all-rounded-corners')
        start_widget.set_overflow(Gtk.Overflow.HIDDEN)
        self.start_widget = start_widget