import gi
import cairo
import math
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, Gdk, GObject, GLib

class PlayingEqIcon(Gtk.DrawingArea):
    def __init__(
            self,
            width: int,
            height: int,
            bar_num: int,
            bar_width: int,
            bar_color: tuple[float, float, float],
            bar_height_frac: float = 0.7,
            active: bool = True,
            anim_speed: float = 0.05,
            wander_speed: float = 0.015
    ):
        super().__init__()
        self.set_content_width(width)
        self.set_content_height(height)

        self.active = active
        self.bar_number = bar_num
        self.bar_width = bar_width
        self.bar_height_frac = bar_height_frac
        self.bar_color = bar_color
        self.phase = 0.0
        self.wander = 0.0
        self.anim_speed = anim_speed
        self.wander_speed = wander_speed


        self.set_draw_func(self.on_draw)
        GLib.timeout_add(16, self.tick)

    def tick(self):
        self.phase += self.anim_speed
        self.wander += self.wander_speed
        self.phase %= 2 * math.pi
        self.wander %= 2 * math.pi
        self.queue_draw()
        return True

    def on_draw(self, area, cr, w, h):
        cr.set_source_rgb(*self.bar_color)
        cr.set_line_width(self.bar_width)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)

        if self.active:
            for i in range(self.bar_number):
                slow_shift = 0.6 * math.sin(self.wander + i * 0.4)
                slow_amp = 0.85 + 0.15 * math.sin(self.wander * 0.5 + 1.1 + i * 0.3)
                v = (math.sin(self.phase * (i+1) + i*0.9 + slow_shift) * slow_amp + 1) * 0.5
                eased = v * v * (3 - 2 * v)
                eased = max(0.0, min(eased, 1.0))

                bar_height = h * eased * self.bar_height_frac
                x = (i + 0.5) * (w / self.bar_number)

                cr.move_to(x, h/2 + bar_height/2)
                cr.line_to(x, h/2 - bar_height/2)
                cr.stroke()
        else:
            for i in range(self.bar_number):
                x = (i + 0.5) * (w / self.bar_number)
                cr.move_to(x, h / 2)
                cr.line_to(x, h / 2)
                cr.stroke()



if __name__ == '__main__':
    class App(Gtk.Application):
        def __init__(self):
            super().__init__()

        def do_activate(self):
            win = Gtk.ApplicationWindow()
            win.set_application(self)
            area = PlayingEqIcon(
                width=20,
                height=20,
                bar_num=3,
                bar_width=6,
                bar_color=(1.0, 1.0, 1.0),
            )

            area.set_halign(Gtk.Align.CENTER)
            area.set_valign(Gtk.Align.CENTER)
            win.set_child(area)
            win.set_size_request(400, 400)
            win.present()

    app = App()
    app.run([])

