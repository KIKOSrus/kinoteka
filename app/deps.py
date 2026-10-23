"""Dependency Injection: сессия БД -> репозитории -> сервисы -> текущий пользователь."""
from typing import Annotated, Iterator

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.exceptions import AuthError, ForbiddenError
from app.models import User
from app.repositories import (
    GenreRepository,
    LibraryRepository,
    MovieRepository,
    PlaylistRepository,
    UserRepository,
)
from app.security import decode_access_token
from app.services.auth import AuthService, UserService
from app.services.catalog import GenreService, MovieService
from app.services.personal import LibraryService, PlaylistService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DB = Annotated[Session, Depends(get_db)]


# --- репозитории ---
def get_user_repo(db: DB) -> UserRepository:
    return UserRepository(db)


def get_genre_repo(db: DB) -> GenreRepository:
    return GenreRepository(db)


def get_movie_repo(db: DB) -> MovieRepository:
    return MovieRepository(db)


def get_library_repo(db: DB) -> LibraryRepository:
    return LibraryRepository(db)


def get_playlist_repo(db: DB) -> PlaylistRepository:
    return PlaylistRepository(db)


# --- сервисы ---
def get_auth_service(users: Annotated[UserRepository, Depends(get_user_repo)]) -> AuthService:
    return AuthService(users)


def get_user_service(users: Annotated[UserRepository, Depends(get_user_repo)]) -> UserService:
    return UserService(users)


def get_movie_service(movies: Annotated[MovieRepository, Depends(get_movie_repo)]) -> MovieService:
    return MovieService(movies)


def get_genre_service(genres: Annotated[GenreRepository, Depends(get_genre_repo)]) -> GenreService:
    return GenreService(genres)


def get_library_service(
    library: Annotated[LibraryRepository, Depends(get_library_repo)],
    movies: Annotated[MovieRepository, Depends(get_movie_repo)],
) -> LibraryService:
    return LibraryService(library, movies)


def get_playlist_service(
    playlists: Annotated[PlaylistRepository, Depends(get_playlist_repo)],
    movies: Annotated[MovieRepository, Depends(get_movie_repo)],
) -> PlaylistService:
    return PlaylistService(playlists, movies)


# --- аутентификация / авторизация (JWT) ---
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    users: Annotated[UserRepository, Depends(get_user_repo)],
) -> User:
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise AuthError("Недействительный или просроченный токен")
    user = users.get(user_id)
    if user is None:
        raise AuthError("Пользователь токена не найден")
    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != "admin":
        raise ForbiddenError("Требуются права администратора")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
UserSvc = Annotated[UserService, Depends(get_user_service)]
MovieSvc = Annotated[MovieService, Depends(get_movie_service)]
GenreSvc = Annotated[GenreService, Depends(get_genre_service)]
LibrarySvc = Annotated[LibraryService, Depends(get_library_service)]
PlaylistSvc = Annotated[PlaylistService, Depends(get_playlist_service)]
