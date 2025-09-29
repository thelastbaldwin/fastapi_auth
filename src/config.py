from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 3
    user_token_algorithm: str = "HS256"
    model_config=SettingsConfigDict(env_file=".env")


settings = Settings()