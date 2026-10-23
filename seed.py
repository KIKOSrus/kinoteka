from app.crud import add_to_library, create_movie, create_playlist, create_user, save_playlist
from app.database import get_session


def main() -> None:
    session = get_session()
    try:
        print("Добавляю пользователей...")
        admin = create_user(session, "admin", "admin@kinoteka.local", "admin12345", role="admin")
        alice = create_user(session, "alice", "alice@example.com", "alicepass", role="user")
        bob = create_user(session, "bob", "bob@example.com", "bobpass", role="user")

        print("Добавляю фильмы...")
        matrix = create_movie(
            session,
            title="Матрица",
            description="Хакер узнаёт правду о природе реальности.",
            release_year=1999,
            director="Лана и Лилли Вачовски",
            duration_minutes=136,
            genre_names=["Фантастика", "Боевик"],
        )
        interstellar = create_movie(
            session,
            title="Интерстеллар",
            description="Экипаж космического корабля ищет новый дом для человечества.",
            release_year=2014,
            director="Кристофер Нолан",
            duration_minutes=169,
            genre_names=["Фантастика", "Драма"],
        )
        pulp_fiction = create_movie(
            session,
            title="Криминальное чтиво",
            description="Несколько переплетающихся историй из жизни бандитов Лос-Анджелеса.",
            release_year=1994,
            director="Квентин Тарантино",
            duration_minutes=154,
            genre_names=["Криминал", "Драма"],
        )
        inception = create_movie(
            session,
            title="Начало",
            description="Вор похищает секреты через технологию совместных снов.",
            release_year=2010,
            director="Кристофер Нолан",
            duration_minutes=148,
            genre_names=["Фантастика", "Боевик"],
        )

        print("Наполняю личные библиотеки пользователей...")
        add_to_library(session, alice.id, matrix.id)
        add_to_library(session, alice.id, interstellar.id)
        add_to_library(session, bob.id, pulp_fiction.id)

        print("Создаю плейлисты...")
        nolan_playlist = create_playlist(
            session,
            owner_id=alice.id,
            name="Лучшее у Нолана",
            movie_ids=[interstellar.id, inception.id],
        )
        crime_playlist = create_playlist(
            session,
            owner_id=bob.id,
            name="Криминальные драмы",
            movie_ids=[pulp_fiction.id],
        )

        print("Пользователь bob добавляет себе плейлист alice...")
        save_playlist(session, bob.id, nolan_playlist.id)

        print(f"Готово: БД заполнена тестовыми данными "
              f"(плейлисты: {nolan_playlist.name!r}, {crime_playlist.name!r}).")
    finally:
        session.close()


if __name__ == "__main__":
    main()
