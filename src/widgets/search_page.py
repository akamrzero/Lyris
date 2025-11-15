from gi.repository import Gtk, Adw

from .views.universal_item_view import UniversalItemView
from ..utils.db_manager import DBM
from .entitys.entity_page import EntityPage


@Gtk.Template(resource_path='/com/github/akamrzero/lyris/search_page_content.ui')
class SearchPageContent(Adw.Bin):
    __gtype_name__ = 'SearchPageContent'
    entry: Gtk.Entry = Gtk.Template.Child()
    song_view_container: Adw.Bin = Gtk.Template.Child()

    all_toggle: Gtk.ToggleButton = Gtk.Template.Child()
    albums_toggle: Gtk.ToggleButton = Gtk.Template.Child()
    artists_toggle: Gtk.ToggleButton = Gtk.Template.Child()
    playlists_toggle: Gtk.ToggleButton = Gtk.Template.Child()
    songs_toggle: Gtk.ToggleButton = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self._toggles = {
            'all': self.all_toggle,
            'albums': self.albums_toggle,
            'artists': self.artists_toggle,
            'playlists': self.playlists_toggle,
            'songs': self.songs_toggle
        }
        for toggle in self._toggles.keys():
            self._toggles[toggle].add_css_class('lyris-filter-toggle')
            self._toggles[toggle].connect('toggled', lambda *_: self.on_active_toggle_changed())

        self._empty_page = Adw.StatusPage(icon_name='system-search-symbolic', title='Search', description='Enter a query to search', hexpand=True)
        self._no_result_page = Adw.StatusPage(icon_name='system-search-symbolic', description='Try a different search term or check your filter.', hexpand=True)
        self._universal_view = UniversalItemView()
        self._universal_view.set_vexpand(True)
        self.song_view_container.set_child(self._empty_page)
        self.entry.connect('notify::text', lambda *_: self.on_search_query_changed(self.entry.get_text()))

    def on_search_query_changed(self, search_query):
        if search_query:
            self.song_view_container.set_child(self._universal_view)
            match self.get_active_toggle():
                case 'all':
                    album_results = list(DBM.album.search(search_query))
                    artists_results = list(DBM.artist.serach(search_query))
                    playlists_results = list(DBM.playlist.search(search_query))
                    songs_results = list(DBM.song.search(search_query))

                    if not album_results and not artists_results and not playlists_results and not songs_results:
                        self._no_result_page.set_title(f'No results for "{search_query}"')
                        self.song_view_container.set_child(self._no_result_page)
                    else:
                        self._universal_view.set_albums(album_results)
                        self._universal_view.set_artists(artists_results)
                        self._universal_view.set_playlists(playlists_results)
                        self._universal_view.set_songs(songs_results)

                        visible_groups = [
                            name for name, result in (
                                ('album', album_results),
                                ('artist', artists_results),
                                ('playlist', playlists_results),
                                ('song', songs_results)
                            ) if result
                        ]

                        self._universal_view.set_groups_visible(*visible_groups)

                case 'albums':
                    album_results = list(DBM.album.search(search_query))
                    if not album_results:
                        self._no_result_page.set_title(f'No results for "{search_query}"')
                        self.song_view_container.set_child(self._no_result_page)
                    else:
                        self._universal_view.set_albums(album_results)

                case 'artists':
                    artist_results = list(DBM.artist.serach(search_query))
                    if not artist_results:
                        self._no_result_page.set_title(f'No results for "{search_query}"')
                        self.song_view_container.set_child(self._no_result_page)
                    else:
                        self._universal_view.set_artists(artist_results)

                case 'playlists':
                    playlist_results = list(DBM.playlist.search(search_query))
                    if not playlist_results:
                        self._no_result_page.set_title(f'No results for "{search_query}"')
                        self.song_view_container.set_child(self._no_result_page)
                    else:
                        self._universal_view.set_playlists(playlist_results)

                case 'songs':
                    song_results = list(DBM.song.search(search_query))
                    if not song_results:
                        self._no_result_page.set_title(f'No results for "{search_query}"')
                        self.song_view_container.set_child(self._no_result_page)
                    else:
                        self._universal_view.set_songs(song_results)
        else:
            self.song_view_container.set_child(self._empty_page)

    def get_active_toggle(self):
        for toggle in self._toggles.keys():
            if self._toggles[toggle].get_active():
                return toggle
        return None

    def on_active_toggle_changed(self):
        self.on_search_query_changed(self.entry.get_text())
        match self.get_active_toggle():
            case 'all':
                self._universal_view.set_groups_visible('album', 'artist', 'song', 'playlist')
            case 'songs':
                self._universal_view.set_groups_visible('song')
            case 'artists':
                self._universal_view.set_groups_visible('artist')
            case 'playlists':
                self._universal_view.set_groups_visible('playlist')
            case 'albums':
                self._universal_view.set_groups_visible('album')

class SearchPage(EntityPage):
    __gtype_name__ = 'SearchPage'

    def __init__(self,):
        super().__init__()

        self.content = SearchPageContent()
        self.set_child(self.content)

