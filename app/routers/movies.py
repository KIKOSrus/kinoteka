from fastapi import APIRouter, Depends, Query, status

from app import schemas
from app.deps import AdminUser, GenreSvc, MovieSvc, get_current_user

# Чтение каталога — для любого авторизованного пользователя,
# изменение — только для администратора.
router = APIRouter(tags=["movies"])


@router.get("/movies", response_model=list[schemas.MovieOut], dependencies=[Depends(get_current_user)])
def list_movies(
    svc: MovieSvc,
    genre: str | None = Query(None, description="Фильтр по названию жанра"),
    search: str | None = Query(None, description="Поиск по части названия"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return svc.list_all(genre, search, skip, limit)


@router.get("/movies/{movie_id}", response_model=schemas.MovieOut, dependencies=[Depends(get_current_user)])
def get_movie(movie_id: int, svc: MovieSvc):
    return svc.get(movie_id)


@router.post("/movies", response_model=schemas.MovieOut, status_code=status.HTTP_201_CREATED)
def create_movie(data: schemas.MovieCreate, _: AdminUser, svc: MovieSvc):
    return svc.create(data)


@router.patch("/movies/{movie_id}", response_model=schemas.MovieOut)
def update_movie(movie_id: int, data: schemas.MovieUpdate, _: AdminUser, svc: MovieSvc):
    return svc.update(movie_id, data)


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, _: AdminUser, svc: MovieSvc):
    svc.delete(movie_id)


@router.get("/genres", response_model=list[schemas.GenreOut], dependencies=[Depends(get_current_user)])
def list_genres(svc: GenreSvc):
    return svc.list_all()


@router.post("/genres", response_model=schemas.GenreOut, status_code=status.HTTP_201_CREATED)
def create_genre(data: schemas.GenreCreate, _: AdminUser, svc: GenreSvc):
    return svc.create(data.name)


@router.delete("/genres/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_genre(genre_id: int, _: AdminUser, svc: GenreSvc):
    svc.delete(genre_id)
