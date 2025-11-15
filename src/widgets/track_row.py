import gi

from ..models.playlist import Playlist

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from typing import Callable, Tuple
from .playing_eq_icon import PlayingEqIcon
from ..utils.event_bus import GEB
from ..utils.db_manager import DBM
from ..utils.audio_metadata import get_cover_image
from ..queue import Queue
from ..audioplayer import AudioPlayer


from .entitys.entity_item_row import EntityItemRow

class TrackRow(EntityItemRow):
    def __init__(self, data: tuple[str, str], callback: Callable):
        super().__init__()
        self.song_id = data[0]
        self.song = DBM.song.get_for_id(self.song_id)
        self.playlist_id = data[1]
        self.playlist = DBM.playlist.get_for_id(self.playlist_id)
        self.callback = callback

        self._end_widget_wrapper = Gtk.Box()
        self._options_button = Gtk.Button()
        self._eq_icon_wrapper = Adw.Bin()

        self.set_song_cover()
        self.set_title()
        self.set_subtitle()
        self.set_end_widget()
        self.connect_signals()

    def set_song_cover(self):
        try:
            cover_image = get_cover_image(self.song.file_path)
            if cover_image:
                image_container = Adw.Bin()
                image = Gtk.Image.new_from_pixbuf(cover_image)
                image.set_pixel_size(56)
                image_container.set_child(image)
                image.add_css_class('lyris-small-rounded-corners')
                image.set_overflow(Gtk.Overflow.HIDDEN)
                self.start_widget = image_container
        except IOError:
            return

    def set_title(self):
        if self.song.name:
            self.title = self.song.name

    def set_subtitle(self):
        if self.song.artist:
            print(self.song.artist)
            artist = DBM.artist.get(self.song.artist)
            if artist.name:
                self.subtitle = artist.name

    def set_eq_icon(self, visible: bool):
        if not visible:
            self._eq_icon_wrapper.set_child(None)

        else:
            eq_icon = PlayingEqIcon(
                20,
                20,
                3,
                4,
                (1.0, 1.0, 1.0),
            )
            self._eq_icon_wrapper.set_child(eq_icon)


    def set_end_widget(self):
        self._options_button.set_icon_name('view-more-symbolic')
        self._options_button.add_css_class('flat')
        self._options_button.add_css_class('circular')
        self._options_button.set_valign(Gtk.Align.CENTER)

        self._eq_icon_wrapper.set_valign(Gtk.Align.CENTER)

        self._end_widget_wrapper.set_orientation(Gtk.Orientation.HORIZONTAL)
        self._end_widget_wrapper.set_spacing(8)
        self._end_widget_wrapper.append(self._eq_icon_wrapper)
        self._end_widget_wrapper.append(self._options_button)
        self.end_widget = self._end_widget_wrapper

        if Queue().get_current_song_id() == self.song.id:
            self.set_eq_icon(True)

    def connect_signals(self):
        # GEB.connect_track_changed(self._on_track_changed)
        # GEB.connect_current_track_provided(self._on_track_provided)
        self._options_button.connect('clicked', self._on_options_clicked)
        Queue().connect('song-changed', self._on_song_changed)

    def _on_song_changed(self, widget, song_id):
        print(song_id, self.song_id)
        if song_id == self.song:
            self.set_eq_icon(True)
        else:
            self.set_eq_icon(False)

    # def _on_track_provided(self, widget, track: Track):
    #     if track == self.track.song:
    #         self.set_eq_icon(True)

    def _on_options_clicked(self, widget):
        GEB.emit_open_song_info_sheet(self.song_id)


