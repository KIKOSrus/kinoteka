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

## Запуск

### Вариант 1 — Docker Compose (БД + backend + nginx)

```bash
docker compose up --build
docker compose exec backend python seed.py       # тестовые данные (admin / admin12345)
./demo.sh http://localhost
```
Всё доступно на http://localhost (nginx :80).

### Вариант 2 — локально

```bash
# 1. БД и зависимости (как в ЛР№1)
sudo -u postgres psql -f init_db.sql
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python seed.py

# 2. Backend
gunicorn -c gunicorn.conf.py app.main:app           # Linux/macOS (127.0.0.1:8000)
uvicorn app.main:app --reload                       # Windows / разработка

# 3. (доп. задание №1) Nginx — см. комментарии в начале nginx/nginx.conf
```
Без nginx API доступно на http://127.0.0.1:8000, с nginx — на http://localhost.

Тестовые пользователи из `seed.py`: `admin / admin12345` (админ), `alice / alicepass`, `bob / bobpass`.

## Демонстрация (cURL)

```bash
curl -X POST http://localhost/register -H 'Content-Type: application/json' \
     -d '{"username":"neo","email":"neo@example.com","password":"secret1"}'

curl -X POST http://localhost/login -H 'Content-Type: application/json' \
     -d '{"username":"neo","password":"secret1"}'
# => {"access_token":"eyJ...","token_type":"bearer","expires_in":3600}

curl http://localhost/movies -H 'Authorization: Bearer eyJ...'
```
Полный сценарий (регистрация → вход → каталог → права admin → библиотека → плейлисты) — `./demo.sh`.
В Postman: создайте переменную `{{token}}` и на вкладке Authorization выберите Bearer Token, либо импортируйте
схему из `http://localhost/openapi.json` (Import → Link).

## Тесты

```bash
python -m pytest -q tests      # нужна БД с миграциями и seed.py
```

## Про uWSGI

FastAPI — ASGI-приложение, а uWSGI изначально рассчитан на WSGI, поэтому в проекте используется Gunicorn
с воркерами `uvicorn.workers.UvicornWorker`. Nginx при этом проксирует по HTTP на Gunicorn (`proxy_pass`).

## Что исправлено в ЛР№1

Миграция `alembic/versions/fcba78371da3_new.py` (автогенерация) повторно создавала уже существующие
уникальные ограничения, из‑за чего `alembic upgrade head` падал на чистой БД
(`relation "uq_saved_playlists_user_playlist" already exists`). Миграция сделана пустой (no-op).
