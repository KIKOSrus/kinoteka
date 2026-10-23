from fastapi import APIRouter, status

from app import schemas
from app.deps import AdminUser, UserSvc

router = APIRouter(prefix="/users", tags=["users (admin)"])


@router.get("", response_model=list[schemas.UserOut])
def list_users(_: AdminUser, svc: UserSvc):
    return svc.list_all()


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, _: AdminUser, svc: UserSvc):
    return svc.get(user_id)


@router.patch("/{user_id}/role", response_model=schemas.UserOut)
def set_role(user_id: int, data: schemas.UserRoleUpdate, _: AdminUser, svc: UserSvc):
    return svc.set_role(user_id, data.role)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, _: AdminUser, svc: UserSvc):
    svc.delete(user_id)
