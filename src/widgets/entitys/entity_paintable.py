import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gdk, Gtk, Gsk, GLib, GObject

class BasePaintable(GObject.Object, Gdk.Paintable):
    __gsignals__ = {
        'first-draw': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'queue-draw': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, paintable: Gdk.Paintable = None):
        super().__init__()
        self._first_draw = True
        self._paintable = paintable

    @property
    def paintable(self):
        return self._paintable

    @paintable.setter
    def paintable(self, value: Gdk.Paintable):
        if self._paintable != value:
            self._paintable = value
            self._first_draw = True
            self.emit('queue-draw')

    # Paintable interface methods
    def snapshot(self, snapshot: Gtk.Snapshot, width: int, height: int):
        if self._first_draw:
            self._first_draw = False
            self.emit('first-draw')
        if self._paintable:
            self._paintable.snapshot(snapshot, width, height)

    def get_current_image(self):
        return self._paintable or self

    def get_flags(self):
        return self._paintable.get_flags() if self._paintable else 0

    def get_intrinsic_aspect_ratio(self):
        return self._paintable.get_intrinsic_aspect_ratio() if self._paintable else 1.0

    def get_intrinsic_width(self):
        return self._paintable.get_intrinsic_width() if self._paintable else 1

    def get_intrinsic_height(self):
        return self._paintable.get_intrinsic_height() if self._paintable else 1