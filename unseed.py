from sqlalchemy import select

from app.database import get_session
from app.models import Genre, Movie, User

SEED_USERNAMES = ["admin", "alice", "bob", "carol"]
SEED_MOVIE_TITLES = ["Матрица", "Интерстеллар", "Криминальное чтиво", "Начало"]
SEED_GENRES = ["Фантастика", "Боевик", "Драма", "Криминал"]


def main() -> None:
    session = get_session()
    try:
        users = list(session.scalars(select(User).where(User.username.in_(SEED_USERNAMES))))
        for user in users:
            session.delete(user)
        session.commit()
        print(f"Удалено пользователей: {len(users)}")

        movies = list(session.scalars(select(Movie).where(Movie.title.in_(SEED_MOVIE_TITLES))))
        for movie in movies:
            session.delete(movie)
        session.commit()
        print(f"Удалено фильмов: {len(movies)}")

        genres = list(session.scalars(select(Genre).where(Genre.name.in_(SEED_GENRES))))
        for genre in genres:
            session.delete(genre)
        session.commit()
        print(f"Удалено жанров: {len(genres)}")

        print("Готово: тестовые данные удалены.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
