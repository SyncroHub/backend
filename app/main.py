from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routers import access_types, auth, users


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_schema:
        Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    if not settings.frontend_dir.is_dir():
        raise RuntimeError(f"Frontend não encontrado em: {settings.frontend_dir}")

    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Backend Python do SyncroHUB.",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/api/health", tags=["infra"])
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "application": settings.app_name,
            "environment": settings.app_env,
        }

    application.include_router(auth.router)
    application.include_router(users.router)
    application.include_router(access_types.router)

    @application.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(settings.frontend_dir / "login.html")

    @application.get("/login", include_in_schema=False)
    async def login() -> FileResponse:
        return FileResponse(settings.frontend_dir / "login.html")

    @application.get("/painel", include_in_schema=False)
    async def painel() -> FileResponse:
        return FileResponse(settings.frontend_dir / "painel.html")

    @application.get("/pdv", include_in_schema=False)
    async def pdv() -> FileResponse:
        return FileResponse(settings.frontend_dir / "pdv.html")

    application.mount(
        "/",
        StaticFiles(directory=settings.frontend_dir, html=True),
        name="frontend",
    )

    return application


app = create_app()
