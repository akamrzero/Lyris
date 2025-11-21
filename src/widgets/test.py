import sys
import gi
import enum
from mesonbuild.rewriter import MTypeStr

from src.utils.pygobject_helpers import gsk_color_stop, gdk_rectangle

# Wir benötigen Gtk 4.0 und Adw 1
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GObject, Graphene, Gsk, Gdk

class CustomSplitviewState(enum.Enum):
    DEFAULT = 'default'
    HIDE_SIDEBAR = 'hide_sidebar'
    HIDE_CONTENT = 'hide_content'


class CustomSplitView(Gtk.Widget):
    __gtype_name__ = 'CustomSplitView'
    state = CustomSplitviewState.DEFAULT
    split_position = GObject.Property(type=int, default=300)

    def __init__(self, sidebar: Gtk.Widget, content: Gtk.Widget, sidebar_width: int = 300, collapse_width: int = 450):
        super().__init__()
        self.collapse_width = collapse_width
        self.sidebar: Gtk.Widget = sidebar
        self.content: Gtk.Widget = content
        self.default_split_position: int = sidebar_width
        self.split_position = sidebar_width

        self.connect('notify::split-position', lambda *_: self.on_split_position_changed())

        self.children = []

        self.add_child(self.sidebar)
        self.add_child(self.content)

    def add_child(self, child):
        self.children.append(child)
        child.set_parent(self)
        self.queue_resize()

    def remove(self, child):
        if child in self.children:
            self.children.remove(child)
            child.unparent()
            self.queue_resize()

    def measure(self, orientation, for_size):
        # for_size: when VERTICAL, it's the width GTK asks about; when HORIZONTAL usually -1 (unconstrained)

        if orientation == Gtk.Orientation.HORIZONTAL:
            # Ask player for its horizontal preference (unconstrained)
            player_min, player_nat = self.content.measure(Gtk.Orientation.HORIZONTAL, -1)
            min_width = self.default_split_position + player_min
            nat_width = self.default_split_position + player_nat
            return min_width, nat_width

        else:  # VERTICAL: for_size is the width GTK wants heights for
            # If for_size is unconstrained (-1) we query children unconstrained.
            if for_size <= 0:
                sidebar_min_h, sidebar_nat_h = self.sidebar.measure(Gtk.Orientation.VERTICAL, -1)
                player_min_h, player_nat_h = self.content.measure(Gtk.Orientation.VERTICAL, -1)
            else:
                # split the available width between sidebar and content
                sidebar_for = min(self.default_split_position, for_size)
                player_for = max(0, for_size - self.default_split_position)

                sidebar_min_h, sidebar_nat_h = self.sidebar.measure(Gtk.Orientation.VERTICAL, sidebar_for)
                player_min_h, player_nat_h = self.content.measure(Gtk.Orientation.VERTICAL, player_for)

            min_height = max(sidebar_min_h, player_min_h)
            nat_height = max(sidebar_nat_h, player_nat_h)
            return min_height, nat_height

    # Allocate children (positioning)
    def do_size_allocate(self, width, height, baseline):
        if width < self.collapse_width:
            if self.state == CustomSplitviewState.DEFAULT:
                self.change_state(CustomSplitviewState.HIDE_CONTENT)
        else:
            if self.state == CustomSplitviewState.HIDE_CONTENT:
                self.change_state(CustomSplitviewState.DEFAULT)

        if not self.children:
            return

        sidebar_x = self.split_position - self.default_split_position
        if sidebar_x > 0:
            sidebar_x = 0
        sidebar_width = max(self.split_position, self.default_split_position)
        if sidebar_width > width:
            sidebar_width = width
        content_x = self.split_position
        content_width = max(width - sidebar_width - sidebar_x, width - self.default_split_position)

        sidebar_alloc = gdk_rectangle(
            x = sidebar_x,
            y = 0,
            width = sidebar_width,
            height = height
        )
        content_alloc = gdk_rectangle(
            x = content_x,
            y = 0,
            width = content_width,
            height = height
        )

        self.sidebar.size_allocate(sidebar_alloc, baseline)
        self.content.size_allocate(content_alloc, baseline)

    def do_snapshot(self, snapshot):

        w = self.get_width()
        h = self.get_height()
        if w <= 0 or h <= 0:
            return

        if self.state == CustomSplitviewState.DEFAULT:
            rect = Graphene.Rect().init(self.default_split_position, 0, 0.5, h)
            rect.normalize()
            colors_2 = [
                gsk_color_stop(0.0, Gdk.RGBA(1, 1, 1, 0.0)),
                gsk_color_stop(0.5, Gdk.RGBA(1.0, 1.0, 1.0, 0.4)),
                gsk_color_stop(1.0, Gdk.RGBA(1, 1, 1, 0.0)),

            ]
            grad_node_2 = Gsk.LinearGradientNode.new(
                rect,
                rect.get_top_left(),
                rect.get_bottom_right(),
                colors_2
            )
            snapshot.append_node(grad_node_2)


        if self.sidebar:
            sidebar_alloc = self.sidebar.get_allocation()
            render_sidebar = True if sidebar_alloc.x + sidebar_alloc.width > 0 else False
            if render_sidebar:
                self.snapshot_child(self.sidebar, snapshot)
        if self.content:
            content_alloc = self.content.get_allocation()
            render_content = True if content_alloc.x < w else False
            if render_content:
                self.snapshot_child(self.content, snapshot)

    def change_state(self, state: CustomSplitviewState):
        if state == CustomSplitviewState.HIDE_SIDEBAR:
            self.animate_split_position(0)
        elif state == CustomSplitviewState.HIDE_CONTENT:
            self.animate_split_position(self.get_width())
        else: # default state
            self.animate_split_position(self.default_split_position)
        self.state = state
        self.queue_allocate()

    def toggle_hide_sidebar(self):
        if self.state == CustomSplitviewState.DEFAULT:
            self.change_state(CustomSplitviewState.HIDE_SIDEBAR)
        elif self.state == CustomSplitviewState.HIDE_SIDEBAR:
            self.change_state(CustomSplitviewState.DEFAULT)

    def animate_split_position(self, end):
        start = self.split_position
        target = Adw.PropertyAnimationTarget.new(self, 'split-position')
        animation = Adw.TimedAnimation.new(self, start, end, 250, target)
        animation.play()

    def on_split_position_changed(self):
        self.queue_allocate()



class ExampleWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Adw NavigationSplitView Demo")

        # Fenstergröße setzen, damit man den Split-Effekt direkt sieht
        self.set_default_size(900, 600)

        status_page_1 = Adw.StatusPage(
            title='Sidebar',
            description='Click the button to do something.',
            icon_name='folder-symbolic',
        )
        status_page_2 = Adw.StatusPage(
            title='Content',
            description='Click the button to do something.',
            icon_name='folder-symbolic',
        )

        # Button
        button_2 = Gtk.Button(label='Do something else')
        # button.connect('clicked', self.on_button_clicked)

        # --- Hauptkomponente: AdwNavigationSplitView ---
        self.split_view = CustomSplitView(
            status_page_1,
            status_page_2,
        )
        status_page_2.set_child(button_2)
        button_2.connect('clicked', lambda *_: self.split_view.toggle_hide_sidebar())

        self.set_content(self.split_view)


class MyApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.SplitViewDemo",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        # Fix für die Warnung "gtk-application-prefer-dark-theme"
        # Wir nutzen den StyleManager von Libadwaita
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)

        win = self.props.active_window
        if not win:
            win = ExampleWindow(self)
        win.present()


if __name__ == "__main__":
    app = MyApp()
    sys.exit(app.run(sys.argv))