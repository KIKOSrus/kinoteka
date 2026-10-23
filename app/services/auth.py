from app import schemas
from app.exceptions import AuthError, ConflictError, NotFoundError
from app.models import User
from app.repositories import UserRepository
from app.security import create_access_token, verify_password


class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, data: schemas.UserRegister) -> User:
        if self.users.get_by_username(data.username):
            raise ConflictError("Пользователь с таким именем уже существует")
        if self.users.get_by_email(data.email):
            raise ConflictError("Пользователь с таким email уже существует")
        # роль при регистрации всегда 'user'; админа назначает другой админ
        return self.users.create(data.username, data.email, data.password, role="user")

    def login(self, username: str, password: str) -> schemas.Token:
        user = self.users.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("Неверное имя пользователя или пароль")
        token, expires_in = create_access_token(user.id, user.role)
        return schemas.Token(access_token=token, expires_in=expires_in)


class UserService:
    def __init__(self, users: UserRepository):
        self.users = users

    def get(self, user_id: int) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user

    def list_all(self) -> list[User]:
        return self.users.list_all()

    def update_email(self, user_id: int, email: str) -> User:
        existing = self.users.get_by_email(email)
        if existing and existing.id != user_id:
            raise ConflictError("Этот email уже занят")
        user = self.users.update_email(user_id, email)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user

    def set_role(self, user_id: int, role: str) -> User:
        user = self.users.set_role(user_id, role)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user

    def delete(self, user_id: int) -> None:
        if not self.users.delete(user_id):
            raise NotFoundError("Пользователь не найден")
