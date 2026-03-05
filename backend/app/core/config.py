"""ModelServe backend — Settings via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # HuggingFace
    hf_token: str = ""
    hf_max_models: int = 5000

    # Database
    database_url: str = "postgresql+asyncpg://modelserve:changeme@localhost:5432/modelserve"

    # Security
    secret_key: str = "change-me-in-production-min-32-chars!!"

    # vLLM
    vllm_host: str = "localhost"
    vllm_port: int = 8080
    vllm_image: str = "vllm/vllm-openai:latest"

    # App
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
