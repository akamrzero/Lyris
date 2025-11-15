import gi

from src.utils.gsettings import gsettings
from src.widgets.app_state import app_state

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio

@Gtk.Template(resource_path='/com/github/akamrzero/lyris/preferences_dialog.ui')
class PreferencesDialog(Adw.PreferencesDialog):
    __gtype_name__ = 'PreferencesDialog'

    background_blur_row: Adw.SwitchRow = Gtk.Template.Child()

    def __init__(self):
        super().__init__()


        self.background_blur_row.connect('notify::active', self.on_background_blur_toggled)
        self.background_blur_row.set_active(gsettings.background_blur)


    def on_background_blur_toggled(self, widget, state):
        state = self.background_blur_row.get_active()
        # self._gsettings.set_boolean('background-blur', state)
        app_state.set_background_blur(state)