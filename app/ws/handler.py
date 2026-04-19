import asyncio
import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from app.serial.arduino import send_command

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 1.0  # seconds


class ConnectionManager:
    def __init__(self):
        self._active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._active.append(ws)
        logger.info("WebSocket client connected. Total: %d", len(self._active))

    def disconnect(self, ws: WebSocket):
        self._active.remove(ws)
        logger.info("WebSocket client disconnected. Total: %d", len(self._active))

    async def send(self, ws: WebSocket, data: dict):
        await ws.send_text(json.dumps(data))


manager = ConnectionManager()


async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)

    heartbeat_task = asyncio.create_task(_heartbeat(ws))

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("Non-JSON message received: %s", raw)
                continue

            cmd = msg.get("cmd")
            if cmd:
                send_command(cmd)
            else:
                logger.debug("Unknown message: %s", msg)

    except WebSocketDisconnect:
        pass
    finally:
        heartbeat_task.cancel()
        manager.disconnect(ws)


async def _heartbeat(ws: WebSocket):
    try:
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            await manager.send(ws, {"status": "connected", "stream": "live"})
    except Exception:
        # Socket closed — let the outer handler clean up
        pass
