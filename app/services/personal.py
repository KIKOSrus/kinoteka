"""Личная библиотека и плейлисты."""
from app.exceptions import ForbiddenError, NotFoundError
from app.models import Movie, Playlist, User
from app.repositories import LibraryRepository, MovieRepository, PlaylistRepository


class LibraryService:
    def __init__(self, library: LibraryRepository, movies: MovieRepository):
        self.library = library
        self.movies = movies

    def list_all(self, user: User) -> list[Movie]:
        return self.library.list_all(user.id)

    def add(self, user: User, movie_id: int) -> None:
        if self.movies.get(movie_id) is None:
            raise NotFoundError("Фильм не найден")
        self.library.add(user.id, movie_id)

    def remove(self, user: User, movie_id: int) -> None:
        if not self.library.remove(user.id, movie_id):
            raise NotFoundError("Фильма нет в вашей библиотеке")


class PlaylistService:
    def __init__(self, playlists: PlaylistRepository, movies: MovieRepository):
        self.playlists = playlists
        self.movies = movies

    def _get(self, playlist_id: int) -> Playlist:
        playlist = self.playlists.get(playlist_id)
        if playlist is None:
            raise NotFoundError("Плейлист не найден")
        return playlist

    def _get_owned(self, playlist_id: int, user: User) -> Playlist:
        playlist = self._get(playlist_id)
        if playlist.owner_id != user.id and user.role != "admin":
            raise ForbiddenError("Изменять плейлист может только его автор")
        return playlist

    def list_all(self, owner_id: int | None = None) -> list[Playlist]:
        return self.playlists.list_all(owner_id)

    def get(self, playlist_id: int) -> Playlist:
        return self._get(playlist_id)

    def create(self, user: User, name: str, movie_ids: list[int]) -> Playlist:
        return self.playlists.create(user.id, name, movie_ids)

    def rename(self, playlist_id: int, user: User, name: str) -> Playlist:
        self._get_owned(playlist_id, user)
        return self.playlists.rename(playlist_id, name)

    def delete(self, playlist_id: int, user: User) -> None:
        self._get_owned(playlist_id, user)
        self.playlists.delete(playlist_id)

    def add_movie(self, playlist_id: int, user: User, movie_id: int) -> Playlist:
        self._get_owned(playlist_id, user)
        playlist = self.playlists.add_movie(playlist_id, movie_id)
        if playlist is None:
            raise NotFoundError("Фильм не найден")
        return playlist

    def remove_movie(self, playlist_id: int, user: User, movie_id: int) -> Playlist:
        self._get_owned(playlist_id, user)
        playlist = self.playlists.remove_movie(playlist_id, movie_id)
        if playlist is None:
            raise NotFoundError("Фильм не найден")
        return playlist

    def saved(self, user: User) -> list[Playlist]:
        return self.playlists.saved(user.id)

    def save(self, user: User, playlist_id: int) -> None:
        if self.playlists.save(user.id, playlist_id) is None:
            raise NotFoundError("Плейлист не найден")

    def unsave(self, user: User, playlist_id: int) -> None:
        if not self.playlists.unsave(user.id, playlist_id):
            raise NotFoundError("Плейлист не был сохранён")
