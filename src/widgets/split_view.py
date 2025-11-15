import gi

from .paintables.blur_paintable import BlurPaintable
from ..audioplayer import AudioPlayer
from ..queue import Queue
from ..utils.db_manager import DBM
from ..utils.get_cached_cover import get_medium_pixbuf_cover

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GObject, Gdk, Gsk, GdkPixbuf, Graphene
from ..utils.pygobject_helpers import *

from .app_state import app_state

class MyLeaflet(Gtk.Widget):
    __gtype_name__ = 'MyLeaflet'

    collapsed = GObject.Property(type=bool, default=False)
    hide_library = GObject.Property(type=bool, default=False)

    def __init__(self, sidebar: Gtk.Widget, player: Gtk.Widget, sidebar_width: int = 300, collapse_width: int = 548):
        super().__init__()
        self.collapse_width = collapse_width
        self.sidebar: Gtk.Widget = sidebar
        self.player: Gtk.Widget = player
        self.sidebar_width: int = sidebar_width

        self.children = []

        self.blur_paintable = None

        self.bind_property('collapsed', app_state, 'collapsed', GObject.BindingFlags.BIDIRECTIONAL)
        self.bind_property('hide-library', app_state, 'hide-library', GObject.BindingFlags.BIDIRECTIONAL)

        app_state.connect('notify::background-blur', lambda *_: self.queue_draw())

        self.connect('notify::hide-library', lambda *_: self.update_hide_library())


        self.update_bg_cover()
        self.update_hide_library()

        Queue().connect('song-changed', lambda *_: self.update_bg_cover())

        self.add_child(self.sidebar)
        self.add_child(self.player)

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
            player_min, player_nat = self.player.measure(Gtk.Orientation.HORIZONTAL, -1)
            min_width = self.sidebar_width + player_min
            nat_width = self.sidebar_width + player_nat
            return min_width, nat_width

        else:  # VERTICAL: for_size is the width GTK wants heights for
            # If for_size is unconstrained (-1) we query children unconstrained.
            if for_size <= 0:
                sidebar_min_h, sidebar_nat_h = self.sidebar.measure(Gtk.Orientation.VERTICAL, -1)
                player_min_h, player_nat_h = self.player.measure(Gtk.Orientation.VERTICAL, -1)
            else:
                # split the available width between sidebar and player
                sidebar_for = min(self.sidebar_width, for_size)
                player_for = max(0, for_size - self.sidebar_width)

                sidebar_min_h, sidebar_nat_h = self.sidebar.measure(Gtk.Orientation.VERTICAL, sidebar_for)
                player_min_h, player_nat_h = self.player.measure(Gtk.Orientation.VERTICAL, player_for)

            min_height = max(sidebar_min_h, player_min_h)
            nat_height = max(sidebar_nat_h, player_nat_h)
            return min_height, nat_height

    # Allocate children (positioning)
    def do_size_allocate(self, width, height, baseline):
        if not self.children:
            return

        sidebar_width = self.sidebar_width
        player_width = max(0, width - sidebar_width)

        if width <= self.collapse_width:
            app_state.set_collapsed(True)

        else:
            app_state.set_collapsed(False)

        zero = gdk_rectangle(0, 0, 0, 0)

        if self.collapsed:
            if self.sidebar:
                self.sidebar.set_visible(True)
                sidebar_alloc = gdk_rectangle(0, 0, width, height)
                self.sidebar.size_allocate(sidebar_alloc, baseline)
            if self.player:
                self.player.set_visible(False)
                self.player.size_allocate(zero, -1)

        elif self.hide_library:
            if self.sidebar:
                self.sidebar.set_visible(False)
                self.sidebar.size_allocate(zero, -1)
            if self.player:
                self.player.set_visible(True)
                player_alloc = gdk_rectangle(0, 0, width, height)
                self.player.size_allocate(player_alloc, baseline)

        else:
            if self.sidebar:
                self.sidebar.set_visible(True)
                sidebar_alloc = gdk_rectangle(0, 0, sidebar_width, height)
                self.sidebar.size_allocate(sidebar_alloc, baseline)

            if self.player:
                self.player.set_visible(True)
                player_alloc = gdk_rectangle(sidebar_width, 0, player_width, height)
                self.player.size_allocate(player_alloc, baseline)



    def do_snapshot(self, snapshot):

        w = self.get_width()
        h = self.get_height()
        if w <= 0 or h <= 0:
            return

        if app_state.background_blur:
            if self.blur_paintable:
                self.blur_paintable.snapshot(snapshot, w, h)

        if not self.collapsed and not self.hide_library:
            rect = Graphene.Rect().init(self.sidebar_width, 0, 0.5, h)
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



        if self.children:
            if w <= self.collapse_width:
                self.snapshot_child(self.sidebar, snapshot)
            else:
                for child in self.children:
                    self.snapshot_child(child, snapshot)

    def update_bg_cover(self):
        if Queue().get_current_song_id():
            cover = get_medium_pixbuf_cover(DBM.song.get_for_id(Queue().get_current_song_id()).medium_cover_file)
            if cover:
                texture = Gdk.Texture.new_for_pixbuf(cover)
                self.blur_paintable = BlurPaintable(texture, blur_radius=102, opacity=0.25)

    # def get_blur_mode(self):
    #     gsettings = Gio.Settings.new('com.github.akamrzero.lyris')
    #     blur_mode = gsettings.get_boolean('background-blur')
    #     return blur_mode

    def update_hide_library(self):
        if self.hide_library != app_state.hide_library:
            self.hide_library = app_state.hide_library
        self.queue_allocate()

