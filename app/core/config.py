from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str 
    MAIL_PORT: int 
    MAIL_SERVER: str 
    MAIL_FROM_NAME: str
    SERVER_HOST: str 
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    database_url: str
    WEBHOOK_SECRET: str
    FRONTEND_URL:str
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env"
    )

settings = Settings()
