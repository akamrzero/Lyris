from .entitys.entity_page import EntityPage
from .views.album_view import AlbumView
from ..utils.db_manager import DBM

class AlbumsPage(EntityPage):
    __gtype_name__ = 'AlbumsPage'
    def __init__(self):
        super().__init__()


        self.content = AlbumView()
        self.content.set_albums(DBM.album.get_ids())
        self.set_child(self.content)

