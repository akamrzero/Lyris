import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GObject
from ..utils.event_bus import GEB

class SeekBar(Gtk.Scale):
    def __init__(self):

        self._seeking = False
        self._adjustment = Gtk.Adjustment(
            value=0,
            lower=0,
            upper=1,
            step_increment=0,
            page_increment=0,
            page_size=0
        )
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self._adjustment)

        self.create_click_gesture()

        GEB.connect_playback_progress(self._on_playback_progress)



    @property
    def duration(self):
        return self._adjustment.get_upper()

    @duration.setter
    def duration(self, value):
        self._adjustment.set_upper(value)

    @property
    def value(self):
        return self._adjustment.get_value()

    @value.setter
    def value(self, value):
        if not self._seeking:
            self._adjustment.set_value(value)

    def _on_pressed(self, gesture, n_press, x, y):
        self._seeking = True

    def _on_released(self, gesture, n_press, x=0, y=0):
        self._seeking = False
        # self.emit('position-seeked', (self._adjustment.get_value()))
        GEB.emit_playback_position_seeked(self._adjustment.get_value())

    def _on_playback_progress(self, _, progress):
        self.value = progress

    def create_click_gesture(self):
        click_gesture = None
        controllers = self.observe_controllers()
        for i in range(controllers.get_n_items()):
            controller = controllers.get_item(i)
            if isinstance(controller, Gtk.GestureClick):
                click_gesture = controller
                break

        click_gesture.set_button(0)  # listen for any button

        click_gesture.connect("pressed", self._on_pressed)
        click_gesture.connect("released", self._on_released)



