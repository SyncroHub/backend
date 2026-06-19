from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = getenv("APP_NAME", "SyncroHUB API")
    app_env: str = getenv("APP_ENV", "development")
    app_host: str = getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(getenv("APP_PORT", "8000"))
    frontend_dir: Path = PROJECT_DIR / "app-cnsonlineprd"


settings = Settings()

