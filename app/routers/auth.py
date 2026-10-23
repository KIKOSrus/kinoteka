from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app import schemas
from app.deps import AuthSvc, CurrentUser, UserSvc

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(data: schemas.UserRegister, svc: AuthSvc):
    return svc.register(data)


@router.post("/login", response_model=schemas.Token)
def login(data: schemas.UserLogin, svc: AuthSvc):
    """Вход по JSON {username, password}. Возвращает JWT."""
    return svc.login(data.username, data.password)


@router.post("/token", response_model=schemas.Token, include_in_schema=False)
def token(form: Annotated[OAuth2PasswordRequestForm, Depends()], svc: AuthSvc):
    """Тот же вход, но в form-формате — для кнопки Authorize в Swagger UI."""
    return svc.login(form.username, form.password)


@router.get("/me", response_model=schemas.UserOut)
def me(user: CurrentUser):
    return user


@router.patch("/me", response_model=schemas.UserOut)
def update_me(data: schemas.UserUpdate, user: CurrentUser, svc: UserSvc):
    return svc.update_email(user.id, data.email)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(user: CurrentUser, svc: UserSvc):
    svc.delete(user.id)
