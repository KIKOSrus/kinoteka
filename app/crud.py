import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Genre, Movie, Playlist, SavedPlaylist, User, UserLibrary


# ---------------------------------------------------------------------------
# Пользователи (users)
# ---------------------------------------------------------------------------
def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def create_user(session: Session, username: str, email: str, password: str, role: str = "user") -> User:
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    return session.scalar(stmt)


def list_users(session: Session) -> list[User]:
    return list(session.scalars(select(User).order_by(User.id)))


def update_user_email(session: Session, user_id: int, new_email: str) -> User | None:
    user = session.get(User, user_id)
    if user is None:
        return None
    user.email = new_email
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if user is None:
        return False
    session.delete(user)
    session.commit()
    return True


# ---------------------------------------------------------------------------
# Жанры (genres)
# ---------------------------------------------------------------------------
def create_genre(session: Session, name: str) -> Genre:
    genre = Genre(name=name)
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre


def get_or_create_genre(session: Session, name: str) -> Genre:
    genre = session.scalar(select(Genre).where(Genre.name == name))
    if genre is None:
        genre = create_genre(session, name)
    return genre


def list_genres(session: Session) -> list[Genre]:
    return list(session.scalars(select(Genre).order_by(Genre.name)))


def delete_genre(session: Session, genre_id: int) -> bool:
    genre = session.get(Genre, genre_id)
    if genre is None:
        return False
    session.delete(genre)
    session.commit()
    return True


# ---------------------------------------------------------------------------
# Фильмы (movies) — сценарии UC3, UC4, UC9
# ---------------------------------------------------------------------------
def create_movie(
    session: Session,
    title: str,
    description: str | None = None,
    release_year: int | None = None,
    director: str | None = None,
    duration_minutes: int | None = None,
    genre_names: list[str] | None = None,
) -> Movie:
    movie = Movie(
        title=title,
        description=description,
        release_year=release_year,
        director=director,
        duration_minutes=duration_minutes,
    )
    if genre_names:
        movie.genres = [get_or_create_genre(session, name) for name in genre_names]
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie


def get_movie(session: Session, movie_id: int) -> Movie | None:
    """UC4: просмотр карточки фильма."""
    return session.get(Movie, movie_id)


def list_movies(session: Session, genre_name: str | None = None) -> list[Movie]:
    """UC3: просмотр каталога, опционально с фильтром по жанру."""
    stmt = select(Movie).order_by(Movie.title)
    if genre_name:
        stmt = stmt.join(Movie.genres).where(Genre.name == genre_name)
    return list(session.scalars(stmt).unique())


def update_movie(session: Session, movie_id: int, **fields) -> Movie | None:
    movie = session.get(Movie, movie_id)
    if movie is None:
        return None
    for key, value in fields.items():
        setattr(movie, key, value)
    session.commit()
    session.refresh(movie)
    return movie


def delete_movie(session: Session, movie_id: int) -> bool:
    movie = session.get(Movie, movie_id)
    if movie is None:
        return False
    session.delete(movie)
    session.commit()
    return True


# ---------------------------------------------------------------------------
# Личная библиотека (user_library) — сценарии UC5, UC6, UC8
# ---------------------------------------------------------------------------
def add_to_library(session: Session, user_id: int, movie_id: int) -> UserLibrary:
    existing = session.get(UserLibrary, (user_id, movie_id))
    if existing is not None:
        return existing
    entry = UserLibrary(user_id=user_id, movie_id=movie_id)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def remove_from_library(session: Session, user_id: int, movie_id: int) -> bool:
    entry = session.get(UserLibrary, (user_id, movie_id))
    if entry is None:
        return False
    session.delete(entry)
    session.commit()
    return True


def get_user_library(session: Session, user_id: int) -> list[Movie]:
    stmt = (
        select(Movie)
        .join(UserLibrary, UserLibrary.movie_id == Movie.id)
        .where(UserLibrary.user_id == user_id)
        .order_by(UserLibrary.added_at)
    )
    return list(session.scalars(stmt))


# ---------------------------------------------------------------------------
# Плейлисты (playlists) — UC11, UC12, UC13
#
# UC11: пользователь создаёт именованный плейлист и наполняет его фильмами.
# UC12: пользователь просматривает чужой плейлист и добавляет его себе
#       (сохраняет в свою коллекцию), не копируя сами фильмы — просто
#       получая ссылку на оригинальный плейлист автора.
# UC13: пользователь просматривает список сохранённых им плейлистов
#       (своих и чужих добавленных).
# ---------------------------------------------------------------------------
def create_playlist(
    session: Session,
    owner_id: int,
    name: str,
    movie_ids: list[int] | None = None,
) -> Playlist:
    """UC11: пользователь создаёт именованный плейлист."""
    playlist = Playlist(name=name, owner_id=owner_id)
    if movie_ids:
        playlist.movies = list(
            session.scalars(select(Movie).where(Movie.id.in_(movie_ids)))
        )
    session.add(playlist)
    session.commit()
    session.refresh(playlist)
    return playlist


def get_playlist(session: Session, playlist_id: int) -> Playlist | None:
    return session.get(Playlist, playlist_id)


def list_playlists(session: Session, owner_id: int | None = None) -> list[Playlist]:
    """Все плейлисты в системе, либо только плейлисты конкретного автора."""
    stmt = select(Playlist).order_by(Playlist.name)
    if owner_id is not None:
        stmt = stmt.where(Playlist.owner_id == owner_id)
    return list(session.scalars(stmt))


def rename_playlist(session: Session, playlist_id: int, new_name: str) -> Playlist | None:
    playlist = session.get(Playlist, playlist_id)
    if playlist is None:
        return None
    playlist.name = new_name
    session.commit()
    session.refresh(playlist)
    return playlist


def add_movie_to_playlist(session: Session, playlist_id: int, movie_id: int) -> Playlist | None:
    playlist = session.get(Playlist, playlist_id)
    movie = session.get(Movie, movie_id)
    if playlist is None or movie is None:
        return None
    if movie not in playlist.movies:
        playlist.movies.append(movie)
        session.commit()
        session.refresh(playlist)
    return playlist


def remove_movie_from_playlist(session: Session, playlist_id: int, movie_id: int) -> Playlist | None:
    playlist = session.get(Playlist, playlist_id)
    movie = session.get(Movie, movie_id)
    if playlist is None or movie is None:
        return None
    if movie in playlist.movies:
        playlist.movies.remove(movie)
        session.commit()
        session.refresh(playlist)
    return playlist


def delete_playlist(session: Session, playlist_id: int) -> bool:
    playlist = session.get(Playlist, playlist_id)
    if playlist is None:
        return False
    session.delete(playlist)
    session.commit()
    return True


def save_playlist(session: Session, user_id: int, playlist_id: int) -> SavedPlaylist | None:
    playlist = session.get(Playlist, playlist_id)
    if playlist is None:
        return None
    existing = session.get(SavedPlaylist, (user_id, playlist_id))
    if existing is not None:
        return existing
    entry = SavedPlaylist(user_id=user_id, playlist_id=playlist_id)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def unsave_playlist(session: Session, user_id: int, playlist_id: int) -> bool:
    entry = session.get(SavedPlaylist, (user_id, playlist_id))
    if entry is None:
        return False
    session.delete(entry)
    session.commit()
    return True


def get_saved_playlists(session: Session, user_id: int) -> list[Playlist]:
    stmt = (
        select(Playlist)
        .join(SavedPlaylist, SavedPlaylist.playlist_id == Playlist.id)
        .where(SavedPlaylist.user_id == user_id)
        .order_by(SavedPlaylist.added_at)
    )
    return list(session.scalars(stmt))
