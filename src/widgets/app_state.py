from gi.repository import GObject, Gio

class AppState(GObject.GObject):
    __gtype_name__ = 'AppState'

    collapsed = GObject.Property(type=bool, default=False)
    hide_library = GObject.Property(type=bool, default=False)
    background_blur = GObject.Property(type=bool, default=False)

    def set_collapsed(self, collapsed: bool):
        self.collapsed = collapsed

    def set_hide_library(self, hide_library: bool):
        self.hide_library = hide_library
        self._gsettings.set_boolean('hide-library', hide_library)

    def set_background_blur(self, background_blur: bool):
        self.background_blur = background_blur
        self._gsettings.set_boolean('background-blur', background_blur)

    def __init__(self):
        super().__init__()
        self._gsettings = Gio.Settings.new('com.github.akamrzero.lyris')
        self.set_hide_library(self._gsettings.get_boolean('hide-library'))
        self.set_background_blur(self._gsettings.get_boolean('background-blur'))


app_state = AppState()