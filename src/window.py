# window.py
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

from gi.repository import Adw
from gi.repository import Gtk, Gio

from .utils.gsettings import gsettings
from .widgets.blur_background import BlurBackground
# from .widgets.playlists_view import PlaylistView
from .widgets.now_playing_panel import NowPlayingPanel
from .widgets.main_content import MainContent
from .widgets.split_view import LyrisSplitView

class LyrisWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'LyrisWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.application = kwargs['application']

        self.main_content = MainContent()

        self.now_playing_panel = NowPlayingPanel()

        self.split_view = LyrisSplitView(self.main_content, self.now_playing_panel, 390, 922)

        self.blur_background = BlurBackground(self.split_view)


        self.set_content(self.blur_background)

        self.set_size_request(390, 500)


        self.set_default_size(gsettings.window_width, gsettings.window_height)

        self.connect('close-request', self._on_close_request)

    def _on_close_request(self, *args):
        gsettings.window_width = self.get_width()
        gsettings.window_height = self.get_height()












