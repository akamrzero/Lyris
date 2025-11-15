import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject
from typing import Callable



class NavigationTabBarItem(Gtk.Button):
    def __init__(
            self,
            identifier: str,
            icon_name: str,
            title: str = '',
            funktion: Callable = lambda: None,
            activatable_only: bool = False,

    ):
        super().__init__()
        self.identifier = identifier
        self.function = funktion
        self.activatable_only = activatable_only
        self._tab_bar = None
        self.set_hexpand(True)

        self.set_icon_name(icon_name)
        self.set_tooltip_text(title)
        self.set_has_tooltip(True)
        self.add_css_class('lyris-navbar-button')

        self.connect('clicked', self.on_clicked)


    @property
    def title(self) -> str:
        return self.get_tooltip_text()

    @title.setter
    def title(self, title: str):
        self.set_tooltip_text()

    def set_highlighted(self, highlighted: bool):
        if highlighted:
            self.add_css_class('accent')
        else:
            self.remove_css_class('accent')


    def on_clicked(self, button: Gtk.Button):
        if self.activatable_only:
            self.function()
            return
        self.select()
        self.function()

    def select(self):
        if self._tab_bar:
            self._tab_bar.unselect_all()
        self.set_highlighted(True)

    def set_tab_bar(self, tab_bar):
        self._tab_bar = tab_bar

class NavigationTabBarSeperator(Gtk.Separator):
    def __init__(self):
        super().__init__()

    def set_tab_bar(self, tab_bar):
        pass

    def set_highlighted(self, highlighted: bool):
        pass

@Gtk.Template(resource_path='/com/github/akamrzero/lyris/tab_bar.ui')
class TabBar(Adw.Bin):
    __gtype_name__ = 'TabBar'

    content: Gtk.Box = Gtk.Template.Child()

    def __init__(self, items:list[NavigationTabBarItem]):
        super().__init__()

        self.items = items
        self.items[0].add_css_class('lyris-navbar-first-button')
        self.items[-1].add_css_class('lyris-navbar-last-button')
        for item in items:
            item.set_tab_bar(self)
            self.append(item)


    def append(self, widget: Gtk.Widget):
        self.content.append(widget)

    def unselect_all(self):
        for item in self.items:
            item.set_highlighted(False)

    def select_item(self, identifier: str):
        for item in self.items:
            if item.identifier == identifier:
                item.select()
