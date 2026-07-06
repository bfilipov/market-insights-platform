import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

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


app = FastAPI(
    title="Market Insights Platform - Market Signal Service",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(signal_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("market_signal.main:app", host=settings.market_signal_host, port=settings.market_signal_port)
