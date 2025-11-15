import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject, GLib, Gst
import threading


class EntityItemView(Adw.Bin):
    def __init__(self):
        super().__init__()
        self._content = Gtk.ListBox()
        self.set_vexpand(True)
        self.set_child(self._content)

        self._content.add_css_class('boxed-list')
        self._content.set_selection_mode(Gtk.SelectionMode.NONE)
        self._content.set_valign(Gtk.Align.START)

    def _add_item(self, item):
        """Add an item to the content asynchronously on the main loop."""
        GLib.idle_add(lambda: self._content.append(item) or False)

    def _load_items(self, arg):
        """Needs to be overwritten by child class, arg will be a list passed in by set_items"""
        pass

    def _set_items(self, arg: list):
        self._content.remove_all()
        thread = threading.Thread(
            target=self._load_items,
            args=(arg,)
        )
        thread.start()