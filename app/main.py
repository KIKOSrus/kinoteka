from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import AuthError, DomainError
from app.routers import auth, library, movies, playlists, users

app = FastAPI(
    title="Кинотека API",
    version="2.0.0",
    description="REST API для каталога фильмов, личных библиотек и плейлистов. Аутентификация — JWT (Bearer).",
)


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, exc: DomainError):
    headers = {"WWW-Authenticate": "Bearer"} if isinstance(exc, AuthError) else None
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=headers)


@app.get("/health", tags=["service"])
def health():
    return {"status": "ok"}


for r in (auth.router, users.router, movies.router, library.router, playlists.router):
    app.include_router(r)
