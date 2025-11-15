import gi

from .entitys.entity_detail_page import EntityDetailPage

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from ..utils.db_manager import DBM
from ..queue import Queue
from.views.song_view import SongView

class AlbumDetailPage(EntityDetailPage):
    __gtype_name__ = 'AlbumDetailPage'

    content: Gtk.Box = Gtk.Template.Child()


    def __init__(self, album_id):
        super().__init__()
        self.album_id = album_id
        self.album = DBM.album.get(album_id)

        self.content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
        )
        self.shuffle_button = Gtk.Button(
            child=Adw.ButtonContent(icon_name='media-playlist-shuffle-symbolic', label='Shuffle'),
            hexpand=True,
        )
        self.shuffle_button.add_css_class('suggested-action')
        self.shuffle_button.add_css_class('pill')
        self._top_buttons.remove_css_class('lyris-linked-buttons')

        self._song_view = SongView()
        self.content.append(self._song_view)

        self.set_child(self.content)
        self.add_top_button(self.shuffle_button)

        self.set_data()
        self.load_tracks()
        self.connect_signals()


    def set_data(self):
        songs = DBM.song.get_for_album(self.album_id)
        self.set_title_label(self.album.name)
        self.set_details_label(f'{len(songs)} Song{'s' if len(songs) != 1 else''}')

    def load_tracks(self):
        self._song_view.set_songs(DBM.song.get_for_album(self.album_id))


    def connect_signals(self):
        self.shuffle_button.connect('clicked', self.on_shuffle_button_clicked)

    def on_shuffle_button_clicked(self, _):
        Queue().set_shuffled(True)
        Queue().add_song_batch(
            DBM.song.get_for_album(self.album_id),
            True
        )