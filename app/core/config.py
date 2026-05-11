from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RECAPTCHA_SECRET_KEY: str = ""  # ← tambah ini

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()