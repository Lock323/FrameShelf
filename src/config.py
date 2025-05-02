from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    # JWT settings
    JWT_SECRET: str = Field(alias='JWT_SECRET')
    JWT_ALGORITHM: str = Field(alias='JWT_ALGORITHM')

    # API settings
    API_KEY: str = Field(alias='API_KEY')

    # Proxy settings
    PROXY_USER: str = Field(alias='PROXY_USER')
    PROXY_PASSWORD: str = Field(alias='PROXY_PASSWORD')
    PROXY_HOST: str = Field(alias='PROXY_HOST')
    PROXY_PORT: str = Field(alias='PROXY_PORT')

    # SMTP settings
    SMTP_USER: str = Field(alias='SMTP_USER')
    SMTP_PASSWORD: str = Field(alias='SMTP_PASSWORD')
    SMTP_HOST: str = Field(alias='SMTP_HOST')
    SMTP_PORT: str = Field(alias='SMTP_PORT')

    # Redis settings
    REDIS_HOST: str = Field(alias='REDIS_HOST')
    REDIS_PORT: str = Field(alias='REDIS_PORT')
    REDIS_PASSWORD: str = Field(alias='REDIS_PASSWORD')

    # Database settings
    DB_USER: str = Field(alias='POSTGRES_USER')
    DB_PASSWORD: str = Field(alias='POSTGRES_PASSWORD')
    DB_HOST: str = Field(alias='POSTGRES_HOST')
    DB_PORT: str = Field(alias='POSTGRES_PORT')
    DB_NAME: str = Field(alias='POSTGRES_DB')

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def proxy_url(self):
        return f"http://{self.PROXY_USER}:{self.PROXY_PASSWORD}@{self.PROXY_HOST}:{self.PROXY_PORT}"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )


settings = Settings()
