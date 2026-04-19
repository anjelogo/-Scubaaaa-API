import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import app.camera.broadcaster as cam
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class Command(BaseModel):
    cmd: str


@router.get("/health", tags=["vessel"])
async def health():
    return {
        "status": "ok",
        "stream_url": settings.camera_stream_url,
    }


@router.get("/stream", tags=["vessel"])
async def stream():
    """Proxy MJPEG stream — all viewers share one upstream connection."""
    q = cam.broadcaster.subscribe()
    return StreamingResponse(
        cam.broadcaster.iter_multipart(q),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/stream-info", tags=["vessel"])
async def stream_info():
    """Return camera MJPEG stream URL (proxied through this API)."""
    return {
        "stream_url": f"http://{settings.CAMERA_HOST}:{settings.APP_PORT}/stream",
        "format": "mjpeg",
        "resolution": "320x240",
    }


@router.post("/cmd", tags=["vessel"])
async def command(body: Command):
    """Stub — logs the command. Motor control wired in later."""
    logger.info("Received command: %s", body.cmd)
    return {"received": True}
