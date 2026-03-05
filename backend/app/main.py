"""FastAPI application factory and entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import Settings
from app.core.database import create_engine, create_session_factory
from app.api.deps import init_deps
from app.utils import exceptions, error_codes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    settings = Settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    init_deps(session_factory, settings)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="ModelServe",
        description="Self-hosted GPU model serving platform",
        version="0.1.0",
        lifespan=lifespan,
    )

    settings = Settings()

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    @app.exception_handler(exceptions.ModelNotFoundError)
    async def model_not_found_handler(request: Request, exc: exceptions.ModelNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc), "code": error_codes.MODEL_NOT_FOUND},
        )

    @app.exception_handler(exceptions.InvalidAPIKeyError)
    async def invalid_key_handler(request: Request, exc: exceptions.InvalidAPIKeyError):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc), "code": error_codes.INVALID_API_KEY},
        )

    @app.exception_handler(exceptions.KeyNotFoundError)
    async def key_not_found_handler(request: Request, exc: exceptions.KeyNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc), "code": error_codes.KEY_NOT_FOUND},
        )

    @app.exception_handler(exceptions.ServedModelNotFoundError)
    async def served_model_not_found_handler(request: Request, exc: exceptions.ServedModelNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc), "code": error_codes.SERVED_MODEL_NOT_FOUND},
        )

    @app.exception_handler(exceptions.GPUUnavailableError)
    async def gpu_unavailable_handler(request: Request, exc: exceptions.GPUUnavailableError):
        return JSONResponse(
            status_code=503,
            content={"detail": str(exc), "code": error_codes.GPU_UNAVAILABLE},
        )

    @app.exception_handler(exceptions.VLLMError)
    async def vllm_error_handler(request: Request, exc: exceptions.VLLMError):
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "code": error_codes.VLLM_ERROR},
        )

    # Routers
    from app.api.v1 import models, serve, keys, health

    app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["health"])
    app.include_router(models.router, prefix=settings.api_v1_prefix, tags=["models"])
    app.include_router(serve.router, prefix=settings.api_v1_prefix, tags=["serve"])
    app.include_router(keys.router, prefix=settings.api_v1_prefix, tags=["keys"])

    return app


app = create_app()
