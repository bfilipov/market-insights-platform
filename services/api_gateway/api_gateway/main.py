"""
API Gateway Service - Main entry point.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api_gateway.config import get_settings
from api_gateway.routers.market import router as market_router

# Configure logging based on settings
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.

    Manages startup and shutdown events for proper resource cleanup.
    """
    logger.info("Starting API Gateway service...")

    yield

    # Shutdown logic
    logger.info("Shutting down API Gateway service...")

    # Clean up cached clients
    from api_gateway.dependencies import get_market_data_client

    market_client = get_market_data_client()

    await market_client.close()

    # Clear the lru_cache to release references
    get_market_data_client.cache_clear()


def create_app() -> FastAPI:
    """
    Application factory function.
    """
    app = FastAPI(
        title="Market Insights Platform - API Gateway",
        description="""
        A REST API for accessing normalized cryptocurrency market data
        with rule-based market signals.

        ## Authentication

        All endpoints (except `/health`) require a valid API key
        passed as a Bearer token in the Authorization header.

        ```
        Authorization: Bearer your-api-key
        ```
        """,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Include routers
    app.include_router(market_router)

    # Custom exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
            request: Request,
            exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle request validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": "Invalid request parameters", "errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
            request: Request,
            exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.exception(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"},
        )

    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_gateway.main:app",
        host=settings.api_gateway_host,
        port=settings.api_gateway_port,
        reload=False,
        log_level=settings.log_level.lower(),
    )
