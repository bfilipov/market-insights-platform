import datetime
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from market_signal.config import get_settings
from market_signal.routers.signal import router as signal_router

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Market Signal Service...")
    yield
    logger.info("Shutting down Market Signal Service...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Market Insights Platform - Market Signal Service",
        description="Internal service for providing Market Insights data.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(signal_router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(status_code=422, content={"detail": "Invalid request parameters", "errors": exc.errors()})

    return app


app = create_app()


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "market-signal",
        "version": "0.1.0",
        "timestamp": datetime.datetime.now(datetime.UTC)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("market_signal.main:app", host=settings.market_signal_host, port=settings.market_signal_port)
