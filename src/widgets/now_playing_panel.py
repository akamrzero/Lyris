import gi

from .app_state import AppState, app_state
from ..utils.audio_metadata import get_cover_image

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gst, GObject
from .album_art import AlbumArt
from .music_visualizer import lyrisVisualizer
from .marquee_label import MarqueeLabel
from .seek_bar import SeekBar
from ..utils.event_bus import GEB
from ..utils.db_manager import DBM
from ..queue import Queue
from ..audioplayer import AudioPlayer

class CombinedAlbumArt(Gtk.Overlay):
    def __init__(self):
        super().__init__()
        stylemanager = Adw.StyleManager.get_default()
        color = stylemanager.get_accent_color_rgba()
        # (0.81, 0.78, 1, 1.0)
        self.music_visualizer = lyrisVisualizer(150, 250, (color.red, color.green, color.blue, 1.0), 0.1)
        self.album_art_wrapper = Adw.Bin()
        self.album_art_wrapper.set_halign(Gtk.Align.CENTER)
        self.album_art_wrapper.set_valign(Gtk.Align.CENTER)
        self.album_art_wrapper.add_css_class('lyris-all-rounded-corners')
        self.album_art_wrapper.set_overflow(Gtk.Overflow.HIDDEN)

        self.set_child(self.music_visualizer)
        self.add_overlay(self.album_art_wrapper)

    def update(self, data):
        self.music_visualizer.update(data)

    def set_album_art(self, album_art: AlbumArt):
        self.album_art_wrapper.set_child(album_art)



@Gtk.Template(resource_path='/com/github/akamrzero/lyris/now_playing_panel.ui')
class NowPlayingPanel(Gtk.Box):
    __gtype_name__ = 'NowPlayingPanel'

    album_art_container: Adw.Bin = Gtk.Template.Child()
    play_pause_button: Gtk.Button = Gtk.Template.Child()
    next_button: Gtk.Button = Gtk.Template.Child()
    previous_button : Gtk.Button= Gtk.Template.Child()
    hide_library_button: Gtk.ToggleButton = Gtk.Template.Child()
    repeat_button: Gtk.ToggleButton = Gtk.Template.Child()
    shuffle_button: Gtk.ToggleButton = Gtk.Template.Child()
    volume_control_button: Gtk.MenuButton = Gtk.Template.Child()
    song_info_box: Gtk.Box = Gtk.Template.Child()
    seek_bar_container: Adw.Bin = Gtk.Template.Child()
    bottom_container: Gtk.Box = Gtk.Template.Child()
    volume_control_adjustment: Gtk.Adjustment = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.combined_album_art = CombinedAlbumArt()
        self.album_art_container.set_child(self.combined_album_art)
        self.seek_bar = SeekBar()
        self.seek_bar_container.set_child(self.seek_bar)

        self.volume_control_adjustment.bind_property('value', AudioPlayer(), 'volume', GObject.BindingFlags.BIDIRECTIONAL)
        self.hide_library_button.set_active(app_state.hide_library)
        self.on_hide_library_button_active_changed()
        self.hide_library_button.connect('toggled', self.on_hide_library_button_toggled)
        self.hide_library_button.connect('notify::active', self.on_hide_library_button_active_changed)

        Queue().connect('shuffle-toggled', lambda _, shuffle: self.shuffle_button.set_active(shuffle))
        self.shuffle_button.connect('toggled', lambda _: Queue().set_shuffled(self.shuffle_button.get_active()))
        Queue().connect('loop-toggled', lambda _,loop: self.repeat_button.set_active(loop))
        self.repeat_button.connect('toggled', lambda _: Queue().set_loop_current(self.repeat_button.get_active()))

        self.title_label = MarqueeLabel('')
        self.title_label.set_xalign(0.5)
        self.title_label.add_css_class('title-1')
        self.artist_label = MarqueeLabel('')
        self.artist_label.set_xalign(0.5)
        self.song_info_box.append(self.title_label)
        self.song_info_box.append(self.artist_label)


        self.connect_local_signals()
        self.connect_global_signals()


    def set_play_pause_icon(self,):
        state = AudioPlayer().get_state()
        if state == Gst.State.PLAYING:
            self.play_pause_button.set_icon_name('media-playback-pause-symbolic')
        else:
            self.play_pause_button.set_icon_name('media-playback-start-symbolic')


    def on_track_changed(self, _, song, _start_playback):
        song = DBM.song.get_for_id(song)
        self.set_play_pause_icon()
        self.title_label.set_text(song.name)
        self.artist_label.set_text(song.artist.name if song.artist else 'Unknown Artist')
        self.combined_album_art.set_album_art(AlbumArt(250, covers=[get_cover_image(song.file_path)]))
        self.seek_bar.duration = song.length

    def on_playback_progress(self, _, progress):
        self.seek_bar.value = progress

    def connect_local_signals(self):
        self.play_pause_button.connect('clicked', lambda _: AudioPlayer().toggle_playback())
        self.next_button.connect('clicked', lambda _: Queue().next_song())
        self.previous_button.connect('clicked', lambda _: Queue().previous_song())

    def connect_global_signals(self):
        Queue().connect('song-changed', self.on_track_changed)
        GEB.connect_toggle_playback_confirm(self.set_play_pause_icon)
        GEB.connect_song_changed(self.on_track_changed)
        GEB.connect_spectrum_data_updated(lambda _, data: self.combined_album_art.update(data))
        AudioPlayer().connect('playback-state-changed', lambda _: self.set_play_pause_icon())

    def on_hide_library_button_toggled(self, *_):
        app_state.set_hide_library(self.hide_library_button.get_active())

    def on_hide_library_button_active_changed(self, *_):
        print('niwuef')
        if self.hide_library_button.get_active():
            self.hide_library_button.set_icon_name('arrows-pointing-inward-symbolic')
        else:
            self.hide_library_button.set_icon_name('arrows-pointing-outward-symbolic')


