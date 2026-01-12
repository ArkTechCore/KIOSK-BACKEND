from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Kiosk Backend"
    ENV: str = "dev"
    DATABASE_URL: str = "sqlite:///./dev.db"
    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60 * 24

    class Config:
        env_file = ".env"

settings = Settings()
