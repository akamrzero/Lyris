from .views.playlists_view import PlaylistView

from src.utils.db_manager import DBM
from src.widgets.entitys.entity_page import EntityPage

class PlaylistsPage(EntityPage):
    __gtype_name__ = 'PlaylistsPage'

    def __init__(self,):
        super().__init__()

        self.content = PlaylistView()
        self.content.set_playlists(DBM.playlist.get())
        self.set_child(self.content)






