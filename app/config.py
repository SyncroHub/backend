from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")

APP_ENV = getenv("APP_ENV", "development")


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = getenv("APP_NAME", "SyncroHUB API")
    app_env: str = APP_ENV
    app_host: str = getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(getenv("APP_PORT", "8000"))
    frontend_dir: Path = PROJECT_DIR / "app-cnsonlineprd"
    data_provider: str = getenv(
        "DATA_PROVIDER",
        "totvs" if APP_ENV == "production" else "demo",
    )
    totvs_proxy_url: str | None = getenv("TOTVS_PROXY_URL")
    totvs_proxy_api_key: str | None = getenv("TOTVS_PROXY_API_KEY")
    totvs_proxy_timeout: float = float(getenv("TOTVS_PROXY_TIMEOUT", "15"))
    database_url: str = getenv(
        "DATABASE_URL",
        "postgresql+psycopg://syncrohub:syncrohub@localhost:5432/syncrohub",
    )
    redis_url: str | None = getenv("REDIS_URL", "redis://localhost:6379/0")
    jwt_secret: str = getenv(
        "JWT_SECRET",
        "development-only-change-this-32-byte-secret",
    )
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = int(getenv("ACCESS_TOKEN_MINUTES", "15"))
    refresh_token_days: int = int(getenv("REFRESH_TOKEN_DAYS", "7"))
    bcrypt_rounds: int = int(getenv("BCRYPT_ROUNDS", "12"))
    auto_create_schema: bool = getenv("AUTO_CREATE_SCHEMA", "true").lower() in {
        "1",
        "true",
        "yes",
    }
    login_rate_limit: int = int(getenv("LOGIN_RATE_LIMIT", "5"))
    login_rate_window_seconds: int = int(getenv("LOGIN_RATE_WINDOW_SECONDS", "60"))


settings = Settings()
