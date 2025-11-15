from ..utils.db_manager import DBM
from .entitys.entity_page import EntityPage
from.views.song_view import SongView

class SongsPage(EntityPage):
    __gtype_name__ = 'SongsPage'

    def __init__(self,):
        super().__init__()

        self.content = SongView()
        self.content.set_songs(DBM.song.get_all())
        self.set_child(self.content)
