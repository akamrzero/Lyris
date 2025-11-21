import gi

from .paintables.blur_paintable import BlurPaintable
from ..queue import Queue
from ..utils.db_manager import DBM
from ..utils.get_cached_cover import get_cached_cover, CoverSize
from ..utils.pygobject_helpers import gdk_rectangle, gsk_color_stop

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GObject, Gdk, Gsk, GdkPixbuf, Graphene, Adw

from .app_state import app_state

class SplitViewState:
    DEFAULT = 'default'
    HIDE_SIDEBAR = 'hide_sidebar'
    HIDE_CONTENT = 'hide_content'


class LyrisSplitView(Gtk.Widget):
    __gtype_name__ = 'LyrisSplitView'
    state = GObject.Property(type=str, default=SplitViewState.DEFAULT)
    split_position = GObject.Property(type=int, default=300)

    def __init__(self, sidebar: Gtk.Widget, content: Gtk.Widget, sidebar_width: int = 300, collapse_width: int = 450):
        super().__init__()
        self.collapse_width = collapse_width
        self.sidebar: Gtk.Widget = sidebar
        self.content: Gtk.Widget = content
        self.default_split_position: int = sidebar_width
        self.split_position = sidebar_width
        self.transitioning = False

        self.connect('notify::split-position', lambda *_: self.on_split_position_changed())

        if app_state:
            app_state.connect('notify::hide-library', lambda *_: self.on_appstate_hide_library_changed())


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
            if self.state == SplitViewState.DEFAULT:
                self.change_state(SplitViewState.HIDE_CONTENT)
        else:
            if self.state == SplitViewState.HIDE_CONTENT:
                self.change_state(SplitViewState.DEFAULT)

        if not self.children:
            return

        if self.state == SplitViewState.HIDE_CONTENT and not self.transitioning:
            self.split_position = width

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

        if self.state == SplitViewState.DEFAULT:
            rect = Graphene.Rect().init(self.split_position, 0, 0.5, h)
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

    def change_state(self, state: str):
        if state == SplitViewState.HIDE_SIDEBAR:
            self.animate_split_position(0)
            if app_state:
                app_state.set_collapsed(False)
                app_state.set_hide_library(True)
        elif state == SplitViewState.HIDE_CONTENT:
            self.animate_split_position(self.get_width())
            if app_state:
                app_state.set_collapsed(True)
                app_state.set_hide_library(False)
        else: # default state
            self.animate_split_position(self.default_split_position)
            if app_state:
                app_state.set_collapsed(False)
                app_state.set_hide_library(False)
        self.state = state
        self.queue_allocate()

    def toggle_hide_sidebar(self):
        if self.state == SplitViewState.DEFAULT:
            self.change_state(SplitViewState.HIDE_SIDEBAR)
        elif self.state == SplitViewState.HIDE_SIDEBAR:
            self.change_state(SplitViewState.DEFAULT)

    def animate_split_position(self, end):
        def on_finished():
            self.transitioning = False
        self.transitioning = True
        start = self.split_position
        target = Adw.PropertyAnimationTarget.new(self, 'split-position')
        animation = Adw.TimedAnimation.new(self, start, end, 250, target)
        animation.play()
        animation.connect('done', lambda *_: on_finished())

    def on_split_position_changed(self):
        self.queue_allocate()

    def on_appstate_hide_library_changed(self):
        if not self.transitioning:
            if app_state.hide_library:
                self.change_state(SplitViewState.HIDE_SIDEBAR)
            else:
                self.change_state(SplitViewState.DEFAULT)

