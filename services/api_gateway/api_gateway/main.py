"""API Gateway Service — Main entry point."""
import datetime
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api_gateway.config import get_settings
from api_gateway.middleware.auth import validate_api_key
from api_gateway.models.responses import HealthResponse
from api_gateway.models.user import User
from api_gateway.routers.admin import router as admin_router
from api_gateway.routers.market import router as market_router

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("Starting API Gateway service...")

    yield

    # Shutdown logic
    logger.info("Shutting down API Gateway service...")
    from api_gateway.dependencies import get_market_data_client

    market_client = get_market_data_client()
    await market_client.close()
    get_market_data_client.cache_clear()


def create_app() -> FastAPI:
    """Application factory function."""
    app = FastAPI(
        title="Market Insights Platform - API Gateway",
        description="""
        A REST API for accessing normalized cryptocurrency market data
        with rule-based market signals.

        ## Authentication

        All endpoints require a valid API key
        passed as a Bearer token in the Authorization header.

        ```
        Authorization: Bearer your-api-key
        ```

        ## User Management

        Admin endpoints under `/api/v1/admin` require a separate admin
        API key (`API_GATEWAY_ADMIN_API_KEY`). Use these endpoints to
        create, list, deactivate, and delete API users.
        """,
        version="2.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(market_router)
    app.include_router(admin_router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
            request: Request,
            exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Invalid request parameters",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
            request: Request,
            exc: Exception,
    ) -> JSONResponse:
        logger.exception(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"},
        )

    return app


app = create_app()


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
)
async def health_check(
        current_user: User = Depends(validate_api_key),
) -> HealthResponse:
    """Health check endpoint — no authentication required."""
    return HealthResponse(
        status="healthy",
        service="api-gateway",
        version="0.1.0",
        timestamp=datetime.datetime.now(datetime.UTC)
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_gateway.main:app",
        host=settings.api_gateway_host,
        port=settings.api_gateway_port,
        reload=False,
        log_level=settings.log_level.lower(),
    )
