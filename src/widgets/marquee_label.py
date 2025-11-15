import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GObject, Pango, Gdk, Graphene, Gsk


class EllipsizeMode(GObject.GEnum):
    NONE = Pango.EllipsizeMode.NONE
    START = Pango.EllipsizeMode.START
    MIDDLE = Pango.EllipsizeMode.MIDDLE
    END = Pango.EllipsizeMode.END
    MARQUEE = 4


class MarqueeLabel(Gtk.Widget):
    __gtype_name__ = 'MarqueeLabel'

    def __init__(self, text='', marquee=True):
        super().__init__()
        self._label = Gtk.Label()
        self._label.set_xalign(0)
        self._label.set_parent(self)
        self._ellipsize = EllipsizeMode.NONE
        self._label_offset = 0
        self._label_width = 0
        self._tick_handler = 0
        self._timer_id = 0
        self._tick_moving = False
        self._tick_start_time = 0
        self._pixels_per_second = 24
        self._space = 40

        self.set_text(text)
        self.set_marquee(marquee)

    def do_measure(self, orientation, for_size):
        if orientation == Gtk.Orientation.VERTICAL:
            text = self._label.get_label()
            self._label.set_label("A中")
            minimum, natural, min_baseline, nat_baseline = self._label.measure(orientation, for_size)
            self._label.set_label(text)
            return minimum, natural, min_baseline, nat_baseline
        else:
            minimum, natural, min_baseline, nat_baseline = self._label.measure(orientation, for_size)
            self._label_width = natural


            if self.get_marquee():
                minimum = 0
                natural = 0

            return minimum, natural, min_baseline, nat_baseline

    def do_size_allocate(self, width, height, baseline):
        allocation = Gdk.Rectangle()
        allocation.x = 0
        allocation.y = 0
        allocation.width = width
        allocation.height = height
        self._label.size_allocate(allocation, baseline)
        self.update_tick_delayed()

    def do_snapshot(self, snapshot):
        width = self.get_width()
        overflow = self.get_marquee() and width < self._label_width

        orig_xalign = self._label.get_xalign()

        if overflow:
            self._label.set_xalign(0.0)

            height = self.get_height()
            total_width = self._label_width + self._space

            bounds = Graphene.Rect()
            bounds.init(0, 0, width, height)
            snapshot.push_clip(bounds)

            point = Graphene.Point()
            point.init(0, 0)

            if self._label_offset < self._label_width:
                point.x = -self._label_offset
                snapshot.translate(point)
                Gtk.Widget.do_snapshot(self, snapshot)
                point.x = -point.x
                snapshot.translate(point)

            if self._label_offset >= total_width - width:
                point.x = -self._label_offset + total_width
                snapshot.translate(point)
                Gtk.Widget.do_snapshot(self, snapshot)
                point.x = -point.x
                snapshot.translate(point)

            snapshot.pop()

            self._label.set_xalign(orig_xalign)
        else:
            Gtk.Widget.do_snapshot(self, snapshot)

    def get_text(self):
        return self._label.get_label()

    def set_text(self, label):
        self._label.set_label(label)
        self.queue_resize()
        self.stop_tick()
        self.update_tick_delayed()

    def get_ellipsize(self):
        return self._ellipsize

    def set_ellipsize(self, ellipsize):
        self._ellipsize = ellipsize
        if ellipsize == EllipsizeMode.MARQUEE:
            self._label.set_ellipsize(Pango.EllipsizeMode.NONE)
        else:
            self._label.set_ellipsize(ellipsize)
        self.stop_tick()

    def get_marquee(self):
        return self._ellipsize == EllipsizeMode.MARQUEE

    def set_marquee(self, marquee):
        self.set_ellipsize(EllipsizeMode.MARQUEE if marquee else EllipsizeMode.NONE)

    def on_tick_callback(self, widget, clock, user_data):
        if self._tick_moving:
            now = clock.get_frame_time()
            elapsed = (now - self._tick_start_time) / 1000000
            self._label_offset = elapsed * self._pixels_per_second
            if self._label_offset > self._label_width + self._space:
                self.stop_tick()
                self.update_tick_delayed()
            self.queue_draw()
        return True

    def stop_tick(self):
        if self._tick_handler != 0:
            self.remove_tick_callback(self._tick_handler)
            self._tick_handler = 0
        if self._timer_id != 0:
            GObject.source_remove(self._timer_id)
            self._timer_id = 0
        self._label_offset = 0
        self._tick_moving = False

    def update_tick(self):
        need_tick = self.get_marquee() and self.get_width() < self._label_width
        if need_tick and self._tick_handler == 0 and self.get_frame_clock():
            self._tick_handler = self.add_tick_callback(self.on_tick_callback, None)
            self._tick_moving = self._tick_handler != 0
            self._tick_start_time = self.get_frame_clock().get_frame_time()
        elif not need_tick and self._tick_handler != 0:
            self.stop_tick()

    def update_tick_delayed(self):
        if self._timer_id == 0:
            self._timer_id = GObject.timeout_add(3000, self.timeout_cb)

    def timeout_cb(self):
        self._timer_id = 0
        self.update_tick()
        return False

    def set_xalign(self, xalign):
        self._label.set_xalign(xalign)

    def get_xalign(self):
        return self._label.get_xalign()


    def __del__(self):
        self._label.unparent()

    label = GObject.Property(type=str, getter=get_text, setter=set_text)
    ellipsize = GObject.Property(type=EllipsizeMode, getter=get_ellipsize, setter=set_ellipsize,
                                 default=EllipsizeMode.NONE)
    marquee = GObject.Property(type=bool, getter=get_marquee, setter=set_marquee, default=False)


GObject.type_register(MarqueeLabel)