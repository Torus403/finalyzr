import secrets

from pydantic import MySQLDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    # Project
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Finalyzr"

    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # Database
    DB_HOST: str
    DB_PORT: int = 3306
    DB_NAME: str = ""
    DB_USER: str
    DB_PASSWORD: str

    @computed_field
    @property
    def DB_URI(self) -> MySQLDsn:
        return MultiHostUrl.build(
            scheme="mysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )


settings = Settings()
