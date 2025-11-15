from operator import length_hint

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstPbutils', '1.0')
from gi.repository import Gst, GstPbutils, GdkPixbuf, Gio, GLib

Gst.init(None)

def get_song_title(path):
    try:
        discoverer = GstPbutils.Discoverer.new(Gst.SECOND)
        uri = Gst.filename_to_uri(path)
        info = discoverer.discover_uri(uri)
        tags = info.get_tags()
        if tags:
            title = tags.get_string('title')[1]
            return title
    except Exception as e:
        print(e)
    return None

def get_artist_name(path):
    try:
        discoverer = GstPbutils.Discoverer.new(Gst.SECOND)
        uri = Gst.filename_to_uri(path)
        info = discoverer.discover_uri(uri)
        tags = info.get_tags()
        if tags:
            title = tags.get_string('artist')[1]
            return title
        return None
    except Exception as e:
        print(e)
    return None

def get_album_name(path):
    try:
        discoverer = GstPbutils.Discoverer.new(Gst.SECOND)
        uri = Gst.filename_to_uri(path)
        info = discoverer.discover_uri(uri)
        tags = info.get_tags()
        if tags:
            title = tags.get_string('album')[1]
            return title
        return None
    except Exception as e:
        print(e)
    return None

def get_song_length(path):
    """Returns the length of an audio file in milliseconds."""
    discoverer = GstPbutils.Discoverer.new(Gst.SECOND)
    uri = Gst.filename_to_uri(path)
    info = discoverer.discover_uri(uri)
    duration = info.get_duration() // Gst.MSECOND  # duration is now in milliseconds
    if duration:
        return duration
    return None


def get_cover_image(path):
    discoverer = GstPbutils.Discoverer.new(Gst.SECOND)
    uri = Gst.filename_to_uri(path)
    info = discoverer.discover_uri(uri)
    tags = info.get_tags()
    ok, cover = tags.get_sample('image')
    if ok and cover:
        buffer = cover.get_buffer()
        result, mapinfo = buffer.map(Gst.MapFlags.READ)
        if result:
            data = mapinfo.data

            # Load bytes into GdkPixbuf
            stream = Gio.MemoryInputStream.new_from_bytes(GLib.Bytes.new(data))
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_stream(stream, None)
            except GLib.Error:
                pixbuf = GdkPixbuf.Pixbuf()

            buffer.unmap(mapinfo)
            return pixbuf
    return None
