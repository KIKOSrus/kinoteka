"""Сквозные тесты API. Требуют запущенную БД с миграциями и seed.py (admin / admin12345)."""
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def login(username, password):
    r = client.post("/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def admin():
    return login("admin", "admin12345")


@pytest.fixture(scope="module")
def user():
    name = "u" + uuid.uuid4().hex[:8]
    r = client.post("/register", json={"username": name, "email": f"{name}@ex.com", "password": "secret1"})
    assert r.status_code == 201
    assert r.json()["role"] == "user" and "password" not in r.json()
    return {"name": name, "token": login(name, "secret1"), "id": r.json()["id"]}


def test_register_duplicate_and_validation(user):
    r = client.post("/register", json={"username": user["name"], "email": "x@ex.com", "password": "secret1"})
    assert r.status_code == 409
    assert client.post("/register", json={"username": "ab", "email": "bad", "password": "1"}).status_code == 422


def test_login_wrong_password(user):
    assert client.post("/login", json={"username": user["name"], "password": "nope"}).status_code == 401


def test_protected_requires_token():
    assert client.get("/movies").status_code == 401
    assert client.get("/movies", headers=auth("garbage")).status_code == 401
    assert client.get("/health").status_code == 200


def test_me(user):
    r = client.get("/me", headers=auth(user["token"]))
    assert r.status_code == 200 and r.json()["username"] == user["name"]


def test_movies_crud_admin_only(admin, user):
    body = {"title": "Тест-фильм", "release_year": 2020, "genres": ["Тест"]}
    assert client.post("/movies", json=body, headers=auth(user["token"])).status_code == 403
    r = client.post("/movies", json=body, headers=auth(admin))
    assert r.status_code == 201
    mid = r.json()["id"]
    assert r.json()["genres"][0]["name"] == "Тест"

    assert client.get(f"/movies/{mid}", headers=auth(user["token"])).status_code == 200
    assert client.get("/movies?genre=Тест", headers=auth(user["token"])).json()[0]["id"] == mid
    assert client.get("/movies?search=тест-фи", headers=auth(user["token"])).status_code == 200

    r = client.patch(f"/movies/{mid}", json={"director": "Я", "genres": []}, headers=auth(admin))
    assert r.status_code == 200 and r.json()["director"] == "Я" and r.json()["genres"] == []
    assert client.patch(f"/movies/{mid}", json={"release_year": 1}, headers=auth(admin)).status_code == 422

    assert client.delete(f"/movies/{mid}", headers=auth(user["token"])).status_code == 403
    assert client.delete(f"/movies/{mid}", headers=auth(admin)).status_code == 204
    assert client.get(f"/movies/{mid}", headers=auth(admin)).status_code == 404


def test_library(user):
    h = auth(user["token"])
    movies = client.get("/movies", headers=h).json()
    mid = movies[0]["id"]
    assert client.post("/library", json={"movie_id": mid}, headers=h).status_code == 204
    assert client.post("/library", json={"movie_id": mid}, headers=h).status_code == 204  # идемпотентно
    assert [m["id"] for m in client.get("/library", headers=h).json()] == [mid]
    assert client.post("/library", json={"movie_id": 999999}, headers=h).status_code == 404
    assert client.delete(f"/library/{mid}", headers=h).status_code == 204
    assert client.delete(f"/library/{mid}", headers=h).status_code == 404


def test_playlists_flow_and_permissions(user, admin):
    h = auth(user["token"])
    movies = client.get("/movies", headers=h).json()
    m1, m2 = movies[0]["id"], movies[1]["id"]

    r = client.post("/playlists", json={"name": "Мой", "movie_ids": [m1]}, headers=h)
    assert r.status_code == 201
    pid = r.json()["id"]
    assert r.json()["owner_id"] == user["id"]

    r = client.put(f"/playlists/{pid}/movies/{m2}", headers=h)
    assert r.status_code == 200 and len(r.json()["movies"]) == 2
    r = client.delete(f"/playlists/{pid}/movies/{m1}", headers=h)
    assert [m["id"] for m in r.json()["movies"]] == [m2]
    assert client.patch(f"/playlists/{pid}", json={"name": "Новое"}, headers=h).json()["name"] == "Новое"

    # чужой пользователь не может менять, но может сохранить
    other = "o" + uuid.uuid4().hex[:8]
    client.post("/register", json={"username": other, "email": f"{other}@ex.com", "password": "secret1"})
    ho = auth(login(other, "secret1"))
    assert client.delete(f"/playlists/{pid}", headers=ho).status_code == 403
    assert client.put(f"/playlists/{pid}/save", headers=ho).status_code == 204
    assert [p["id"] for p in client.get("/playlists/saved", headers=ho).json()] == [pid]
    assert client.delete(f"/playlists/{pid}/save", headers=ho).status_code == 204
    assert client.delete(f"/playlists/{pid}/save", headers=ho).status_code == 404
    assert client.put("/playlists/999999/save", headers=ho).status_code == 404

    assert client.delete(f"/playlists/{pid}", headers=h).status_code == 204
    assert client.get(f"/playlists/{pid}", headers=h).status_code == 404


def test_admin_users(admin, user):
    assert client.get("/users", headers=auth(user["token"])).status_code == 403
    assert client.get("/users", headers=auth(admin)).status_code == 200
    r = client.patch(f"/users/{user['id']}/role", json={"role": "admin"}, headers=auth(admin))
    assert r.json()["role"] == "admin"
    client.patch(f"/users/{user['id']}/role", json={"role": "user"}, headers=auth(admin))


def test_swagger_form_token(user):
    r = client.post("/token", data={"username": user["name"], "password": "secret1"})
    assert r.status_code == 200 and r.json()["token_type"] == "bearer"


def test_expired_token():
    import jwt, datetime
    from app.config import SECRET_KEY, JWT_ALGORITHM
    t = jwt.encode({"sub": "1", "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=5)},
                   SECRET_KEY, algorithm=JWT_ALGORITHM)
    assert client.get("/me", headers=auth(t)).status_code == 401
