import gi
import cairo
import math
import re
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Adw

from ..utils.process_specrum_data import process_spectrum_data


class lyrisVisualizer(Gtk.DrawingArea):
    def __init__(
            self,
            inner_radius: int,
            outer_radius: int,
            bars_color: tuple[float, float, float, float],
            smoothing: float,
    ):
        super().__init__()
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.bars_color = bars_color
        self.smoothing = smoothing

        self.display_amplitudes = [ 0.0 for i in range(64) ]
        self.prev_amplitudes = [ 0.0 for i in range(64) ]

        self.set_draw_func(self.on_draw)


        self.set_size_request(self.outer_radius*2, self.outer_radius*2)
        # self.set_hexpand(False)
        # self.set_vexpand(False)
        # self.set_halign(Gtk.Align.CENTER)
        # self.set_valign(Gtk.Align.CENTER)

    def on_draw(self, area, cr: cairo.Context, width, height):
        cx, cy = width / 2, height / 2
        max_line_length = self. outer_radius - self.inner_radius

        smoothing = 0.1

        # smooth amplitudes
        smoothed_amplitudes = []
        for prev, curr in zip(self.prev_amplitudes, self.display_amplitudes):
            smoothed = prev * (1 - smoothing) + curr * smoothing
            smoothed_amplitudes.append(smoothed)


        num_lines = len(smoothed_amplitudes)
        for i, amp in enumerate(smoothed_amplitudes):
            angle = (2 * math.pi / num_lines) * i
            x_start = cx + math.cos(angle) * self.inner_radius
            y_start = cy + math.sin(angle) * self.inner_radius
            x_end = cx + math.cos(angle) * (self.inner_radius + amp * max_line_length)
            y_end = cy + math.sin(angle) * (self.inner_radius + amp * max_line_length)
            cr.set_source_rgba(*self.bars_color)
            cr.set_line_width(8)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.move_to(x_start, y_start)
            cr.line_to(x_end, y_end)
            cr.stroke()

    def update(self, data):
        self.display_amplitudes, self.prev_amplitudes = process_spectrum_data(data, 32)
        self.display_amplitudes += self.display_amplitudes[::-1]
        self.prev_amplitudes += self.prev_amplitudes[::-1]
        self.queue_draw()
