from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

# Settings Class
class Settings(BaseSettings):

    # JWT SECRET KEY
    SECRET_KEY: str

    # JWT Algorithm
    ALGORITHM: str="HS256"

    # Access Token Expiration
    ACCESS_TOKEN_EXPIRE_MINUTES: int=30

    # Refresh Token Expiration
    REFRESH_TOKEN_EXPIRE_DAYS: int=7

    # Email Verification Secret
    EMAIL_SECRET_KEY: str

    # Default Admin Email
    # Used for Role Based Access.
    ADMIN_EMAIL: str

    # Tell Pydantic to read .env file

    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8",extra="ignore")

# Create Settings Object
settings = Settings()