# audioplayer.py
#
# Copyright (C) 2025 akamrzero
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import math

import gi
import re


from .queue import Queue
from .utils.event_bus import GEB

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib
from .utils.db_manager import DBM

Gst.init(None)


class AudioPlayer(GObject.GObject):
    __gsignals__ = {
        'playback-state-changed': (GObject.SIGNAL_RUN_FIRST, None, ()),
        # 'spectrum-data-updated': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        'playback-progress': (GObject.SIGNAL_RUN_FIRST, None, (float,))
    }

    volume = GObject.Property(type=GObject.TYPE_FLOAT, default=1.0)

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self):
        super().__init__()
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        Queue().connect('song-changed', self.on_song_changed)

        self.spectrum = Gst.ElementFactory.make('spectrum', 'spectrum')
        self.spectrum.set_property('bands', 512)
        self.spectrum.set_property('threshold', -60)
        self.spectrum.set_property('post-messages', True)

        self.pipeline = Gst.ElementFactory.make('playbin', 'player')
        self.bind_property('volume', self.pipeline, 'volume', GObject.BindingFlags.BIDIRECTIONAL)

        # IMPORTANT: insert spectrum into the audio chain using audio-filter
        self.pipeline.set_property('audio-filter', self.spectrum)

        self._setup_bus()
        GLib.timeout_add(100, self._on_position_changed)  # 10x a second

        self.connect_global_signals()


    def _setup_bus(self):
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_bus_message)

    def _on_bus_message(self, bus, msg):
        t = msg.type
        if t == Gst.MessageType.ERROR:
            err, dbg = msg.parse_error()
            print(f'\nGstError: {err} {dbg}')
            self.playback_state = Gst.State.NULL
        elif t == Gst.MessageType.EOS:
            Queue().next_song()
        elif t == Gst.MessageType.ELEMENT:
            struct = msg.get_structure()
            src_is_spectrum = (msg.src == self.spectrum)
            struct_is_spectrum = (struct is not None and struct.get_name() == 'spectrum')
            if src_is_spectrum or struct_is_spectrum:
                self._handle_spectrum_message(msg)

    def _handle_spectrum_message(self, msg):
        struct = msg.get_structure()
        if not struct:
            return

        try:
            raw = struct.get_value('magnitude')
            mags = [float(x) for x in raw]
        except Exception:
            mags = None

        # 2) If that failed (TypeError: unknown type GstValueList), parse the structure string
        if mags is None:
            s = struct.to_string()
            # locate the 'magnitude' section and extract floats from the following chunk
            idx = s.find('magnitude')
            if idx != -1:
                # take a reasonable slice after 'magnitude' to capture the array text
                snippet = s[idx: idx + 2000]
                # regex that matches floats and scientific notation
                nums = re.findall(r'[-+]?\d*\.\d+(?:[eE][-+]?\d+)?|[-+]?\d+(?:[eE][-+]?\d+)?', snippet)
                if nums:
                    try:
                        mags = [float(x) for x in nums]
                    except Exception:
                        mags = None

        if not mags:
            print('\n[spectrum] could not parse magnitude values. structure repr:')
            print(struct.to_string())
            return

        # Emit for GUI consumers
        GEB.emit_spectrum_data_updated(mags)
        # self.emit('spectrum-data-updated', mags)

    def _wait_for_state(self):
        self.pipeline.get_state(Gst.CLOCK_TIME_NONE)

    def set_source(self, filepath):
        uri = GLib.filename_to_uri(filepath, None)
        print(f"\nSetting source to: {filepath}")

        self.pipeline.set_state(Gst.State.READY)
        self._wait_for_state()

        self.pipeline.set_property('uri', uri)
        self.playback_state = Gst.State.PLAYING

    @property
    def playback_state(self):
        _, state, pending = self.pipeline.get_state(timeout=Gst.CLOCK_TIME_NONE)
        return state

    @playback_state.setter
    def playback_state(self, state):
        self.pipeline.set_state(state)


    def on_song_changed(self, queue_instance, song, start_playing):
        song = DBM.song.get_for_id(song)
        if song and song.file_path:
            self.set_source(song.file_path)
        if not start_playing:
            self.pipeline.set_state(Gst.State.PAUSED)

    def _on_position_changed(self):
        success, pos = self.pipeline.query_position(Gst.Format.TIME)
        if success:
            mseconds = pos // Gst.MSECOND
            GEB.emit_playback_progress(mseconds)
        return True

    def on_position_seeked(self, _, position):
        self.pipeline.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, position*1000000)

    # global signals
    def on_toggle_playback_request(self, bus):
        self.toggle_playback()

    def toggle_playback(self):
        print('toggle_playback')
        if self.playback_state == Gst.State.PLAYING:
            self.playback_state = Gst.State.PAUSED
        else:
            self.playback_state = Gst.State.PLAYING

        self.emit('playback-state-changed')

    def get_state(self):
        return self.playback_state


    def connect_global_signals(self):
        GEB.connect_toggle_playback_request(self.on_toggle_playback_request)
        GEB.connect_playback_position_seeked(self.on_position_seeked)

    def set_volume(self, volume: float):
        self.pipeline.set_property('volume', volume)

    def get_volume(self) -> float:
        volume = self.pipeline.get_property('volume')
        return volume
