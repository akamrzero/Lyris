import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject, Pango
from typing import Callable

class EntityItemRow(Adw.Bin):
    def __init__(self, callback: Callable | None = None):
        super().__init__()
        self.add_css_class('lyris-very-small-padding-container')
        self.set_valign(Gtk.Align.START)
        self.set_vexpand_set(True)

        self._callback = callback

        self._main_wrapper = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._start_widget = Adw.Bin()
        self._end_widget = Adw.Bin()
        self._title_widget = Gtk.Label()
        self._subtitle_widget = Gtk.Label()

        self.build_ui()
        self._add_controllers()

    @property
    def start_widget(self):
        return self._start_widget.get_child()

    @start_widget.setter
    def start_widget(self, widget: Gtk.Widget):
        self._start_widget.set_child(widget)

    @property
    def end_widget(self):
        return self._end_widget.get_child()

    @end_widget.setter
    def end_widget(self, widget: Gtk.Widget):
        self._end_widget.set_child(widget)

    @property
    def title(self):
        return self._title_widget.get_text()

    @title.setter
    def title(self, title: str):
        self._title_widget.set_text(title)

    @property
    def subtitle(self):
        return self._subtitle_widget.get_text()

    @subtitle.setter
    def subtitle(self, text: str):
        self._subtitle_widget.set_text(text)

    @property
    def callback(self):
        return self._callback
    @callback.setter
    def callback(self, callback: Callable):
        self._callback = callback

    def build_ui(self):
        self._title_widget.set_ellipsize(Pango.EllipsizeMode.END)
        self._title_widget.set_xalign(0)
        self._title_widget.add_css_class('heading')
        self._subtitle_widget.set_ellipsize(Pango.EllipsizeMode.END)
        self._subtitle_widget.set_xalign(0)
        self._subtitle_widget.add_css_class('dimmed')
        self._end_widget.set_valign(Gtk.Align.CENTER)
        self._end_widget.set_halign(Gtk.Align.END)

        self._main_wrapper.set_hexpand(True)
        self._main_wrapper.set_vexpand(True)
        self._main_wrapper.set_spacing(16)

        vwrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vwrapper.append(self._title_widget)
        vwrapper.append(self._subtitle_widget)
        vwrapper.set_hexpand_set(True)
        vwrapper.set_hexpand(True)
        vwrapper.set_valign(Gtk.Align.CENTER)

        self._main_wrapper.append(self._start_widget)
        self._main_wrapper.append(vwrapper)
        self._main_wrapper.append(self._end_widget)

        self.set_child(self._main_wrapper)

    def _add_controllers(self):
        controller = Gtk.GestureClick()
        controller.connect('released', lambda n_press, x, y, user_data: self._on_click())
        self.add_controller(controller)

    def _on_click(self):
        if self.callback:
            self.callback()


