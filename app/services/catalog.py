from sqlalchemy.exc import IntegrityError

from app import schemas
from app.exceptions import ConflictError, NotFoundError
from app.models import Genre, Movie
from app.repositories import GenreRepository, MovieRepository


class MovieService:
    def __init__(self, movies: MovieRepository):
        self.movies = movies

    def list_all(self, genre=None, search=None, skip=0, limit=50) -> list[Movie]:
        return self.movies.list_all(genre, search, skip, limit)

    def get(self, movie_id: int) -> Movie:
        movie = self.movies.get(movie_id)
        if movie is None:
            raise NotFoundError("Фильм не найден")
        return movie

    def create(self, data: schemas.MovieCreate) -> Movie:
        return self.movies.create(**data.model_dump())

    def update(self, movie_id: int, data: schemas.MovieUpdate) -> Movie:
        fields = data.model_dump(exclude_unset=True)
        genres = fields.pop("genres", None)
        movie = self.movies.update(movie_id, genres=genres, **fields)
        if movie is None:
            raise NotFoundError("Фильм не найден")
        return movie

    def delete(self, movie_id: int) -> None:
        if not self.movies.delete(movie_id):
            raise NotFoundError("Фильм не найден")


class GenreService:
    def __init__(self, genres: GenreRepository):
        self.genres = genres

    def list_all(self) -> list[Genre]:
        return self.genres.list_all()

    def create(self, name: str) -> Genre:
        if self.genres.get_by_name(name):
            raise ConflictError("Такой жанр уже существует")
        try:
            return self.genres.create(name)
        except IntegrityError:
            self.genres.db.rollback()
            raise ConflictError("Такой жанр уже существует")

    def delete(self, genre_id: int) -> None:
        if not self.genres.delete(genre_id):
            raise NotFoundError("Жанр не найден")
