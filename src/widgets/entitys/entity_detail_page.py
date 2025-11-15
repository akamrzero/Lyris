import gi

from ..app_state import app_state

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject, Pango
from ..marquee_label import MarqueeLabel

class EntityDetailPage(Adw.Bin):
    __gtype_name__ = 'EntityDetailPage'

    show_window_controls = GObject.Property(type=bool, default=False)

    def __init__(self):
        super().__init__()

        self._tool_bar_view = Adw.ToolbarView()
        self._header_bar = Adw.HeaderBar()
        self._content = Adw.Bin()
        self._top_buttons = Gtk.Box()
        self._title_label = Gtk.Label(xalign=0)
        self._details_label = Gtk.Label(xalign=0)

        self.build_ui()

    def build_ui(self):
        self._details_label.add_css_class('dimmed')
        self._details_label.add_css_class('caption')


        top_buttons_wrapper = Adw.Bin()
        top_buttons_wrapper.set_hexpand(True)
        top_buttons_wrapper.add_css_class('lyris-small-padding-container')
        top_buttons_wrapper.set_child(self._top_buttons)

        self._top_buttons.add_css_class('lyris-linked-buttons')
        self._top_buttons.set_hexpand(True)
        self._top_buttons.set_spacing(8)
        self._top_buttons.set_size_request(-1, 48)

        self._title_label.set_ellipsize(Pango.EllipsizeMode.END)
        self._details_label.set_ellipsize(Pango.EllipsizeMode.END)

        info_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        info_wrapper.append(self._title_label)
        info_wrapper.append(self._details_label)

        self._header_bar.set_show_title(False)
        self._header_bar.pack_start(info_wrapper)
        app_state.bind_property(
            'collapsed',
            self._header_bar,
            'show-end-title-buttons',
            GObject.BindingFlags.SYNC_CREATE
        )

        scroll_wrapper = Gtk.ScrolledWindow()
        scroll_wrapper.set_vexpand(True)
        scroll_wrapper.set_child(self._content)

        self._content.set_valign(Gtk.Align.START)
        self._content.add_css_class('lyris-small-padding-container')

        main_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_wrapper.append(top_buttons_wrapper)
        main_wrapper.append(scroll_wrapper)


        self._tool_bar_view.add_top_bar(self._header_bar)
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

    def set_show_end_title_buttons(self, show_buttons: bool):
        if show_buttons:
            self._header_bar.set_show_end_title_buttons(True)
        else:
            self._header_bar.set_show_end_title_buttons(False)

