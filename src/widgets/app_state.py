from gi.repository import GObject, Gio

from src.utils.gsettings import gsettings


class AppState(GObject.GObject):
    __gtype_name__ = 'AppState'

    collapsed = GObject.Property(type=bool, default=False)
    hide_library = GObject.Property(type=bool, default=False)
    background_blur = GObject.Property(type=bool, default=False)

    def set_collapsed(self, collapsed: bool):
        self.collapsed = collapsed

    def set_hide_library(self, hide_library: bool):
        self.hide_library = hide_library
        gsettings.hide_library = hide_library

    def set_background_blur(self, background_blur: bool):
        self.background_blur = background_blur
        gsettings.background_blur = background_blur

    def __init__(self):
        super().__init__()
        self.set_hide_library(gsettings.hide_library)
        self.set_background_blur(gsettings.background_blur)


app_state = AppState()