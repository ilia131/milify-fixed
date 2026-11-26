from rest_framework.pagination import CursorPagination

class ExplorePagination(CursorPagination):
    page_size = 20
    ordering = "-score"



class SongSearchPagination(CursorPagination):
    page_size = 20
    ordering = "-play_count"


class ArtistSearchPagination(CursorPagination):
    page_size = 20
    ordering = "-monthly_listeners_calc"


class GenreBrowsePagination(CursorPagination):
    page_size = 10
    ordering = "-songs_count"
    

class GenreSongsPagination(CursorPagination):
    page_size = 20
    ordering = ("-plays_last_24h", "-play_count", "-id")