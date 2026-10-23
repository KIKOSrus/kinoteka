"""DTO: Pydantic-модели для HTTP-запросов и ответов (отдельно от ORM-моделей)."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Auth / Users ----------
class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str  # валидируется при вводе (UserRegister), в ответе — как в БД
    role: Literal["user", "admin"]
    created_at: datetime | None = None


class UserUpdate(BaseModel):
    email: EmailStr


class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin"]


# ---------- Genres ----------
class GenreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class GenreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# ---------- Movies ----------
class MovieBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    release_year: int | None = Field(default=None, ge=1888, le=2100)
    director: str | None = Field(default=None, max_length=150)
    duration_minutes: int | None = Field(default=None, gt=0, le=1000)


class MovieCreate(MovieBase):
    genres: list[str] = []


class MovieUpdate(BaseModel):
    """PATCH: все поля необязательны."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    release_year: int | None = Field(default=None, ge=1888, le=2100)
    director: str | None = Field(default=None, max_length=150)
    duration_minutes: int | None = Field(default=None, gt=0, le=1000)
    genres: list[str] | None = None


class MovieOut(MovieBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    genres: list[GenreOut] = []


# ---------- Library ----------
class LibraryAdd(BaseModel):
    movie_id: int


# ---------- Playlists ----------
class PlaylistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    movie_ids: list[int] = []


class PlaylistRename(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class PlaylistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    owner_id: int
    created_at: datetime | None = None
    movies: list[MovieOut] = []
