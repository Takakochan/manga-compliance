from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    fukidashi_api_url: str = ""
    fukidashi_api_key: str = ""
    request_timeout: float = 120
    rules_dir: Path = Path("rules")
    out_dir: Path = Path("out")


settings = Settings()
