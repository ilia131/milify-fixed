from rest_framework.pagination import CursorPagination


class ArtistSongsPagination(CursorPagination):
    page_size = 20
    ordering = "-score"


class ArtistAlbumsPagination(CursorPagination):
    page_size = 20
    ordering = "-release_date"