import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers.vessel import router as vessel_router
from app.camera.broadcaster import init_broadcaster
from app.core.config import settings
from app.serial.arduino import init_serial
from app.ws.handler import websocket_endpoint

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_broadcaster(settings.camera_stream_url)
    init_serial(settings.SERIAL_DEVICE, settings.SERIAL_BAUD)
    yield


app = FastAPI(title="scubaaaa-api", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vessel_router)


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket_endpoint(websocket)
