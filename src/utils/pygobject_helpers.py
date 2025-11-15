# This file contains simplified wrapper functions for PyGObject nodes.
# It provides more readable Pythonic APIs for some tasks

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject, Gsk, Graphene


def gdk_rectangle(x: int, y: int, width: int, height: int) -> Gdk.Rectangle :
    rectangle = Gdk.Rectangle()
    rectangle.x = x
    rectangle.y = y
    rectangle.width = width
    rectangle.height = height
    return rectangle

def gsk_color_stop(offset: float, color: Gdk.RGBA) -> Gsk.ColorStop:
    color_stop = Gsk.ColorStop()
    color_stop.offset = offset
    color_stop.color = color
    return color_stop
