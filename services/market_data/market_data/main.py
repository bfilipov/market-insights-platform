"""Market Data Service - Main entry point."""

import datetime
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from market_data.config import get_settings
from market_data.routers.market import router as market_router
from market_data.routers.health import router as health_router

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting Market Data service v2.0 (Multi-Provider)...")
    yield
    logger.info("Shutting down Market Data service...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Market Insights Platform - Market Data Service",
        description="Internal service for fetching and normalizing market data from multiple providers.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(market_router)
    app.include_router(health_router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(status_code=422, content={"detail": "Invalid request parameters", "errors": exc.errors()})

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("market_data.main:app", host=settings.market_data_host, port=settings.market_data_port)
