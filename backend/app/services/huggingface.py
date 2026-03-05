"""HuggingFace Hub API client with in-memory caching."""

import re
import time
from urllib.parse import urljoin

import httpx

from app.core.config import Settings
from app.schemas.models import ModelSummary, ModelDetail

# Pipeline tag → display label + badge color
CATEGORY_MAP: dict[str, dict[str, str]] = {
    "text-generation": {"label": "LLM", "color": "blue"},
    "feature-extraction": {"label": "Text Embedding", "color": "purple"},
    "text-to-image": {"label": "Image Generation", "color": "pink"},
    "text-to-video": {"label": "Video Generation", "color": "orange"},
    "automatic-speech-recognition": {"label": "Speech-to-Text", "color": "green"},
    "image-to-text": {"label": "Vision-Language", "color": "cyan"},
}

# Cache TTL in seconds
CACHE_TTL = 300  # 5 minutes

HF_API_BASE = "https://huggingface.co/api"


class HuggingFaceService:
    """Wraps the HuggingFace Hub API for model discovery."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {settings.hf_token}"} if settings.hf_token else {},
            timeout=30.0,
        )
        self._cache: dict[str, tuple[float, list]] = {}

    def _extract_next_url(self, link_header: str | None) -> str | None:
        """Extract the next page URL from an RFC5988 Link header."""
        if not link_header:
            return None
        match = re.search(r'<([^>]+)>\s*;\s*rel="next"', link_header)
        if not match:
            return None
        url = match.group(1)
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return urljoin(HF_API_BASE, url)

    def _get_label_and_color(self, pipeline_tag: str | None) -> tuple[str, str]:
        """Map a pipeline tag to a display label and badge color.

        Args:
            pipeline_tag: HuggingFace pipeline tag string.

        Returns:
            Tuple of (label, color).
        """
        if pipeline_tag and pipeline_tag in CATEGORY_MAP:
            info = CATEGORY_MAP[pipeline_tag]
            return info["label"], info["color"]
        return "Custom", "gray"

    async def list_models(
        self,
        category: str | None = None,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ModelSummary], int]:
        """Fetch models from HF Hub, optionally filtered by pipeline tag.

        Args:
            category: Pipeline tag to filter by (e.g. ``text-generation``).
            query: Search query string.
            page: Page number (1-indexed).
            page_size: Number of results per page.

        Returns:
            Tuple of (list of model summaries, total count).
        """
        cache_key = f"list:{category}:{query}"

        # Check cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if time.time() - cached_time < CACHE_TTL:
                # Paginate cached data
                total = len(cached_data)
                start = (page - 1) * page_size
                return cached_data[start : start + page_size], total

        # Build HF API request (paginate through all pages and cache once).
        params: dict[str, str | int] = {"limit": 100, "sort": "downloads", "direction": -1}
        if category:
            params["pipeline_tag"] = category
        if query:
            params["search"] = query

        max_models = self.settings.hf_max_models
        next_url: str | None = f"{HF_API_BASE}/models"
        next_params: dict[str, str | int] | None = params
        models: list[ModelSummary] = []

        while next_url:
            resp = await self._client.get(next_url, params=next_params)
            resp.raise_for_status()
            raw_models = resp.json()

            for m in raw_models:
                model_id = m.get("modelId")
                if not model_id:
                    continue

                pipeline_tag = m.get("pipeline_tag")
                label, color = self._get_label_and_color(pipeline_tag)
                models.append(
                    ModelSummary(
                        id=model_id,
                        name=model_id.split("/")[-1] if "/" in model_id else model_id,
                        pipeline_tag=pipeline_tag,
                        description=m.get("description", ""),
                        downloads=m.get("downloads", 0),
                        likes=m.get("likes", 0),
                        label=label,
                        badge_color=color,
                    )
                )

                if max_models > 0 and len(models) >= max_models:
                    next_url = None
                    break

            if next_url is None:
                break

            next_url = self._extract_next_url(resp.headers.get("Link"))
            next_params = None

        # Cache the full result
        self._cache[cache_key] = (time.time(), models)

        # Paginate
        total = len(models)
        start = (page - 1) * page_size
        return models[start : start + page_size], total

    async def get_model(self, model_id: str) -> ModelDetail:
        """Fetch detailed info for a single model.

        Args:
            model_id: HuggingFace model ID (e.g. ``mistralai/Mistral-7B-Instruct-v0.2``).

        Returns:
            Detailed model information.

        Raises:
            ModelNotFoundError: If the model doesn't exist on HF.
        """
        from app.utils.exceptions import ModelNotFoundError

        resp = await self._client.get(f"{HF_API_BASE}/models/{model_id}")
        if resp.status_code == 404:
            raise ModelNotFoundError(f"Model '{model_id}' not found on HuggingFace")
        resp.raise_for_status()

        m = resp.json()
        pipeline_tag = m.get("pipeline_tag")
        label, color = self._get_label_and_color(pipeline_tag)

        return ModelDetail(
            id=m["modelId"],
            name=m["modelId"].split("/")[-1] if "/" in m["modelId"] else m["modelId"],
            pipeline_tag=pipeline_tag,
            description=m.get("description", ""),
            downloads=m.get("downloads", 0),
            likes=m.get("likes", 0),
            label=label,
            badge_color=color,
            model_card_url=f"https://huggingface.co/{model_id}",
            library_name=m.get("library_name"),
            tags=m.get("tags", []),
        )
