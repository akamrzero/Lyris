import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject

class ViewStackBaseItem(Adw.Bin):
    def __init__(self, items, search_page):
        super().__init__()
        self.search_button = Gtk.ToggleButton(icon_name='system-search-symbolic')
        self.search_button.connect('toggled', lambda _: self.set_search_page_visible(self.search_button.get_active()))
        self.search_page = search_page
        self.main_menu_button = Gtk.MenuButton(icon_name='open-menu-symbolic', menu_model=self.get_menu_model())

        self.toolbar_view = Adw.ToolbarView()

        self.header = Adw.HeaderBar()
        self.header.pack_start(self.search_button)
        self.header.pack_end(self.main_menu_button)

        self.toolbar_view.add_top_bar(self.header)
        self.stack = Gtk.Stack()
        self.search_stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE)
        self.search_stack.add_named(self.stack, 'stack')
        self.search_stack.add_named(self.search_page, 'search')
        self.toolbar_view.set_content(self.search_stack)
        self.set_child(self.toolbar_view)

        for item in items:
            self.stack.add_child(item)
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

    def set_search_page_visible(self, visible: bool):
        if visible:
            self.search_stack.set_visible_child_name('search')
            self.search_page.get_content().content.entry.grab_focus()
        else:
            self.search_stack.set_visible_child_name('stack')

    def set_visible_child(self, child: Gtk.Widget):
        self.search_button.set_active(False)
        self.stack.set_visible_child(child)

    def set_end_buttons_visible(self, visible: bool):
        self.header.set_show_end_title_buttons(visible)

    def get_menu_model(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/com/github/akamrzero/lyris/main_menu.ui')
        menu = builder.get_object('MainMenu')
        return menu


class ViewStack(Adw.Bin):
    end_buttons_visible = GObject.Property(type=bool, default=False)

    def __init__(self, main_items: list[Gtk.Widget] = None, search_page=None):
        super().__init__()

        self._navigation_view = Adw.NavigationView()

        self.main_page_item = ViewStackBaseItem(main_items, search_page)

        self.main_page = Adw.NavigationPage(
            can_pop=False,
            child=self.main_page_item,
            title='Lyris'
        )

        self._navigation_view.add(self.main_page)

        self.set_child(self._navigation_view)

        self.bind_property('end_buttons_visible', self.main_page_item.header, 'show_end_title_buttons', GObject.BindingFlags.SYNC_CREATE)

    def _add_mouse_event(self):
        controller = Gtk.GestureClick()
        controller.set_button(8)
        controller.connect('pressed', lambda c, n_press, x, y: self.pop() if c.get_current_button() else None)
        self.add_controller(controller)

    def set_main_child(self, child: Gtk.Widget):
        self._navigation_view.pop_to_page(self.main_page)
        self.main_page_item.set_visible_child(child)

    def push(self, widget: Gtk.Widget=None):
        page = Adw.NavigationPage(child=widget, title='none')
        self._navigation_view.push(page)

    def pop(self):
        self._navigation_view.pop()

    def set_main_item_end_buttons_visible(self, visible: bool):
        self.main_page_item.set_end_buttons_visible(visible)


@Gtk.Template(resource_path='/com/github/akamrzero/lyris/viewstack_page.ui')
class ViewStackPage(Gtk.Box):
    __gtype_name__ = 'ViewStackPage'
    toolbar_view: Adw.ToolbarView = Gtk.Template.Child()

    def __init__(self, content: Gtk.Widget = None):
        super().__init__()
        if content:
            self.set_content(content)

    def set_content(self, content: Gtk.Widget):
        self.toolbar_view.set_content(content)

    def get_content(self):
        return self.toolbar_view.get_content()

