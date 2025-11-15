from .entitys.entity_page import EntityPage
from .views.artist_view import ArtistView
from ..utils.db_manager import DBM

class ArtistsPage(EntityPage):
    __gtype_name__ = 'ArtistsPage'

    def __init__(self):
        super().__init__()

        self.content = ArtistView()
        self.content.set_artists(DBM.artist.get_ids())
        self.set_child(self.content)
