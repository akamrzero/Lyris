import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Adw


class AlbumArt(Adw.Bin):
    __gtype_name__ = 'AlbumArt'

    _fallback_icon_name = 'music-note-symbolic'
    _spacing = 6

    def __init__(self, size: int, placeholder_icon: str='music-note-symbolic', covers: list[GdkPixbuf.Pixbuf]=None):
        """
        A reusable GTK widget for displaying album artwork or a placeholder image.

        This widget can display:
          • A single album cover.
          • A collage of up to four covers (e.g., for playlists).
          • A fallback placeholder when no image is provided.

        Args:
            size (int): The width and height of the album art area in pixels.
            placeholder_icon (str, optional): The name of the icon to use.
            *covers (GdkPixbuf.Pixbuf): The data image data, up to 4)
        Raises:
            ValueError: If `size` is not a positive integer.
            ValueError: If more than 4 images are passed in `covers`.
            TypeError: If `covers` is not a list with items of type GdkPixbuf.Pixbuf or None.
        """
        if size <= 0:
            raise ValueError('`size` must be a positive integer.')#

        if not covers:
            covers = []

        if len(covers) > 4:
            raise ValueError('`covers` can only include up to 4 images.')

        for cover in covers:
            if cover is not None and not isinstance(cover, GdkPixbuf.Pixbuf):
                raise ValueError('All items in `covers` must be of type GdkPixbuf.Pixbuf or None.')

        super().__init__()

        self.size = size

        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        self.placeholder_icon = self._fallback_icon_name
        if icon_theme.has_icon(placeholder_icon):
            self.placeholder_icon = placeholder_icon

        self.covers = covers
        self.cover_number = min(len(self.covers), 4)
        # if any(c is not None for c in self.covers):
        #     self.draw_covers()
        # else:
        #     self.draw_placeholder()
        self.draw_covers()

        self.set_size_request(size, size)

    def draw_covers(self):
        wrapper = Gtk.FlowBox(
            orientation=Gtk.Orientation.VERTICAL,
            max_children_per_line=2,
            selection_mode=Gtk.SelectionMode.NONE,
            can_target=False,
        )

        if self.covers:
            spacing = self._spacing if self.cover_number > 1 else 0
            pixel_size = int(self.size / self.cover_number - spacing)
            for cover in self.covers:
                if cover:
                    item = Gtk.Image.new_from_pixbuf(cover)
                    item.set_pixel_size(pixel_size)
                else:
                    image = Gtk.Image.new_from_icon_name(self.placeholder_icon)
                    image.set_pixel_size(int(self.size*0.5 / self.cover_number))
                    item = Adw.Bin()
                    item.set_size_request(pixel_size, pixel_size)
                    item.add_css_class('lyris-accent-bg-2')
                    item.set_child(image)

                item.add_css_class('lyris-all-rounded-corners')
                item.set_overflow(Gtk.Overflow.HIDDEN)
                wrapper.append(item)
        else:
            image = Gtk.Image.new_from_icon_name(self.placeholder_icon)
            image.set_pixel_size(int(self.size * 0.5))
            item = Adw.Bin()
            item.set_size_request(self.size ,self.size)
            item.add_css_class('lyris-accent-bg-2')
            item.set_child(image)

            item.add_css_class('lyris-all-rounded-corners')
            item.set_overflow(Gtk.Overflow.HIDDEN)
            wrapper.append(item)


        self.set_child(wrapper)









