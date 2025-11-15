import gi

from ..audioplayer import AudioPlayer

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject, Gst

from .marquee_label import MarqueeLabel
from .album_art import AlbumArt
from ..queue import Queue
from ..utils.db_manager import DBM
from ..utils.get_cached_cover import get_small_pixbuf_cover

@Gtk.Template(resource_path='/com/github/akamrzero/lyris/small_song_preview.ui')
class SmallSongPreview(Adw.Bin):
    __gtype_name__ = 'SmallSongPreview'

    expanded = GObject.Property(type=bool, default=False)

    revealer: Gtk.Revealer = Gtk.Template.Child()
    cover_container: Adw.Bin = Gtk.Template.Child()
    info_container: Gtk.Box = Gtk.Template.Child()
    play_pause_button: Gtk.Button = Gtk.Template.Child()
    next_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        # self._album_art = AlbumArt(32)
        self._title_label = MarqueeLabel()
        self._title_label.add_css_class('heading')
        self._artist_label = MarqueeLabel()
        self._artist_label.add_css_class('dimmed')
        self._artist_label.add_css_class('body')

        self.set_margin_start(12)
        self.set_margin_end(12)

        self.cover_container.set_child(AlbumArt(42))
        self.info_container.append(self._title_label)
        self.info_container.append(self._artist_label)

        self.connect_signals()

        self.revealer.set_reveal_child(False)

        self.bind_property(
            'expanded',
            self.revealer,
            'reveal_child',
            GObject.BindingFlags.SYNC_CREATE
        )

    def on_track_changed(self, _, song, _start_playback):
        # if not self.revealer.get_child_visible():
        #     self.revealer.set_child_visible(True)
        song = DBM.song.get_for_id(song)
        self.set_play_pause_icon()
        self._title_label.set_text(song.name)
        self._artist_label.set_text(song.artist.name if song.artist else 'Unknown')
        self.cover_container.set_child(AlbumArt(42, covers=[get_small_pixbuf_cover(song.small_cover_file)]))

    def set_play_pause_icon(self):
        state = AudioPlayer().get_state()
        if state == Gst.State.PLAYING:
            self.play_pause_button.set_icon_name('media-playback-pause-symbolic')
        else:
            self.play_pause_button.set_icon_name('media-playback-start-symbolic')

    def connect_signals(self):
        Queue().connect('song-changed', self.on_track_changed)
        AudioPlayer().connect('playback-state-changed', lambda _: self.set_play_pause_icon())
        self.play_pause_button.connect('clicked', lambda _: AudioPlayer().toggle_playback())
        self.next_button.connect('clicked', lambda _: Queue().next_song())

    def set_expanded(self, expanded: bool):
        self.revealer.set_reveal_child(expanded)


