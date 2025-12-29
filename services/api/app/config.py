from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Quilent API"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://quilent:quilent@localhost:5432/quilent"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        # Railway uses postgres:// but SQLAlchemy needs postgresql://
        if v and v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        return v

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"  # noqa: S105
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI
    ANTHROPIC_API_KEY: str = ""

    # External APIs
    SAM_GOV_API_KEY: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Email
    RESEND_API_KEY: str = ""

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS - can be set via CORS_ORIGINS env var as comma-separated list
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "https://govbids.quilent.ai",
        "https://quilent.ai",
        "https://govbids-production.up.railway.app",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        # Allow comma-separated string from env var
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
