from fastapi import APIRouter, status

from app import schemas
from app.deps import CurrentUser, LibrarySvc

router = APIRouter(prefix="/library", tags=["library"])


@router.get("", response_model=list[schemas.MovieOut])
def my_library(user: CurrentUser, svc: LibrarySvc):
    return svc.list_all(user)


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def add_to_library(data: schemas.LibraryAdd, user: CurrentUser, svc: LibrarySvc):
    svc.add(user, data.movie_id)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_library(movie_id: int, user: CurrentUser, svc: LibrarySvc):
    svc.remove(user, movie_id)
