import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    secret_key: str = os.getenv("SECRET_KEY")
    db_url: str = os.getenv("DB_URL")
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 3
    user_token_algorithm: str = "HS256"

settings = Settings()

@lru_cache
def get_settings():
    return settings