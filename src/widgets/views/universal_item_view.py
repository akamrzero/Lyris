import gi

from src.widgets.entitys.entity_item_view import EntityItemView

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject

from src.widgets.views import AlbumView, ArtistView, PlaylistView, SongView

class UniversalItemViewGroup(Gtk.Box):
    def __init__(self, title: str, view: EntityItemView):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self._title = Gtk.Label(label=title, xalign=0, css_classes=['heading'])
        self.view = view

        self.append(self._title)
        self.append(self.view)

    @property
    def title(self) -> str:
        return self._title.get_text()

    @title.setter
    def title(self, value: str):
        self._title.set_text(value)


class UniversalItemView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        self.album_view = AlbumView()
        self.artist_view = ArtistView()
        self.playlist_view = PlaylistView()
        self.song_view = SongView()

        self.album_view_group = UniversalItemViewGroup(title='Albums', view=self.album_view)
        self.artist_view_group = UniversalItemViewGroup(title='Artists', view=self.artist_view)
        self.playlist_view_group = UniversalItemViewGroup(title='Playlists', view=self.playlist_view)
        self.song_view_group = UniversalItemViewGroup(title='Songs', view=self.song_view)

        self.groups = {
            'album': self.album_view_group,
            'artist': self.artist_view_group,
            'playlist': self.playlist_view_group,
            'song': self.song_view_group
        }

        self.append(self.song_view_group)
        self.append(self.album_view_group)
        self.append(self.artist_view_group)
        self.append(self.playlist_view_group)

    def set_groups_visible(self, *groups: str):
        for group in groups:
            if group in self.groups.keys():
                self.groups[group].set_visible(True)

        keys = self.groups.keys()
        for key in keys:
            if key not in groups:
                self.groups[key].set_visible(False)

    def set_albums(self, albums):
        self.album_view.set_albums(albums)

    def set_artists(self, artists):
        self.artist_view.set_artists(artists)

    def set_playlists(self, playlists):
        self.playlist_view.set_playlists(playlists)

    def set_songs(self, songs):
        self.song_view.set_songs(songs)

