from pydantic import BaseSettings, PostgresDsn, AnyUrl
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    BOT_TOKEN: str
    GITHUB_ORGANIZATION_TOKEN: str

    class Config:
        """Pydantic BaseSettings config"""
        case_sensitive = True
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
