import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "market-signal",
        "version": "0.1.0",
        "timestamp": datetime.datetime.now(datetime.UTC)
    }
