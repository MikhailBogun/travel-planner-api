from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    api_username: str = "admin"
    api_password: str = "secret"

    model_config = {"env_file": ".env"}


settings = Settings()
