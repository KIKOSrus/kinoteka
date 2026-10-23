"""Репозитории: единственное место, где сервисы обращаются к БД (через crud.py из ЛР№1)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import crud
from app.models import Genre, Movie, Playlist, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> User | None:
        return crud.get_user(self.db, user_id)

    def get_by_username(self, username: str) -> User | None:
        return crud.get_user_by_username(self.db, username)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def list_all(self) -> list[User]:
        return crud.list_users(self.db)

    def create(self, username: str, email: str, password: str, role: str = "user") -> User:
        return crud.create_user(self.db, username, email, password, role)

    def update_email(self, user_id: int, email: str) -> User | None:
        return crud.update_user_email(self.db, user_id, email)

    def set_role(self, user_id: int, role: str) -> User | None:
        user = self.db.get(User, user_id)
        if user is None:
            return None
        user.role = role
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        return crud.delete_user(self.db, user_id)


class GenreRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Genre]:
        return crud.list_genres(self.db)

    def get_by_name(self, name: str) -> Genre | None:
        return self.db.scalar(select(Genre).where(Genre.name == name))

    def create(self, name: str) -> Genre:
        return crud.create_genre(self.db, name)

    def delete(self, genre_id: int) -> bool:
        return crud.delete_genre(self.db, genre_id)


class MovieRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, movie_id: int) -> Movie | None:
        return crud.get_movie(self.db, movie_id)

    def list_all(self, genre: str | None = None, search: str | None = None,
             skip: int = 0, limit: int = 50) -> list[Movie]:
        stmt = select(Movie).order_by(Movie.title)
        if genre:
            stmt = stmt.join(Movie.genres).where(Genre.name == genre)
        if search:
            stmt = stmt.where(Movie.title.ilike(f"%{search}%"))
        stmt = stmt.offset(skip).limit(limit)
        return list(self.db.scalars(stmt).unique())

    def create(self, **data) -> Movie:
        return crud.create_movie(
            self.db,
            title=data["title"],
            description=data.get("description"),
            release_year=data.get("release_year"),
            director=data.get("director"),
            duration_minutes=data.get("duration_minutes"),
            genre_names=data.get("genres") or None,
        )

    def update(self, movie_id: int, genres: list[str] | None = None, **fields) -> Movie | None:
        movie = crud.update_movie(self.db, movie_id, **fields) if fields else self.get(movie_id)
        if movie is not None and genres is not None:
            movie.genres = [crud.get_or_create_genre(self.db, g) for g in genres]
            self.db.commit()
            self.db.refresh(movie)
        return movie

    def delete(self, movie_id: int) -> bool:
        return crud.delete_movie(self.db, movie_id)


class LibraryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, user_id: int) -> list[Movie]:
        return crud.get_user_library(self.db, user_id)

    def add(self, user_id: int, movie_id: int):
        return crud.add_to_library(self.db, user_id, movie_id)

    def remove(self, user_id: int, movie_id: int) -> bool:
        return crud.remove_from_library(self.db, user_id, movie_id)


class PlaylistRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, playlist_id: int) -> Playlist | None:
        return crud.get_playlist(self.db, playlist_id)

    def list_all(self, owner_id: int | None = None) -> list[Playlist]:
        return crud.list_playlists(self.db, owner_id)

    def create(self, owner_id: int, name: str, movie_ids: list[int]) -> Playlist:
        return crud.create_playlist(self.db, owner_id, name, movie_ids)

    def rename(self, playlist_id: int, name: str) -> Playlist | None:
        return crud.rename_playlist(self.db, playlist_id, name)

    def add_movie(self, playlist_id: int, movie_id: int) -> Playlist | None:
        return crud.add_movie_to_playlist(self.db, playlist_id, movie_id)

    def remove_movie(self, playlist_id: int, movie_id: int) -> Playlist | None:
        return crud.remove_movie_from_playlist(self.db, playlist_id, movie_id)

    def delete(self, playlist_id: int) -> bool:
        return crud.delete_playlist(self.db, playlist_id)

    def saved(self, user_id: int) -> list[Playlist]:
        return crud.get_saved_playlists(self.db, user_id)

    def save(self, user_id: int, playlist_id: int):
        return crud.save_playlist(self.db, user_id, playlist_id)

    def unsave(self, user_id: int, playlist_id: int) -> bool:
        return crud.unsave_playlist(self.db, user_id, playlist_id)
