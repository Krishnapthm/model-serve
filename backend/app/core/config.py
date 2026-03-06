"""ModelServe backend — Settings via pydantic-settings."""

import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

MAX_VLLM_SLOTS = 4


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = (
        "postgresql+asyncpg://modelserve:changeme@localhost:5432/modelserve"
    )

    # Security
    secret_key: str = "change-me-in-production-min-32-chars!!"
    access_token_expire_minutes: int = 1440

    # vLLM — model slots (max 4). Set in .env to enable each slot.
    vllm_model_1: str = ""
    vllm_model_2: str = ""
    vllm_model_3: str = ""
    vllm_model_4: str = ""

    # Host used to construct external endpoint URLs for served models.
    # Inside Compose this is the Docker host; outside it defaults to localhost.
    vllm_host: str = "localhost"

    # First external port for vLLM slots.  Slot N listens on
    # ``vllm_base_port + (N - 1)`` e.g. 8081, 8082, 8083, 8084.
    vllm_base_port: int = 8081

    # Optional shared API key passed to every vLLM instance via ``--api-key``.
    # Clients must send this as ``Authorization: Bearer <key>``.
    vllm_api_key: str = ""

    # Official vLLM ROCm image.
    # https://hub.docker.com/r/vllm/vllm-openai-rocm/tags
    vllm_rocm_image: str = "vllm/vllm-openai-rocm:latest"

    # HuggingFace token — used by vLLM containers to pull gated models.
    hf_token: str = ""

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

    def configured_models(self) -> list[dict[str, str | int]]:
        """Return the list of configured vLLM model slots.

        Each entry contains ``slot``, ``model_id``, ``display_name``, and
        ``endpoint_url``.  Only slots with a non-empty model ID are returned.
        """
        models: list[dict[str, str | int]] = []
        for i in range(1, MAX_VLLM_SLOTS + 1):
            model_id: str = getattr(self, f"vllm_model_{i}", "")
            if not model_id:
                continue
            port = self.vllm_base_port + (i - 1)
            models.append(
                {
                    "slot": i,
                    "model_id": model_id,
                    "display_name": (
                        model_id.split("/")[-1] if "/" in model_id else model_id
                    ),
                    "endpoint_url": f"http://{self.vllm_host}:{port}/v1",
                }
            )
        return models
