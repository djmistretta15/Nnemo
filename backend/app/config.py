"""
Configuration management for Mnemo platform
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = "postgresql://mnemo:mnemo_password@localhost:5432/mnemo_db"

    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""

    # Crypto
    ETH_RPC_URL: str = ""
    SOL_RPC_URL: str = ""

    # Platform
    PLATFORM_FEE_PERCENT: float = 5.0
    MIN_NODE_HEARTBEAT_SEC: int = 30
    MAX_NODE_HEARTBEAT_SEC: int = 120
    CONTRACT_SETTLEMENT_TIMEOUT_SEC: int = 3600

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
