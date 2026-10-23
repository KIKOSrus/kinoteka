from app import crud
from app.database import get_session
import random

def line(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main() -> None:
    session = get_session()
    try:
        # -------------------------------------------------------------
        # UC1: регистрация нового пользователя (запись в БД)
        # -------------------------------------------------------------
        line("UC1. Регистрация нового пользователя")
        existing = crud.get_user_by_username(session, "carol")
        if existing is None:
            carol = crud.create_user(session, "carol", "carol@example.com", "carolpass", role="user")
        else:
            carol = existing
        print(f"Создан/найден пользователь: {carol}")

        # -------------------------------------------------------------
        # Проверка пароля (пригодится для JWT-аутентификации в ЛР№2)
        # -------------------------------------------------------------
        line("Проверка хеширования пароля")
        print("Пароль 'carolpass' верен:", crud.verify_password("carolpass", carol.password_hash))
        print("Пароль 'wrong' верен:", crud.verify_password("wrong", carol.password_hash))

        # -------------------------------------------------------------
        # UC3: просмотр каталога, в т.ч. с фильтром по жанру
        # -------------------------------------------------------------
        line("UC3. Просмотр каталога фильмов (весь каталог)")
        for movie in crud.list_movies(session):
            genres = ", ".join(g.name for g in movie.genres)
            print(f"  [{movie.id}] {movie.title} ({movie.release_year}) — жанры: {genres}")

        line("UC3. Просмотр каталога с фильтром по жанру 'Фантастика'")
        for movie in crud.list_movies(session, genre_name="Фантастика"):
            print(f"  [{movie.id}] {movie.title}")

        # -------------------------------------------------------------
        # UC4: просмотр карточки конкретного фильма
        # -------------------------------------------------------------
        line("UC4. Просмотр карточки фильма")
        movie = crud.list_movies(session)[0]
        card = crud.get_movie(session, movie.id)
        print(f"Название: {card.title}")
        print(f"Год: {card.release_year}")
        print(f"Режиссёр: {card.director}")
        print(f"Длительность: {card.duration_minutes} мин")
        print(f"Описание: {card.description}")
        print(f"Жанры: {', '.join(g.name for g in card.genres)}")

        # -------------------------------------------------------------
        # UC9: администратор публикует новый фильм (запись + связь M:N)
        # -------------------------------------------------------------
        line("UC9. Администратор публикует новый фильм")
        new_movie = crud.create_movie(
            session,
            title="Начало",
            description="Вор похищает секреты через технологию совместных снов.",
            release_year=2010,
            director="Кристофер Нолан",
            duration_minutes=148,
            genre_names=["Фантастика", "Боевик"],
        )
        print(f"Опубликован фильм: {new_movie}")

        # -------------------------------------------------------------
        # Редактирование данных (обязательное требование: edit)
        # -------------------------------------------------------------
        line("Редактирование карточки фильма")
        updated = crud.update_movie(session, new_movie.id, duration_minutes=150)
        print(f"Обновлена длительность фильма '{updated.title}': {updated.duration_minutes} мин")

        line("Редактирование e-mail пользователя")
        updated_user = crud.update_user_email(session, carol.id, "carol.new@example.com")
        print(f"Новый e-mail пользователя {updated_user.username}: {updated_user.email}")

        # -------------------------------------------------------------
        # UC5: пользователь добавляет фильм в свою библиотеку
        # -------------------------------------------------------------
        line("UC5. Пользователь добавляет фильм в личную библиотеку")
        crud.add_to_library(session, carol.id, new_movie.id)
        print(f"Пользователь {carol.username} добавил фильм '{new_movie.title}' в библиотеку")

        # -------------------------------------------------------------
        # UC6: пользователь просматривает свою библиотеку
        # -------------------------------------------------------------
        line("UC6. Просмотр личной библиотеки пользователя (carol)")
        for m in crud.get_user_library(session, carol.id):
            print(f"  {m.title} ({m.release_year})")

        # -------------------------------------------------------------
        # UC8: администратор просматривает библиотеку любого пользователя
        # -------------------------------------------------------------
        line("UC8. Администратор просматривает библиотеку пользователя alice")
        alice = crud.get_user_by_username(session, "alice")
        for m in crud.get_user_library(session, alice.id):
            print(f"  {m.title} ({m.release_year})")

        # -------------------------------------------------------------
        # Удаление данных (обязательное требование: чтение/запись/удаление)
        # -------------------------------------------------------------
        line("Удаление фильма из библиотеки пользователя")
        removed = crud.remove_from_library(session, carol.id, new_movie.id)
        print("Запись удалена из user_library:", removed)

        line("Список всех пользователей системы")
        for u in crud.list_users(session):
            print(f"  [{u.id}] {u.username} — роль: {u.role}")

        # -------------------------------------------------------------
        # UC11: пользователь создаёт именованный плейлист
        # -------------------------------------------------------------
        line("UC11. Пользователь carol создаёт именованный плейлист")
        all_movies = crud.list_movies(session)
        first_two_ids = [m.id for m in all_movies[:2]]
        playlist = crud.create_playlist(
            session, owner_id=carol.id, name="Вечер пятницы", movie_ids=first_two_ids
        )
        print(f"Создан плейлист: {playlist} — фильмы: {[m.title for m in playlist.movies]}")

        line("Добавление ещё одного фильма в плейлист")
        extra_movie = all_movies[2] if len(all_movies) > 2 else all_movies[0]
        crud.add_movie_to_playlist(session, playlist.id, extra_movie.id)
        playlist = crud.get_playlist(session, playlist.id)
        print(f"Состав плейлиста теперь: {[m.title for m in playlist.movies]}")

        # -------------------------------------------------------------
        # UC12: другой пользователь добавляет себе чужой плейлист
        # -------------------------------------------------------------
        line("UC12. Пользователь alice добавляет себе плейлист carol")
        crud.save_playlist(session, alice.id, playlist.id)
        print(f"Пользователь alice сохранил плейлист '{playlist.name}' (автор: carol)")

        # -------------------------------------------------------------
        # UC13: просмотр сохранённых плейлистов
        # -------------------------------------------------------------
        line("UC13. Плейлисты, доступные пользователю alice")
        for pl in crud.get_saved_playlists(session, alice.id):
            print(f"  '{pl.name}' (автор: {pl.owner.username}) — фильмы: {[m.title for m in pl.movies]}")

        line("Все плейлисты в системе")
        for pl in crud.list_playlists(session):
            print(f"  [{pl.id}] {pl.name} (автор: {pl.owner.username})")

        line("Переименование плейлиста")
        renamed = crud.rename_playlist(session, playlist.id, "Пятничный киновечер")
        print(f"Новое название: {renamed.name}")

        line("Удаление фильма из плейлиста")
        crud.remove_movie_from_playlist(session, playlist.id, extra_movie.id)
        playlist = crud.get_playlist(session, playlist.id)
        print(f"Состав плейлиста после удаления: {[m.title for m in playlist.movies]}")


        # обновление фильма
        movies = crud.list_movies(session)
        print(movies)
        movie = movies[0]
        print(f"Обновление года у фильма {movie}")
        crud.update_movie(session, movie.id, release_year=random.randint(1, 3000))
        print(crud.get_movie(session, movie.id))


    finally:
        session.close()


if __name__ == "__main__":
    main()
