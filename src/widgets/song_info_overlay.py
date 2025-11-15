import gi

from .album_art import AlbumArt
from ..queue import Queue

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject, GLib
from ..utils.time_converter import *
from ..utils.event_bus import GEB
from ..utils.db_manager import DBM
from ..utils.get_cached_cover import get_large_pixbuf_cover

@Gtk.Template(resource_path='/com/github/akamrzero/lyris/song_info_overlay.ui')
class SongInfoOverlay(Adw.Bin):
    __gtype_name__ = 'SongInfoOverlay'

    edit_bottom_sheet_overlay: Adw.BottomSheet = Gtk.Template.Child()
    info_bottom_sheet_overlay: Adw.BottomSheet = Gtk.Template.Child()
    main_content: Adw.Bin = Gtk.Template.Child()
    title_label: Gtk.Label = Gtk.Template.Child()
    album_art_img_container: Adw.Bin = Gtk.Template.Child()
    duration_label: Adw.ActionRow = Gtk.Template.Child()
    album_label: Adw.ActionRow = Gtk.Template.Child()
    artist_label: Adw.ActionRow = Gtk.Template.Child()
    close_info_button: Gtk.Button = Gtk.Template.Child()
    play_btn: Gtk.Button = Gtk.Template.Child()
    queue_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self, child: Gtk.Widget | None = None):
        super().__init__()
        self._current_song_id = None
        self.main_content.set_child(child)
        self.close_info_button.connect('clicked', lambda _: GEB.emit_close_song_info_sheet())
        self.play_btn.connect('clicked', lambda _: Queue().add_song_id(self._current_song_id, play_instantly=True))


    def set_track(self, song_id):
        self._current_song_id = song_id
        self.update_data()


    def show_info(self, show=True):
        self.info_bottom_sheet_overlay.set_open(show)

    def show_edit(self, show=True):
        self.edit_bottom_sheet_overlay.set_open(show)

    def set_child(self, child = None):
        self.main_content.set_child(child)

    def get_child(self):
        return self.main_content.get_child()

    def update_data(self):
        song = DBM.song.get_for_id(self._current_song_id)
        album = DBM.album.get(song.album)
        artist = DBM.artist.get(song.artist)
        song_title = GLib.markup_escape_text(DBM.song.get_for_id(self._current_song_id).name)
        song_album = GLib.markup_escape_text(album.name if album else 'Unknown')
        song_artist = GLib.markup_escape_text(artist.name if artist else 'Unknown')

        self.title_label.set_text(song_title)
        self.duration_label.set_subtitle(ms_to_minutes(song.length))
        self.album_label.set_subtitle(song_album)
        self.artist_label.set_subtitle(song_artist)

        image = AlbumArt(90, covers=[get_large_pixbuf_cover(DBM.song.get_for_id(self._current_song_id).large_cover_file)])
        self.album_art_img_container.set_child(image)