import warnings
from gi.repository import GObject


class EventBus(GObject.GObject):
    __gtype_name__ = 'EventBus'
    __gsignals__ = {
        'current-song-provided': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        'current_track_requested': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'next-song': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'playback-position-seeked': (GObject.SIGNAL_RUN_FIRST, None, (float,)),
        'playback-progress': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        'previous-track': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'queue-play': (GObject.SIGNAL_RUN_FIRST, None, (str, object,)),
        'queue-play-collection': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        'queue-set-shuffled': (GObject.SIGNAL_RUN_FIRST, None, (bool,)),
        'spectrum-data-updated': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        'song-changed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'toggle-playback-confirm': (GObject.SIGNAL_RUN_FIRST, None, (bool,)),
        'toggle-playback-request': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'viewstack-pop-page': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'viewstack-push-page': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        'open-song-info-sheet': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        'close-song-info-sheet': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def emit(self, *args, **kwargs):
        warnings.warn('emit() should not be used directly, use wrapper methods instead',
                      stacklevel=2)
        return super().emit(*args, **kwargs)

    def _emit(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def connect(self, *args, **kwargs):
        warnings.warn('connect() should not be used directly, use wrapper methods instead',
                      stacklevel=2)
        return super().connect(*args, **kwargs)

    def _connect(self, *args, **kwargs):
        return super().connect(*args, **kwargs)


    # --- emit wrappers ---
    def emit_current_track_provided(self, track):
        self._emit('current-song-provided', track)

    def emit_current_track_requested(self):
        self._emit('current-track-requested')

    def emit_next_track(self):
        self._emit('next-song')

    def emit_playback_position_seeked(self, position: float):
        self._emit('playback-position-seeked', position)

    def emit_playback_progress(self, progress: int):
        self._emit('playback-progress', progress)

    def emit_previous_track(self):
        self._emit('previous-track')

    def emit_queue_play(self, obj: object):
        self._emit('queue-play', obj)

    def emit_queue_play_playlist(self, playlist: object):
        self._emit('queue-play-collection', playlist)

    def emit_queue_set_shuffled(self, shuffled: bool):
        self._emit('queue-set-shuffled', shuffled)

    def emit_spectrum_data_updated(self, mags):
        self._emit('spectrum-data-updated', mags)

    def emit_toggle_playback_confirm(self, is_playing: bool):
        self._emit('toggle-playback-confirm', is_playing)

    def emit_toggle_playback_request(self):
        self._emit('toggle-playback-request')

    def emit_viewstack_pop_page(self):
        self._emit('viewstack-pop-page')

    def emit_viewstack_push_page(self, page: object):
        self._emit('viewstack-push-page', page)

    def emit_open_song_info_sheet(self, track: object):
        self._emit('open-song-info-sheet', track)

    def emit_close_song_info_sheet(self):
        self._emit('close-song-info-sheet')


    # --- connect wrappers ---
    def connect_current_track_provided(self, callback, *args):
        self._connect('current-song-provided', callback, *args)

    def connect_current_track_requested(self, callback, *args):
        self._connect('current-track-requested', callback, *args)

    def connect_next_song(self, callback, *args):
        self._connect('next-song', callback, *args)

    def connect_playback_position_seeked(self, callback, *args):
        return self._connect('playback-position-seeked', callback, *args)

    def connect_playback_progress(self, callback, *args):
        return self._connect('playback-progress', callback, *args)

    def connect_previous_track(self, callback, *args):
        return self._connect('previous-track', callback, *args)

    def connect_queue_play(self, callback, *args):
        self._connect('queue-play', callback, *args)

    def connect_queue_play_playlist(self, callback, *args):
        self._connect('queue-play-collection', callback, *args)

    def connect_queue_set_shuffled(self, callback, *args):
        self._connect('queue-set-shuffled', callback, *args)

    def connect_spectrum_data_updated(self, callback, *args):
        return self._connect('spectrum-data-updated', callback, *args)

    def connect_song_changed(self, callback, *args):
        return self._connect('song-changed', callback, *args)

    def connect_toggle_playback_confirm(self, callback, *args):
        return self._connect('toggle-playback-confirm', callback, *args)

    def connect_toggle_playback_request(self, callback, *args):
        return self._connect('toggle-playback-request', callback, *args)

    def connect_viewstack_pop_page(self, callback, *args):
        return self._connect('viewstack-pop-page', callback, *args)

    def connect_viewstack_push_page(self, callback, *args):
        return self._connect('viewstack-push-page', callback, *args)

    def connect_open_song_info_sheet(self, callback, *args):
        return self._connect('open-song-info-sheet', callback, *args)

    def connect_close_song_info_sheet(self, callback, *args):
        return self._connect('close-song-info-sheet', callback, *args)

GEB = EventBus.instance()


