import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject


class Window(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__()
        self.set_application(app)

        self.viewstack = Gtk.Stack()
        self.viewswitcher = Gtk.StackSwitcher()
        self.viewswitcher.set_stack(self.viewstack)
        self.viewstack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        home_page = self.viewstack.add_named(Gtk.Label(label='Home'), 'home')
        home_page.set_title('Home')
        about_page = self.viewstack.add_named(Gtk.Label(label='About'), 'about')
        about_page.set_title('About')
        about_page = self.viewstack.add_named(Gtk.Label(label='Mehr'), 'more')
        about_page.set_title('Mehr')
        about_page = self.viewstack.add_named(Gtk.Label(label='x'), 'x')
        about_page.set_title('x')

        # Switcher erstellen


        # HeaderBar
        header = Adw.HeaderBar()
        header.set_title_widget(self.viewswitcher)

        # ToolbarView
        toolbarview = Adw.ToolbarView()
        toolbarview.add_top_bar(header)
        toolbarview.set_content(self.viewstack)

        # Fensterinhalt setzen
        self.set_content(toolbarview)




class App(Adw.Application):
    def __init__(self):
        super().__init__()

    def do_activate(self):
        win = Window(self)
        win.present()

if __name__ == '__main__':
    app = App()
    app.run([''])