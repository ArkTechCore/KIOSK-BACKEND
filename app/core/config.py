from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Kiosk Backend"
    ENV: str = "dev"

    # Local dev default (SQLite). On Render, set DATABASE_URL to Postgres internal URL.
    DATABASE_URL: str = "sqlite:///./dev.db"

    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60 * 24  # 1 day

    # For creating the first platform admin safely
    ADMIN_BOOTSTRAP_KEY: str = "change-this"

    class Config:
        env_file = ".env"


settings = Settings()
