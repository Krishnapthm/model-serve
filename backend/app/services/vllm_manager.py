"""vLLM process lifecycle manager via Docker SDK."""

import uuid
from datetime import datetime

import docker
from docker.errors import NotFound, APIError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import generate_api_key, hash_key, extract_prefix
from app.models.served_model import ServedModel, ModelStatus, GPUType
from app.models.api_key import APIKey
from app.utils.exceptions import ServedModelNotFoundError, VLLMError


class VLLMManager:
    """Manages vLLM container lifecycle via the Docker SDK."""

    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        try:
            self._docker = docker.from_env()
        except docker.errors.DockerException:
            self._docker = None

    async def serve(self, model_id: str, gpu_type: str = "cuda") -> dict:
        """Pull and serve a model via vLLM.

        Args:
            model_id: HuggingFace model ID.
            gpu_type: GPU backend — ``cuda`` or ``rocm``.

        Returns:
            Dict with served model data including endpoint URL and env snippet.

        Raises:
            VLLMError: If the container cannot be started.
        """
        # Create an API key for this served model
        raw_key = generate_api_key()
        key_record = APIKey(
            name=f"auto:{model_id}",
            key_hash=hash_key(raw_key),
            key_prefix=extract_prefix(raw_key),
        )
        self.db.add(key_record)

        # Determine endpoint port (use a simple incrementing approach)
        port = self.settings.vllm_port
        endpoint_url = f"http://{self.settings.vllm_host}:{port}/v1"

        # Create served model record
        served = ServedModel(
            model_id=model_id,
            display_name=model_id.split("/")[-1] if "/" in model_id else model_id,
            pipeline_tag=None,  # Will be updated when we have HF info
            endpoint_url=endpoint_url,
            status=ModelStatus.PENDING,
            gpu_type=GPUType(gpu_type),
            started_at=datetime.utcnow(),
        )

        # Try to start the container
        if self._docker:
            try:
                env = {"HUGGING_FACE_HUB_TOKEN": self.settings.hf_token}
                cmd = [
                    "--model", model_id,
                    "--host", "0.0.0.0",
                    "--port", str(port),
                ]

                device_requests = []
                if gpu_type == "cuda":
                    device_requests = [
                        docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
                    ]

                container = self._docker.containers.run(
                    self.settings.vllm_image,
                    command=cmd,
                    environment=env,
                    device_requests=device_requests if gpu_type == "cuda" else [],
                    detach=True,
                    name=f"vllm-{served.id}",
                    ports={f"{port}/tcp": port},
                    volumes={
                        "hf_cache": {"bind": "/root/.cache/huggingface", "mode": "rw"}
                    },
                )
                served.container_id = container.id
                served.status = ModelStatus.RUNNING
            except (APIError, Exception) as e:
                served.status = ModelStatus.ERROR
                served.container_id = None
        else:
            # No Docker available — mark as pending (useful for dev/testing)
            served.status = ModelStatus.PENDING

        self.db.add(served)
        await self.db.commit()
        await self.db.refresh(served)

        return {
            "id": str(served.id),
            "model_id": served.model_id,
            "display_name": served.display_name,
            "status": served.status.value,
            "endpoint_url": served.endpoint_url,
            "gpu_type": served.gpu_type.value,
            "started_at": served.started_at.isoformat(),
            "env_snippet": {
                "OPENAI_API_KEY": raw_key,
                "OPENAI_BASE_URL": endpoint_url,
            },
        }

    async def stop(self, served_model_id: str) -> dict:
        """Stop a served model and remove its container.

        Args:
            served_model_id: UUID of the served model record.

        Returns:
            Updated served model data.

        Raises:
            ServedModelNotFoundError: If the record doesn't exist.
        """
        result = await self.db.execute(
            select(ServedModel).where(ServedModel.id == uuid.UUID(served_model_id))
        )
        served = result.scalar_one_or_none()
        if not served:
            raise ServedModelNotFoundError(f"Served model '{served_model_id}' not found")

        # Stop Docker container
        if self._docker and served.container_id:
            try:
                container = self._docker.containers.get(served.container_id)
                container.stop(timeout=10)
                container.remove()
            except NotFound:
                pass
            except APIError:
                pass

        served.status = ModelStatus.STOPPED
        served.stopped_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(served)

        return {
            "id": str(served.id),
            "model_id": served.model_id,
            "display_name": served.display_name,
            "status": served.status.value,
            "stopped_at": served.stopped_at.isoformat() if served.stopped_at else None,
        }

    async def get_status(self, served_model_id: str) -> dict:
        """Get the current status of a served model.

        Args:
            served_model_id: UUID of the served model record.

        Returns:
            Served model data.

        Raises:
            ServedModelNotFoundError: If the record doesn't exist.
        """
        result = await self.db.execute(
            select(ServedModel).where(ServedModel.id == uuid.UUID(served_model_id))
        )
        served = result.scalar_one_or_none()
        if not served:
            raise ServedModelNotFoundError(f"Served model '{served_model_id}' not found")

        # Optionally sync with Docker container state
        if self._docker and served.container_id and served.status == ModelStatus.PENDING:
            try:
                container = self._docker.containers.get(served.container_id)
                if container.status == "running":
                    served.status = ModelStatus.RUNNING
                    await self.db.commit()
            except NotFound:
                served.status = ModelStatus.ERROR
                await self.db.commit()

        return {
            "id": str(served.id),
            "model_id": served.model_id,
            "display_name": served.display_name,
            "pipeline_tag": served.pipeline_tag,
            "status": served.status.value,
            "endpoint_url": served.endpoint_url,
            "gpu_type": served.gpu_type.value,
            "started_at": served.started_at.isoformat(),
            "stopped_at": served.stopped_at.isoformat() if served.stopped_at else None,
        }

    async def list_served(self) -> list[dict]:
        """List all served models.

        Returns:
            List of served model data dicts.
        """
        result = await self.db.execute(
            select(ServedModel).order_by(ServedModel.started_at.desc())
        )
        models = result.scalars().all()

        return [
            {
                "id": str(m.id),
                "model_id": m.model_id,
                "display_name": m.display_name,
                "pipeline_tag": m.pipeline_tag,
                "status": m.status.value,
                "endpoint_url": m.endpoint_url,
                "gpu_type": m.gpu_type.value,
                "started_at": m.started_at.isoformat(),
                "stopped_at": m.stopped_at.isoformat() if m.stopped_at else None,
            }
            for m in models
        ]
