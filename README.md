# Кинотека — Лабораторная работа №2: REST API

REST API на **FastAPI** поверх БД из ЛР№1 (SQLAlchemy + PostgreSQL + Alembic).
Регистрация и вход, JWT, CRUD над каталогом, личная библиотека и плейлисты.
За API стоит **Nginx** (reverse proxy + статика), приложение запускается через **Gunicorn**.

## Архитектура

```
Клиент (Postman / cURL)
   │  HTTP
   ▼
Nginx :80 ──/ , /static/*──► статические файлы
   │  всё остальное (proxy_pass)
   ▼
Gunicorn (воркеры uvicorn) :8000
   ▼
FastAPI: router ─► service ─► repository ─► crud.py / ORM (ЛР№1) ─► PostgreSQL
```

```
app/
├── main.py            # приложение, обработчик ошибок
├── config.py          # SECRET_KEY, срок жизни токена (из .env)
├── security.py        # bcrypt + создание/проверка JWT
├── schemas.py         # DTO (Pydantic) — модели HTTP-запросов/ответов
├── models.py          # ORM-модели (SQLAlchemy) — слой данных, из ЛР№1
├── crud.py            # CRUD из ЛР№1
├── repositories.py    # репозитории (доступ к данным)
├── services/          # бизнес-логика: auth, catalog, personal (библиотека, плейлисты)
├── deps.py            # Dependency Injection: Session → Repository → Service → current user
├── exceptions.py      # доменные ошибки → HTTP-коды
└── routers/           # auth, users, movies(+genres), library, playlists
nginx/nginx.conf, nginx/static/   # доп. задание №1
gunicorn.conf.py, Dockerfile, docker-compose.yml
tests/test_api.py, demo.sh        # автотесты и cURL-демо
```

* **DTO и ORM разделены**: `schemas.py` (Pydantic) отвечает за HTTP, `models.py` (SQLAlchemy) — за БД.
  Пароль и `password_hash` никогда не попадают в ответы.
* **Dependency Injection**: роутеры получают сервисы через `Depends`, сервисы — репозитории, репозитории — сессию БД
  (`app/deps.py`). Текущий пользователь и проверка роли admin — тоже зависимости.
* **JWT (доп. задание №2)**: `/login` выдаёт токен (`sub` = id пользователя, `role`, `exp`), дальше он передаётся
  в заголовке `Authorization: Bearer <token>`. Роль `admin` проверяется зависимостью `require_admin`.

## Эндпоинты

| Метод и путь | Доступ | Описание |
|---|---|---|
| `POST /register` | все | регистрация (роль всегда `user`) |
| `POST /login` | все | вход по JSON `{username, password}` → JWT |
| `GET /me`, `PATCH /me`, `DELETE /me` | авторизованный | профиль, смена email, удаление аккаунта |
| `GET /users`, `GET /users/{id}`, `PATCH /users/{id}/role`, `DELETE /users/{id}` | admin | управление пользователями |
| `GET /movies` (`?genre=&search=&skip=&limit=`), `GET /movies/{id}` | авторизованный | каталог, карточка фильма |
| `POST /movies`, `PATCH /movies/{id}`, `DELETE /movies/{id}` | admin | управление каталогом |
| `GET /genres` / `POST /genres`, `DELETE /genres/{id}` | авторизованный / admin | жанры |
| `GET /library`, `POST /library` `{movie_id}`, `DELETE /library/{movie_id}` | авторизованный | личная библиотека |
| `GET /playlists` (`?owner_id=`), `GET /playlists/{id}`, `POST /playlists` | авторизованный | плейлисты |
| `PATCH /playlists/{id}`, `DELETE /playlists/{id}` | автор или admin | переименование, удаление |
| `PUT/DELETE /playlists/{id}/movies/{movie_id}` | автор или admin | состав плейлиста |
| `GET /playlists/saved`, `PUT/DELETE /playlists/{id}/save` | авторизованный | сохранённые плейлисты |
| `GET /health` | все | проверка работоспособности |

Коды ошибок: `401` — нет/неверный/просроченный токен, `403` — недостаточно прав, `404` — не найдено,
`409` — конфликт (дубликат), `422` — ошибка валидации. Интерактивная документация: `/docs` (Swagger UI, кнопка Authorize).
