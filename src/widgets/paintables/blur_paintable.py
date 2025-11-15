import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject

from src.widgets.entitys.entity_paintable import BasePaintable


class BlurPaintable(BasePaintable):
    def __init__(self, paintable: Gdk.Paintable, blur_radius: float = 80.0, opacity: float = 0.25):
        super().__init__(paintable)
        self.blur_radius = blur_radius
        self.opacity = opacity

    def snapshot(self, snapshot: Gtk.Snapshot, width: int, height: int):
        if not self._paintable or width <= 0 or height <= 0:
            return

        # Effekte direkt auf den übergebenen Snapshot anwenden
        snapshot.push_opacity(self.opacity)
        snapshot.push_blur(self.blur_radius)

        # Paintable direkt rendern
        self._paintable.snapshot(snapshot, width, height)

        # Effekte wieder entfernen
        snapshot.pop()  # Blur
        snapshot.pop()