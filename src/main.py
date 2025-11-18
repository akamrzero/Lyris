# main.py
#
# Copyright (C) 2025 akamrzero
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi
import peewee

from .utils.media_indexer import media_indexer
from .utils.mediastore import media_store

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gio, Adw, GLib, Gtk
from .window import lyrisWindow
from .audioplayer import AudioPlayer
# from .models.library import Library
from .mpris import MPRIS

from .models import db, init_db
from .models import Song
from .models import Album
from .models import Artist
from .models import PlaylistSong
from .models import Playlist
from .utils.db_manager import DBM
from .utils.index_folder import index_folder
from gettext import gettext as _
from src.widgets.preferences_dialog import PreferencesDialog




class LyrisApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='com.github.akamrzero.Lyris',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path='/com/github/akamrzero/lyris')

        GLib.set_application_name(_('Lyris'))

        init_db(Artist, Album, Playlist, Song, PlaylistSong)
        # index_folder(DBM, GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC))
        media_store.add_folder(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC))
        print(media_store.folders)
        media_indexer.index()

        # self.library = Library(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC))

        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about)
        self.create_action('preferences', self.on_preferences_action, ['<primary>comma'])
        self.create_action('shortcuts', lambda *_: print('Shortcuts'), ['<primary>question'])

        self.connect('shutdown', self.on_shutdown)
        audio_player = AudioPlayer()



    def do_startup(self):
        Adw.Application.do_startup(self)

        style_manager = Adw.StyleManager.get_default()

        # Start MPRIS server
        self.mpris = MPRIS(self)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window
        if not self.win:
            self.win = lyrisWindow(application=self)

        self.win.present()



    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')
        dialog = PreferencesDialog()
        # dialog.set_parent(self.win)
        dialog.present(self.win)


    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)



    def on_about(self, _action, _param):
        builder = Gtk.Builder.new_from_resource('/com/github/akamrzero/lyris/about_window.ui')
        about: Adw.AboutDialog = builder.get_object('AboutWindow')

        about.present(self.win)

    def on_shutdown(self, *args):
        # self.save_queue()
        print('Bye bye')




def main(version):
    """The application's entry point."""
    print(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC))
    app = LyrisApplication()
    return app.run(sys.argv)
