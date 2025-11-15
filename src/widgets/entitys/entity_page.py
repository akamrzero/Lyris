import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject
from ..marquee_label import MarqueeLabel

class EntityPage(Adw.Bin):
    __gtype_name__ = 'EntityPage'



    def __init__(self):
        super().__init__()


        self._tool_bar_view = Adw.ToolbarView()
        self._content = Adw.Bin(vexpand=True, vexpand_set=True)
        self._top_buttons = Gtk.Box()
        self._back_button = Gtk.Button(icon_name='go-previous')
        self._title_label = Gtk.Label()
        self._details_label = Gtk.Label()

        self.build_ui()


    def build_ui(self):

        info_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        info_wrapper.append(self._title_label)
        info_wrapper.append(self._details_label)


        scroll_wrapper = Gtk.ScrolledWindow()
        scroll_wrapper.set_vexpand(True)
        scroll_wrapper.set_child(self._content)

        self._content.add_css_class('lyris-small-padding-container')

        main_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_wrapper.append(self._top_buttons)
        main_wrapper.append(scroll_wrapper)


        self._tool_bar_view.set_content(main_wrapper)
        super().set_child(self._tool_bar_view)

    def set_title_label(self, label: str):
        self._title_label.set_label(label)

    def set_details_label(self, label: str):
        self._details_label.set_label(label)

    def add_top_button(self, button: Gtk.Button):
        self._top_buttons.append(button)

    def set_child(self, child: Gtk.Widget | None = None) -> None:
        self._content.set_child(child)

    def get_child(self) -> Gtk.Widget | None:
        return self._content.get_child()

