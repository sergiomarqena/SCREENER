from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"
    mexc_base_url: str = "https://contract.mexc.com/api/v1"
    database_url: str | None = None
    poll_interval_seconds: int = 8
    snapshot_interval_seconds: int = 60
    snapshot_retention_days: int = 7
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


settings = Settings()
