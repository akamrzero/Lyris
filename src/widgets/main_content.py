import gi

from src.widgets.artists_page import ArtistsPage
from src.widgets.albums_page import AlbumsPage
from src.widgets.navigation_tab_bar import NavigationTabBarItem, TabBar
from src.widgets.playlists_page import PlaylistsPage
from src.widgets.playlist_detail_page import PlaylistDetailPage
from src.widgets.view_stack import ViewStackPage, ViewStack
from src.widgets.small_song_preview import SmallSongPreview
from src.widgets.songs_page import SongsPage
from src.utils.event_bus import GEB
from src.widgets.song_info_overlay import SongInfoOverlay
from src.widgets.search_page import SearchPage

from .app_state import app_state
from .home_page import HomePage

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Adw, GObject, Gio

class MainContent(Adw.Bin):
    __gtype_name__ = 'MainContent'

    def __init__(self):
        super().__init__()
        self._split_view = None


        self._toolbar_view = Adw.ToolbarView()
        self._header_bar = Adw.HeaderBar()

        self._song_info_overlay = SongInfoOverlay()
        self._overlay = Gtk.Overlay()
        self._bottom_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.small_song_preview = SmallSongPreview()
        self._bottom_navbar = TabBar(self.get_navigation_items())
        self.albums_page = ViewStackPage(AlbumsPage())
        self.artists_page = ViewStackPage(ArtistsPage())
        self.home_page = ViewStackPage(HomePage())
        self.search_page = ViewStackPage(SearchPage())
        self.songs_page = ViewStackPage(SongsPage())
        self.playlists_page = ViewStackPage(PlaylistsPage())
        self._view = ViewStack([
            self.home_page,
            self.songs_page,
            self.playlists_page,
            self.artists_page,
            self.albums_page
        ], self.search_page)


        GEB.connect_viewstack_push_page(lambda _, page: self._view.push(page))
        GEB.connect_viewstack_pop_page(lambda _: self._view.pop())
        GEB.connect_open_song_info_sheet(self._on_song_info_opened)
        GEB.connect_close_song_info_sheet(self._on_song_info_close)

        self.albums_page.set_hexpand(True)
        self.artists_page.set_hexpand(True)
        self.home_page.set_hexpand(True)
        self.playlists_page.set_hexpand(True)

        self.pages = {
            'home': self.home_page,
            'songs': self.songs_page,
            'albums': self.albums_page,
            'artists': self.artists_page,
            'playlists': self.playlists_page,
        }



        self._build_ui()

        app_state.bind_property(
            'collapsed',
            self.small_song_preview,
            'expanded',
            GObject.BindingFlags.SYNC_CREATE
        )

        app_state.bind_property(
            'collapsed',
            self._view,
            'end_buttons_visible',
            GObject.BindingFlags.SYNC_CREATE
        )

        self.open_last_page()

    def on_navigate(self, _, page_name:str):
        self._view.set_main_child(self.pages[page_name])
        self._bottom_navbar.select_item(page_name)

        settings = Gio.Settings.new('com.github.akamrzero.lyris')
        settings.set_string('last-opened-page', page_name)



    def _build_ui(self):
        self._header_bar.set_show_end_title_buttons(False)

        self._toolbar_view.set_vexpand(True)
        self._toolbar_view.set_hexpand(True)
        self.set_child(self._toolbar_view)

        vwrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._bottom_container.set_margin_bottom(76)
        self._bottom_container.set_valign(Gtk.Align.END)
        self._bottom_container.append(self.small_song_preview)
        self._overlay.add_overlay(self._bottom_container)

        vwrapper.append(self._view)
        vwrapper.append(self._bottom_navbar)

        self._toolbar_view.set_content(self._song_info_overlay)
        self._song_info_overlay.set_child(self._overlay)
        self._overlay.set_child(vwrapper)

    def get_navigation_items(self):
        items = [
            NavigationTabBarItem(
                'home',
                'go-home-symbolic', #
                'Home',
                lambda: self.on_navigate(None, 'home')
            ),
            NavigationTabBarItem(
                'songs',
                'music-note-single-symbolic',
                'Songs',
                lambda: self.on_navigate(None, 'songs')
            ),
            NavigationTabBarItem(
                'playlists',
                'library-music-symbolic',
                'Playlists',
                lambda: self.on_navigate(None, 'playlists')
                                   ),
            NavigationTabBarItem(
                'artists',
                'music-artist-symbolic',
                'Artists',
                lambda: self.on_navigate(None, 'artists')
            ),
            NavigationTabBarItem(
                'albums',
                'library-artists-symbolic',
                'Albums',
                lambda: self.on_navigate(None, 'albums')
            ),
        ]
        return items

    def _on_song_info_opened(self, _, song):
        self._song_info_overlay.set_track(song)
        self._song_info_overlay.show_info(True)

    def _on_song_info_close(self, _):
        self._song_info_overlay.show_info(False)

    def open_last_page(self):
        settings = Gio.Settings.new('com.github.akamrzero.lyris')
        page = settings.get_string('last-opened-page')
        print(page)
        self.on_navigate(None, page)




