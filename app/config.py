from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Email settings
    EMAIL_ADDRESS: str = "baxronovasror77@gmail.com"
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_PASSWORD: str
    REDIS_URL: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"


settings = Settings()
