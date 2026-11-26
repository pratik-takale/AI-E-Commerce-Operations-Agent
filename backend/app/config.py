from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI E-Commerce Agent"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # Database / Redis
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security (Day 4 मध्ये वापरू)
    SECRET_KEY: str = "change-me-in-real-use"

    # Frontend ला परवानगी (CORS), commas ने वेगळे
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()