from gi.repository import Gio, GLib

class GSettings:
    def __init__(self):
        self._settings = Gio.Settings.new('com.github.akamrzero.Lyris')

    # window-height
    @property
    def window_height(self) -> int:
        return self._settings.get_int('window-height')

    @window_height.setter
    def window_height(self, value: int):
        self._settings.set_int('window-height', value)

    # window-width
    @property
    def window_width(self) -> int:
        return self._settings.get_int('window-width')

    @window_width.setter
    def window_width(self, value: int):
        self._settings.set_int('window-width', value)

    # last-opened-page
    @property
    def last_opened_page(self) -> str:
        return self._settings.get_string('last-opened-page')

    @last_opened_page.setter
    def last_opened_page(self, value: str):
        self._settings.set_string('last-opened-page', value)

    # hide-library
    @property
    def hide_library(self) -> bool:
        return self._settings.get_boolean('hide-library')

    @hide_library.setter
    def hide_library(self, value: bool):
        self._settings.set_boolean('hide-library', value)

    # queue-last-index
    @property
    def queue_last_index(self) -> int:
        return self._settings.get_int('queue-last-index')

    @queue_last_index.setter
    def queue_last_index(self, value: int):
        self._settings.set_int('queue-last-index', value)

    # queue-last-songs
    @property
    def queue_last_songs(self) -> list[str]:
        return self._settings.get_strv('queue-last-songs')

    @queue_last_songs.setter
    def queue_last_songs(self, value: list[str]):
        self._settings.set_strv('queue-last-songs', value)

    # queue-last-play-order
    @property
    def queue_last_play_order(self) -> list[int]:
        return self._settings.get_value('queue-last-play-order').unpack()

    @queue_last_play_order.setter
    def queue_last_play_order(self, value: list[int]):
        self._settings.set_value('queue-last-play-order', GLib.Variant('ai', value))

    # queue-shuffle
    @property
    def queue_shuffle(self) -> bool:
        return self._settings.get_boolean('queue-shuffle')

    @queue_shuffle.setter
    def queue_shuffle(self, value: bool):
        self._settings.set_boolean('queue-shuffle', value)

    # queue-loop
    @property
    def queue_loop(self) -> bool:
        return self._settings.get_boolean('queue-loop')

    @queue_loop.setter
    def queue_loop(self, value: bool):
        self._settings.set_boolean('queue-loop', value)

    # background-blur
    @property
    def background_blur(self) -> bool:
        return self._settings.get_boolean('background-blur')

    @background_blur.setter
    def background_blur(self, value: bool):
        self._settings.set_boolean('background-blur', value)


gsettings = GSettings()
