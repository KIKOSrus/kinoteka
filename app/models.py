from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    Column,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base




movie_genre = Table(
    "movie_genre",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

playlist_movie = Table(
    "playlist_movie",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True),
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin')", name="ck_users_role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


    library_entries: Mapped[list["UserLibrary"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


    owned_playlists: Mapped[list["Playlist"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


    saved_playlists: Mapped[list["SavedPlaylist"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r}, role={self.role!r})"


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_genre, back_populates="genres"
    )

    def __repr__(self) -> str:
        return f"Genre(id={self.id}, name={self.name!r})"


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    director: Mapped[str | None] = mapped_column(String(150), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    genres: Mapped[list["Genre"]] = relationship(
        secondary=movie_genre, back_populates="movies"
    )
    library_entries: Mapped[list["UserLibrary"]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Movie(id={self.id}, title={self.title!r}, year={self.release_year})"


class UserLibrary(Base):
    __tablename__ = "user_library"
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_library_user_movie"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="library_entries")
    movie: Mapped["Movie"] = relationship(back_populates="library_entries")

    def __repr__(self) -> str:
        return f"UserLibrary(user_id={self.user_id}, movie_id={self.movie_id})"


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="owned_playlists")
    movies: Mapped[list["Movie"]] = relationship(secondary=playlist_movie, order_by="Movie.title")
    saved_by: Mapped[list["SavedPlaylist"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Playlist(id={self.id}, name={self.name!r}, owner_id={self.owner_id})"


class SavedPlaylist(Base):
    __tablename__ = "saved_playlists"
    __table_args__ = (
        UniqueConstraint("user_id", "playlist_id", name="uq_saved_playlists_user_playlist"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="saved_playlists")
    playlist: Mapped["Playlist"] = relationship(back_populates="saved_by")

    def __repr__(self) -> str:
        return f"SavedPlaylist(user_id={self.user_id}, playlist_id={self.playlist_id})"
