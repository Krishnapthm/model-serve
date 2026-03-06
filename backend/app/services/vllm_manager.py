"""vLLM process lifecycle manager via Docker SDK."""

import glob
import logging
import re
import uuid
from datetime import datetime

import docker
from docker.errors import NotFound, APIError
from sqlalchemy import String, cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import generate_api_key, hash_key, extract_prefix
from app.models.served_model import ServedModel, ModelStatus, GPUType
from app.models.api_key import APIKey
from app.utils.exceptions import ServedModelNotFoundError, VLLMError

logger = logging.getLogger(__name__)


def _rocm_devices() -> list[str]:
    """Return individual ROCm device paths to pass to the container.

    The Docker Python SDK's ``devices`` parameter expects *file* paths, not
    directories.  Passing ``/dev/dri`` (a directory) silently omits the GPU
    render nodes, causing vLLM to fail with "Failed to infer device type".

    We enumerate the real device files under ``/dev/dri/`` (``renderD*`` and
    ``card*``) and include ``/dev/kfd``, mirroring the flags used in the
    official vLLM ROCm Docker docs.
    """
    devices = ["/dev/kfd"]
    for pattern in ("/dev/dri/renderD*", "/dev/dri/card*"):
        devices.extend(sorted(glob.glob(pattern)))
    return devices


def _container_name(model_id: str, suffix: str = "") -> str:
    """Return a Docker-safe container name derived from the model ID.

    Replaces characters not allowed in Docker container names with ``-``.
    Adds an optional suffix (e.g. a short UUID) to resolve name conflicts.
    """
    sanitized = re.sub(r"[^a-zA-Z0-9._-]", "-", model_id)
    name = f"vllm-{sanitized}"
    return f"{name}-{suffix}" if suffix else name


class VLLMManager:
    """Manages vLLM container lifecycle via the Docker SDK."""

    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        try:
            self._docker = docker.from_env()
        except docker.errors.DockerException:
            self._docker = None

    async def _allocate_port(self) -> int:
        """Return the first free port in the configured range.

        Queries all PENDING and RUNNING served models, extracts the ports they
        are using from their ``endpoint_url``, then returns the lowest port in
        ``[vllm_port_start, vllm_port_end]`` that is not yet taken.

        Raises:
            VLLMError: When every port in the range is already occupied.
        """
        # Cast the enum column to plain text to avoid asyncpg sending
        # values with the ::modelstatus annotation, which causes
        # InvalidTextRepresentationError when the driver serialises the
        # Python enum member name rather than its value.
        result = await self.db.execute(
            select(ServedModel.endpoint_url).where(
                cast(ServedModel.status, String).in_(
                    [ModelStatus.PENDING.value, ModelStatus.RUNNING.value]
                )
            )
        )
        used_ports: set[int] = set()
        for url in result.scalars().all():
            # endpoint_url format: http://<host>:<port>/v1
            if url:
                try:
                    used_ports.add(int(url.split(":")[2].split("/")[0]))
                except (IndexError, ValueError):
                    pass

        for port in range(
            self.settings.vllm_port_start, self.settings.vllm_port_end + 1
        ):
            if port not in used_ports:
                return port

        raise VLLMError(
            f"No free port available in range "
            f"{self.settings.vllm_port_start}–{self.settings.vllm_port_end}. "
            "Stop an existing model before starting a new one."
        )

    async def serve(
        self, model_id: str, owner_id: uuid.UUID, gpu_type: str = "rocm"
    ) -> dict:
        """Pull and serve a model via vLLM (ROCm backend).

        Args:
            model_id: HuggingFace model ID.
            owner_id: User ID that owns the served model and generated key.
            gpu_type: GPU backend — always ``rocm`` for this deployment.

        Returns:
            Dict with served model data including endpoint URL and env snippet.

        Raises:
            VLLMError: If the container cannot be started.
        """
        # Create an API key for this served model
        raw_key = generate_api_key()
        key_record = APIKey(
            owner_id=owner_id,
            name=f"auto:{model_id}",
            key_hash=hash_key(raw_key),
            key_prefix=extract_prefix(raw_key),
        )
        self.db.add(key_record)

        # Allocate a free port from the configured range
        port = await self._allocate_port()
        endpoint_url = f"http://{self.settings.vllm_host}:{port}/v1"

        # Create served model record
        served = ServedModel(
            owner_id=owner_id,
            model_id=model_id,
            display_name=model_id.split("/")[-1] if "/" in model_id else model_id,
            pipeline_tag=None,  # Will be updated when we have HF info
            endpoint_url=endpoint_url,
            status=ModelStatus.PENDING,
            gpu_type=GPUType(gpu_type),
            started_at=datetime.utcnow(),
        )

        self.db.add(served)
        # Flush to generate served.id before using it as the container name.
        await self.db.flush()

        # Try to start the container
        if self._docker:
            try:
                env = {
                    "HUGGING_FACE_HUB_TOKEN": self.settings.hf_token,
                    # Suppress vLLM's Triton/ROCm driver-not-found warning;
                    # the device is explicitly set via --device rocm below.
                    "VLLM_LOGGING_LEVEL": "WARNING",
                }
                cmd = [
                    "--model",
                    model_id,
                    "--device",
                    "rocm",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    str(port),
                    "--enforce-eager",
                ]

                run_kwargs: dict = dict(
                    command=cmd,
                    environment=env,
                    ipc_mode="host",
                    detach=True,
                    name=_container_name(model_id),
                    ports={f"{port}/tcp": port},
                    volumes={
                        "hf_cache": {"bind": "/root/.cache/huggingface", "mode": "rw"}
                    },
                    devices=_rocm_devices(),
                    # video  → /dev/dri/card0
                    # render → /dev/kfd, /dev/dri/renderD128
                    group_add=["video", "render"],
                    cap_add=["SYS_PTRACE"],
                    security_opt=["seccomp=unconfined"],
                )

                image = self.settings.vllm_rocm_image

                logger.info(
                    "Starting vLLM container: image=%s model=%s port=%d gpu=rocm",
                    image, model_id, port,
                )
                try:
                    container = self._docker.containers.run(image, **run_kwargs)
                except docker.errors.APIError as api_err:
                    # Name conflict — another container with this model name
                    # already exists (e.g. still being removed). Retry with a
                    # short UUID suffix to get a unique name.
                    if "name" in str(api_err).lower() and "already" in str(api_err).lower():
                        fallback_name = _container_name(model_id, str(served.id)[:8])
                        logger.warning(
                            "Container name conflict for '%s', retrying as '%s'",
                            run_kwargs["name"], fallback_name,
                        )
                        run_kwargs["name"] = fallback_name
                        container = self._docker.containers.run(image, **run_kwargs)
                    else:
                        raise
                served.container_id = container.id
                # Stay in PENDING — vLLM takes time to load the model.
                # get_status() polling will transition to RUNNING once the
                # container reports status "running" and /health responds.
                served.status = ModelStatus.PENDING
                logger.info("vLLM container created: id=%s", container.short_id)
            except Exception as exc:
                logger.exception(
                    "Failed to start vLLM container for model '%s': %s",
                    model_id, exc,
                )
                served.status = ModelStatus.ERROR
                served.container_id = None
                self.db.add(served)
                await self.db.commit()
                raise VLLMError(
                    f"Could not start vLLM container for '{model_id}': {exc}"
                ) from exc
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

    async def stop(self, served_model_id: str, owner_id: uuid.UUID) -> dict:
        """Stop a served model and remove its container.

        Args:
            served_model_id: UUID of the served model record.
            owner_id: User ID that owns the served model.

        Returns:
            Updated served model data.

        Raises:
            ServedModelNotFoundError: If the record doesn't exist.
        """
        result = await self.db.execute(
            select(ServedModel).where(
                ServedModel.id == uuid.UUID(served_model_id),
                ServedModel.owner_id == owner_id,
            )
        )
        served = result.scalar_one_or_none()
        if not served:
            raise ServedModelNotFoundError(
                f"Served model '{served_model_id}' not found"
            )

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

    async def get_status(self, served_model_id: str, owner_id: uuid.UUID) -> dict:
        """Get the current status of a served model.

        Args:
            served_model_id: UUID of the served model record.
            owner_id: User ID that owns the served model.

        Returns:
            Served model data.

        Raises:
            ServedModelNotFoundError: If the record doesn't exist.
        """
        result = await self.db.execute(
            select(ServedModel).where(
                ServedModel.id == uuid.UUID(served_model_id),
                ServedModel.owner_id == owner_id,
            )
        )
        served = result.scalar_one_or_none()
        if not served:
            raise ServedModelNotFoundError(
                f"Served model '{served_model_id}' not found"
            )

        # Sync DB status against actual Docker container state for any
        # non-terminal status. Catches containers that exited or never started.
        if (
            self._docker
            and served.container_id
            and served.status in (ModelStatus.PENDING, ModelStatus.RUNNING)
        ):
            try:
                container = self._docker.containers.get(served.container_id)
                docker_status = container.status  # running | exited | dead | created | …
                if docker_status == "running":
                    if served.status != ModelStatus.RUNNING:
                        served.status = ModelStatus.RUNNING
                        await self.db.commit()
                elif docker_status in ("exited", "dead", "removing"):
                    logger.warning(
                        "vLLM container %s exited (model=%s). Logs:\n%s",
                        container.short_id,
                        served.model_id,
                        container.logs(tail=50).decode(errors="replace"),
                    )
                    served.status = ModelStatus.ERROR
                    await self.db.commit()
            except NotFound:
                logger.warning(
                    "vLLM container %s not found for model %s",
                    served.container_id, served.model_id,
                )
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

    async def list_served(self, owner_id: uuid.UUID) -> list[dict]:
        """List all served models.

        Args:
            owner_id: User ID that owns the served models.

        Returns:
            List of served model data dicts.
        """
        result = await self.db.execute(
            select(ServedModel)
            .where(ServedModel.owner_id == owner_id)
            .order_by(ServedModel.started_at.desc())
        )
        models = result.scalars().all()

        # Sync Docker state for non-terminal models so the list always
        # reflects reality without a separate status-poll per model.
        if self._docker:
            needs_commit = False
            for m in models:
                if m.status not in (ModelStatus.PENDING, ModelStatus.RUNNING):
                    continue
                if not m.container_id:
                    continue
                try:
                    container = self._docker.containers.get(m.container_id)
                    docker_status = container.status
                    if docker_status == "running" and m.status != ModelStatus.RUNNING:
                        m.status = ModelStatus.RUNNING
                        needs_commit = True
                    elif docker_status in ("exited", "dead", "removing"):
                        m.status = ModelStatus.ERROR
                        needs_commit = True
                except NotFound:
                    m.status = ModelStatus.ERROR
                    needs_commit = True
            if needs_commit:
                await self.db.commit()

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
