from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    DATABASE_URL: str = "sqlite:///./app.db"
    OTLP_ENDPOINT: str


config = Config()
