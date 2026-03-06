"""ModelServe backend — Settings via pydantic-settings."""

import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # HuggingFace
    hf_token: str = ""
    hf_max_models: int = 5000

    # Database
    database_url: str = (
        "postgresql+asyncpg://modelserve:changeme@localhost:5432/modelserve"
    )

    # Security
    secret_key: str = "change-me-in-production-min-32-chars!!"
    access_token_expire_minutes: int = 1440

    # vLLM
    vllm_host: str = "localhost"
    # Port range used when allocating a port for a new vLLM container.
    # Each concurrently-served model gets its own port from this range.
    vllm_port_start: int = 8080
    vllm_port_end: int = 8180
    # GPU backend for spawned vLLM containers — always rocm for this deployment.
    vllm_gpu_type: str = "rocm"
    # Official prebuilt vLLM image for AMD ROCm.
    # See: https://docs.vllm.ai/en/stable/deployment/docker/#amd-rocm
    vllm_rocm_image: str = "vllm/vllm-openai-rocm:latest"

    # App
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    cors_origin_regex: str | None = None
    cors_allow_credentials: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str] | None) -> list[str]:
        """Parse CORS origins from CSV or JSON-like env values."""
        if value is None:
            return ["*"]

        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return ["*"]

            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    parsed = None
                if isinstance(parsed, list):
                    return [
                        str(origin).strip() for origin in parsed if str(origin).strip()
                    ]

            return [origin.strip() for origin in raw.split(",") if origin.strip()]

        return value
