from typing import Callable

import gi

from src.audioplayer import AudioPlayer

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gst

from src.utils.db_manager import DBM
from src.queue import Queue
from src.widgets.entitys.entity_item_row import EntityItemRow
from src.utils.get_cached_cover import get_cached_cover, CoverSize
from src.widgets.playing_eq_icon import PlayingEqIcon
from src.utils.event_bus import GEB
from src.widgets.album_art import AlbumArt
from src.widgets.entitys.entity_item_view import EntityItemView


class SongView(EntityItemView):
    def set_songs(self, songs):
        self._set_items(songs)

    def _load_items(self, arg):
        for i, song_id in enumerate(arg):
            batch = arg[:i].copy()
            new_song_view_item = SongViewItem(
                song_id,
                lambda song=song_id, song_batch=batch: Queue().add_song_batch(
                    batch,
                    True,
                    song
                )
            )

            self._add_item(new_song_view_item)


class SongViewItem(EntityItemRow):
    def __init__(self, song_id, callback: Callable):
        super().__init__()
        self.song_id = song_id
        self.song = DBM.song.get_for_id(self.song_id)
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
        album_art = AlbumArt(56, covers=[get_cached_cover(self.song.cover_base_filename, CoverSize.small)])
        self.start_widget = album_art

    def set_title(self):
        if self.song.name:
            self.title = self.song.name

    def set_subtitle(self):
        if self.song.artist:
            artist = DBM.artist.get(self.song.artist)
            if artist.name:
                self.subtitle = artist.name

    def set_eq_icon(self, visible: bool, active: bool=True):
        if not visible:
            self._eq_icon_wrapper.set_child(None)

        else:
            eq_icon = PlayingEqIcon(
                20,
                20,
                3,
                4,
                (1.0, 1.0, 1.0),
                active=active,
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
        self._options_button.connect('clicked', self._on_options_clicked)
        Queue().connect('song-changed', self._on_song_changed)
        AudioPlayer().connect('playback-state-changed', self._on_playback_state_changed)

    def _on_song_changed(self, widget, song_id, start_playback):
        if song_id == str(self.song_id.id):
            self.set_eq_icon(True, start_playback)

        else:
            self.set_eq_icon(False)

    def _on_options_clicked(self, widget):
        GEB.emit_open_song_info_sheet(self.song_id)

    def _on_playback_state_changed(self, widget):
        playback_state = AudioPlayer().playback_state
        eq_icon = self._eq_icon_wrapper.get_child()
        if  eq_icon and isinstance(eq_icon, PlayingEqIcon):
            if playback_state == Gst.State.PLAYING:
                self._eq_icon_wrapper.get_child().active = True
            else:
                self._eq_icon_wrapper.get_child().active = False


