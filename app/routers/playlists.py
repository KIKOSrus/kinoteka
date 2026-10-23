from fastapi import APIRouter, status

from app import schemas
from app.deps import CurrentUser, PlaylistSvc

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("", response_model=list[schemas.PlaylistOut])
def list_playlists(_: CurrentUser, svc: PlaylistSvc, owner_id: int | None = None):
    return svc.list_all(owner_id)


@router.post("", response_model=schemas.PlaylistOut, status_code=status.HTTP_201_CREATED)
def create_playlist(data: schemas.PlaylistCreate, user: CurrentUser, svc: PlaylistSvc):
    return svc.create(user, data.name, data.movie_ids)


# ВАЖНО: /saved объявлен раньше /{playlist_id}, иначе "saved" попытаются разобрать как int
@router.get("/saved", response_model=list[schemas.PlaylistOut])
def saved_playlists(user: CurrentUser, svc: PlaylistSvc):
    return svc.saved(user)


@router.get("/{playlist_id}", response_model=schemas.PlaylistOut)
def get_playlist(playlist_id: int, _: CurrentUser, svc: PlaylistSvc):
    return svc.get(playlist_id)


@router.patch("/{playlist_id}", response_model=schemas.PlaylistOut)
def rename_playlist(playlist_id: int, data: schemas.PlaylistRename, user: CurrentUser, svc: PlaylistSvc):
    return svc.rename(playlist_id, user, data.name)


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist(playlist_id: int, user: CurrentUser, svc: PlaylistSvc):
    svc.delete(playlist_id, user)


@router.put("/{playlist_id}/movies/{movie_id}", response_model=schemas.PlaylistOut)
def add_movie(playlist_id: int, movie_id: int, user: CurrentUser, svc: PlaylistSvc):
    return svc.add_movie(playlist_id, user, movie_id)


@router.delete("/{playlist_id}/movies/{movie_id}", response_model=schemas.PlaylistOut)
def remove_movie(playlist_id: int, movie_id: int, user: CurrentUser, svc: PlaylistSvc):
    return svc.remove_movie(playlist_id, user, movie_id)


@router.put("/{playlist_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def save_playlist(playlist_id: int, user: CurrentUser, svc: PlaylistSvc):
    svc.save(user, playlist_id)


@router.delete("/{playlist_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def unsave_playlist(playlist_id: int, user: CurrentUser, svc: PlaylistSvc):
    svc.unsave(user, playlist_id)
