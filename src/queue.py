# queue.py
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


import random

from gi.repository import GObject, Gio, GLib

from .models.playlist import Playlist
from .utils.event_bus import GEB
from .utils.db_manager import DBM


class Queue(GObject.GObject):
    __gsignals__ = {
        'song-changed': (GObject.SIGNAL_RUN_FIRST, None, (str, bool)),
        'shuffle-toggled': (GObject.SIGNAL_RUN_FIRST, None, (bool,)),
        'loop-toggled': (GObject.SIGNAL_RUN_FIRST, None, (bool,)),
    }

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

        self._gsettings = Gio.Settings.new('com.github.akamrzero.lyris')
        if self._gsettings.get_strv('queue-last-songs'):
            self._songs = self._gsettings.get_strv('queue-last-songs')
            for song in self._songs:
                if not DBM.song.get_for_id(song):
                    self._songs.remove(song)
        else:
            self._songs= []

        if self._gsettings.get_int('queue-last-index'):
            index = self._gsettings.get_int('queue-last-index')
            if len(self._songs) > index:
                self._current_index = index
        else:
            self._current_index: int = 0

        if self._gsettings.get_value('queue-last-play-order'):
            play_order = self._gsettings.get_value('queue-last-play-order').unpack()
            if len(play_order) == len(self._songs):
                self._play_order = play_order
            else:
                self._play_order = []
        else:
            self._play_order = []

        if self._gsettings.get_boolean('queue-shuffle'):
            self._shuffle_playback: bool = self._gsettings.get_boolean('queue-shuffle-playback')
        else:
            self._shuffle_playback: bool = False

        if self._gsettings.get_boolean('queue-loop'):
            self._loop_current: bool = self._gsettings.get_boolean('queue-loop-current')
        else:
            self._loop_current: bool = False

        self._set_play_order()

        self.connect_global_signals()

        if self._play_order:
            GLib.idle_add(lambda: self._emit_track_changed_signal(start_playback=False))

    def add_song_id(self, song_id: str, play_next: bool = False, play_instantly: bool = False, emit_signal: bool = True, update_gsettings: bool = True):
        """
        Add a song to the queue by its ID.

        Args:
            song_id (str): The ID of the song to add.
            play_next (bool): If True, the song will be inserted right after the current song.
            play_instantly (bool): If True, the song will start playing immediately.
                                   If both play_next and play_instantly are True, play_instantly takes precedence.
            emit_signal (bool): If True, the song_changed signal will be emitted. This ist only ment to set to False in when used in the add_song_batch method.
            update_gsettings (bool): If True, the gsettings object will be updated with the new song's ID. This ist only ment to set to False in when used in the add_song_batch method.

        Raises:
            ValueError: If the provided song_id does not exist in the database.
        """
        song_id = str(song_id)

        if DBM.song.get_for_id(song_id) is None:
            raise ValueError(f"Song id {song_id} doesn't exist")

        if play_next or play_instantly:
            self._songs.insert(self._current_index + 1, song_id)
            if play_instantly:
                self.next_song()
        else:
            self._songs.append(song_id)

        if emit_signal:
            self._emit_track_changed_signal()

        self._set_play_order(update_gsettings)

        if update_gsettings:
            self._gsettings.set_strv('queue-last-songs', self._songs)
            self._gsettings.set_int('queue-last-index', self._current_index)


    def add_song_batch(self, songs: list, replace_upcoming: bool=True, play_id: str=None):
        """
        Add a batch of songs to the queue.

        Args:
            songs (list): A list of songs IDs to add.
            replace_upcoming (bool): If True, the upcoming queue will be replaced with the songs.
                                     If False, the list of songs will be appended to the queue.
            play_id (str): The ID of the song to play immediately.
                           If set to None, no song ist played.
        Raises:
            ValueError: If one of the provided song IDs does not exist.
            ValueError: If play_id is not in songs
        """


        if play_id:
            if play_id not in songs:
                raise ValueError(f"Song id {play_id} doesn't exist")

        if replace_upcoming:
            self._songs = self._songs[:self._current_index]

        for song_id in songs:
            self.add_song_id(song_id, play_instantly=(song_id == play_id), emit_signal=False, update_gsettings=False)
        print(f'Added {len(songs)} songs to queue')

        self._emit_track_changed_signal()

        self._set_play_order()

        self._gsettings.set_strv('queue-last-songs', self._songs)
        self._gsettings.set_int('queue-last-index', self._current_index)

    def remove_song_id(self, song_id: str):
        """
        Remove a song from the queue by its ID.
        Args:
            song_id (str): The ID of the song to remove.
        Raises:
            ValueError: If the provided song_id does not exist in the queue.
        """
        self._songs.remove(song_id)


        self._gsettings.set_strv('queue-last-songs', self._songs)
        self._gsettings.set_int('queue-last-index', self._current_index)

    def clear_songs(self, only_history=False, only_upcoming=True):
        """
        Clear all songs from the queue.
        Args:
            only_history (bool): If True, only the history of the songs will be cleared.
            only_upcoming (bool): If True, only the upcoming songs will be cleared.
        """
        if only_history:
            self._songs = self._songs[-self._current_index:]
        if only_upcoming:
            self._songs = self._songs[self._current_index:]
        else:
            self._songs = []


        self._gsettings.set_strv('queue-last-items', self._songs)
        self._gsettings.set_int('queue-last-index', self._current_index)

    def _set_play_order(self, update_gsettings: bool = True):
        """Recompute self._play_order safely and keep current song when possible.
           _play_order holds indices into self._songs.
        """
        n = len(self._songs)

        # empty songs => clear everything
        if n == 0:
            self._play_order = []
            self._current_index = 0
            if update_gsettings:
                self._gsettings.set_value('queue-last-play-order', GLib.Variant('ai', self._play_order))
            return

        # try to figure out which song (index in self._songs) is currently playing
        current_song_idx_in_songs = None
        if self._play_order and 0 <= self._current_index < len(self._play_order):
            # normal case: _current_index points inside old _play_order
            current_song_idx_in_songs = self._play_order[self._current_index]
        elif 0 <= self._current_index < n:
            # fallback: maybe _current_index was stored as index into songs (legacy)
            current_song_idx_in_songs = self._current_index
        else:
            # unknown: default to first song
            current_song_idx_in_songs = 0

        if self._shuffle_playback:
            # If we already had a play_order, preserve history (played ones) if possible
            if self._play_order and 0 <= self._current_index < len(self._play_order):
                history = [i for i in self._play_order[:self._current_index] if i < n]
                upcoming = [i for i in self._play_order[self._current_index:] if i < n]
                # any indices may be stale after song list change; rebuild missing indices:
                remaining = [i for i in range(n) if i not in history and i not in upcoming]
                random.shuffle(upcoming)
                random.shuffle(remaining)
                self._play_order = history + upcoming + remaining
            else:
                # no previous order -> full random order
                self._play_order = list(range(n))
                random.shuffle(self._play_order)

            # set current_index to where current_song_idx_in_songs sits in the new order
            try:
                self._current_index = self._play_order.index(current_song_idx_in_songs)
            except ValueError:
                # if the current song disappeared somehow, clamp to 0
                self._current_index = 0

        else:
            # non-shuffle: plain identity order
            self._play_order = list(range(n))
            # make current_index point to the play_position of current_song_idx_in_songs
            try:
                self._current_index = self._play_order.index(current_song_idx_in_songs)
            except ValueError:
                self._current_index = 0

        # sanity clamp current_index
        if self._current_index is None or self._current_index < 0:
            self._current_index = 0
        if self._current_index >= max(1, len(self._play_order)):
            self._current_index = len(self._play_order) - 1

        # persist
        if update_gsettings:
            self._gsettings.set_value('queue-last-play-order', GLib.Variant('ai', self._play_order))
            self._gsettings.set_strv('queue-last-songs', self._songs)
            self._gsettings.set_int('queue-last-index', self._current_index)

    def next_song(self):
        """
        Plays the next song in the queue if possible.
        """
        if self._loop_current:
            self._emit_track_changed_signal()
            return True

        if not self._songs:
            return False

        if self._current_index < len(self._play_order) -1:
            self._current_index += 1
            self._emit_track_changed_signal()
            self._gsettings.set_int('queue-last-index', self._current_index)
            return True
        return False


    def previous_song(self):
        """
        Plays the previous song in the queue of possible.
        """
        if self._current_index > 0 and self._songs:
            self._current_index -= 1
            self._emit_track_changed_signal()
            self._gsettings.set_int('queue-last-index', self._current_index)
            return True
        return False

    def play(self, song_id: str):
        """
        Plays a song for a given song ID in the queue.
        Args:
            song_id (str): The ID of the song to play.
        Raises:
            ValueError: If the provided song_id does not exist in the queue.
        """
        if song_id in self._songs:
            index = self._songs.index(song_id)
            song = self._songs.pop(index)
            self._songs.insert(self._current_index, song)
            self.next_song()
            self._gsettings.set_strv('queue-last-songs', self._songs)
            self._gsettings.set_int('queue-last-index', self._current_index)
        else:
            raise ValueError(f"Song id {song_id} doesn't exist")

    def _emit_track_changed_signal(self, start_playback: bool = True):
        self.emit('song-changed', self._songs[self._play_order[self._current_index]], start_playback)

    def set_shuffled(self, shuffled: bool):
        if self._shuffle_playback != shuffled:
            self._shuffle_playback = shuffled
            self.emit('shuffle-toggled', shuffled)
            self._set_play_order()



    def set_loop_current(self, loop_current: bool):
        self._loop_current = loop_current
        self.emit('loop-toggled', loop_current)

    def connect_global_signals(self):
        GEB.connect_next_song(lambda _: self.next_song())
        GEB.connect_previous_track(lambda _: self.previous_song())
        GEB.connect_queue_play(lambda _, track: self.play(track))
        GEB.connect_queue_set_shuffled(lambda _, shuffle: self.set_shuffled(shuffle))
        GEB.connect_current_track_requested(lambda _: self._on_track_requested())


    def _on_track_requested(self):
        if self._songs:
            GEB.emit_current_track_provided(self._songs[self._current_index])

    def get_current_song_id(self):
        if not self._songs:
            return None
        return self._songs[self._current_index]
