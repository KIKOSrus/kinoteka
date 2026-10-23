class DomainError(Exception):
    """Базовая ошибка бизнес-логики; превращается в HTTP-ответ в main.py."""

    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class AuthError(DomainError):
    status_code = 401


class ForbiddenError(DomainError):
    status_code = 403
