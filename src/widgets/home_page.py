import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject
from .view_stack import ViewStackPage

class HomePage(Adw.Bin):
    def __init__(self):
        super().__init__()

        label = Gtk.Label(label='Home')
        self.set_child(label)