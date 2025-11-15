import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from src.utils.time_converter import ms_to_readable
from src.utils.db_manager import DBM
from src.queue import Queue
from src.widgets.views.song_view import SongView
from src.widgets.entitys.entity_detail_page import EntityDetailPage

class PlaylistDetailPage(EntityDetailPage):
    __gtype_name__ = 'lyrisPlaylistDetailPage'

    def __init__(self, playlist_id):
        super().__init__()
        self.playlist_id = playlist_id
        self.playlist = DBM.playlist.get_for_id(playlist_id)
        self.queue = Queue()

        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.play_button = Gtk.Button(
            child=Adw.ButtonContent(icon_name='media-playback-start', label='Play'),
            hexpand=True,
        )
        self.play_button.add_css_class('suggested-action')
        self.shuffle_button = Gtk.Button(
            child=Adw.ButtonContent(icon_name='media-playlist-shuffle-symbolic', label='Shuffle'),
            hexpand=True,
        )

        self.song_view = SongView()

        self.add_top_button(self.play_button)
        self.add_top_button(self.shuffle_button)

        self.content.append(self.song_view)
        self.set_child(self.content)

        self.set_data()
        self.load_tracks()
        self.connect_signals()




    def set_data(self):
        songs = DBM.playlist.get_songs(self.playlist)
        time = 0
        for song in songs:
            time += song.length
        self.set_title_label(self.playlist.name)
        self.set_details_label(f'{len(songs)} Song{'s' if len(songs) != 1 else ''} • {ms_to_readable(time)}')

    def load_tracks(self):
        self.song_view.set_songs(DBM.playlist.get_songs(self.playlist))


    def connect_signals(self):
        # self._back_button.connect('clicked', lambda _: GEB.emit_viewstack_pop_page())
        self.play_button.connect('clicked', self.on_play_button_clicked)
        self.shuffle_button.connect('clicked', self.on_shuffle_button_clicked)

    def on_shuffle_button_clicked(self, _):
        Queue().set_shuffled(True)
        Queue().add_song_batch(
            DBM.playlist.get_songs(self.playlist),
            True
        )

    def on_play_button_clicked(self, _):
        Queue().add_song_batch(
            DBM.playlist.get_songs(self.playlist),
            True
        )