"""vLLM model registry — reads model config from environment, checks health."""

import logging

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)

# Timeout for vLLM health probe
_HEALTH_TIMEOUT = 3.0


class VLLMManager:
    """Reads configured model slots and checks vLLM instance health.

    Models are declared at deploy time via environment variables
    (``VLLM_MODEL_1`` … ``VLLM_MODEL_4``).  vLLM containers are managed
    by Docker Compose — this service only *reads* the config and probes
    each instance's ``/health`` endpoint.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._models = settings.configured_models()

    async def list_models(self) -> list[dict]:
        """Return all configured models with live health status.

        Returns:
            List of model dicts, each containing ``slot``, ``model_id``,
            ``display_name``, ``endpoint_url``, ``status``, and
            ``env_snippet``.
        """
        results: list[dict] = []
        for m in self._models:
            healthy = await self._check_health(str(m["endpoint_url"]))
            results.append(self._build_model_response(m, healthy))
        return results

    async def get_model(self, slot: int) -> dict | None:
        """Return a single model by slot number with health status.

        Args:
            slot: The 1-based model slot (1–4).

        Returns:
            Model dict or ``None`` if the slot is not configured.
        """
        for m in self._models:
            if m["slot"] == slot:
                healthy = await self._check_health(str(m["endpoint_url"]))
                return self._build_model_response(m, healthy)
        return None

    def _build_model_response(self, model: dict, healthy: bool) -> dict:
        """Build a response dict for a single model.

        Args:
            model: Raw model config from ``Settings.configured_models()``.
            healthy: Whether the vLLM ``/health`` probe succeeded.

        Returns:
            Serialisable dict suitable for JSON responses.
        """
        endpoint_url = str(model["endpoint_url"])
        env_snippet: dict[str, str] = {"OPENAI_BASE_URL": endpoint_url}
        if self.settings.vllm_api_key:
            env_snippet["OPENAI_API_KEY"] = self.settings.vllm_api_key

        return {
            "slot": model["slot"],
            "model_id": model["model_id"],
            "display_name": model["display_name"],
            "endpoint_url": endpoint_url,
            "status": "running" if healthy else "loading",
            "env_snippet": env_snippet,
        }

    async def _check_health(self, endpoint_url: str) -> bool:
        """Probe the vLLM ``/health`` endpoint.

        Args:
            endpoint_url: The model's base URL (e.g. ``http://vllm-1:8080/v1``).

        Returns:
            ``True`` when the instance responds 200, ``False`` otherwise.
        """
        # endpoint_url ends with /v1 — health is at the root
        base_url = endpoint_url.rstrip("/").removesuffix("/v1")
        health_url = f"{base_url}/health"
        try:
            async with httpx.AsyncClient(timeout=_HEALTH_TIMEOUT) as client:
                resp = await client.get(health_url)
                return resp.status_code == 200
        except (httpx.RequestError, httpx.HTTPStatusError):
            return False
