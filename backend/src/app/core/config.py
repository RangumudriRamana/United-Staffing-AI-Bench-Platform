from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore",)

    project_name: str = Field(default="United Staffing AI Bench Platform", alias="PROJECT_NAME",)

    environment: str = Field(default="development", alias="PROJECT_ENV",)

    debug: bool = Field(default=True, alias="PROJECT_DEBUG",)

    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST",)

    backend_port: int = Field(default=8000, alias="BACKEND_PORT",)

    database_url: str = Field(alias="DATABASE_URL",)

    database_echo: bool = Field(default=False, alias="DATABASE_ECHO",)

    jwt_secret_key: str = Field(alias="SECRET_KEY",)

    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM",)

    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES",)

    initial_admin_email: str = Field(alias="INITIAL_ADMIN_EMAIL",)

    initial_admin_password: str = Field(alias="INITIAL_ADMIN_PASSWORD",)

    initial_admin_first_name: str = Field(alias="INITIAL_ADMIN_FIRST_NAME",)

    initial_admin_last_name: str = Field(alias="INITIAL_ADMIN_LAST_NAME",)

@lru_cache
def get_settings() -> Settings:
    return Settings()