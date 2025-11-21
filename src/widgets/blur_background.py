import gi
import time

from src.queue import Queue
from src.utils.db_manager import DBM
from src.utils.get_cached_cover import get_cached_cover, CoverSize
from src.utils.pygobject_helpers import gdk_rectangle
from src.widgets.paintables.blur_paintable import BlurPaintable

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject
from src.widgets.app_state import app_state

class BlurBackground(Gtk.Widget):
    def __init__(self, widget: Gtk.Widget):
        super().__init__()
        self.widget = widget
        self.widget.set_parent(self)

        self.blur_paintable = None

        self._old_width = None
        self._old_height = None
        self._old_blur_paintable = None
        self._current_song_id = None


        if app_state:
            app_state.connect('notify::background-blur', lambda *_: self.queue_draw())

        self.update_bg_cover_if_needed()


    def do_size_allocate(self, width, height, baseline):
        allocation = gdk_rectangle(
            0, 0, width, height,
        )
        self.widget.size_allocate(allocation, baseline)

    def do_snapshot(self, snapshot):
        w = self.get_width()
        h = self.get_height()


        if w <= 0 or h <= 0:
            return

        try:
            self.update_bg_cover_if_needed()
        except IndexError as e:
            print(e)

        if app_state.background_blur:
            if self.blur_paintable:
                self.blur_paintable.snapshot(snapshot, w, h)

        self.snapshot_child(self.widget, snapshot)

        self._old_width, self._old_height = w, h
        self._old_blur_paintable = self.blur_paintable




    def update_bg_cover_if_needed(self):
        current_song_id = Queue().get_current_song_id()

        if not current_song_id:
            return

        if self._current_song_id == current_song_id:
            return

        song = DBM.song.get_for_id(current_song_id)
        if not song:
            return

        cover = get_cached_cover(song.cover_base_filename, CoverSize.small)
        if not cover:
            return
        texture = Gdk.Texture.new_for_pixbuf(cover)
        self.blur_paintable = BlurPaintable(texture, blur_radius=100, opacity=0.25)
        self._current_song_id = current_song_id

